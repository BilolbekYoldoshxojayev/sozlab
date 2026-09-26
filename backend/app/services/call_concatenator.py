"""
SözLab Full-Call Audio Concatenation Service
Combines citizen turns and VoiceLab AI turns into call_{call_id}_full.wav using standard wave module.
Generates millisecond-accurate timeline beat markers for admin scrub & seek.
"""
import os
import wave
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from app.core.config import settings

logger = logging.getLogger("sozlab.call_concatenator")


def _get_ffmpeg_bin() -> str:
    """Finds ffmpeg from system PATH or imageio_ffmpeg bundled binary."""
    import shutil
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


class CallConcatenator:
    def __init__(self):
        self.cache_dir: Path = settings.AUDIO_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def transcode_to_wav(self, input_bytes: bytes, output_path: Path) -> bool:
        """
        Transcodes raw browser audio (WebM, Opus, MP4, WAV, etc.) to 24kHz 16-bit mono PCM WAV using ffmpeg.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_input = output_path.with_suffix(".tmp_raw")
        tmp_input.write_bytes(input_bytes)
        try:
            cmd = [
                _get_ffmpeg_bin(), "-y", "-i", str(tmp_input),
                "-ac", "1",
                "-ar", "24000",
                "-c:a", "pcm_s16le",
                str(output_path)
            ]
            res = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10.0
            )
            return (
                res.returncode == 0
                and output_path.exists()
                and output_path.stat().st_size > 44
            )
        except Exception as e:
            logger.error(f"[CallConcatenator] transcode_to_wav failed: {e}")
            return False
        finally:
            if tmp_input.exists():
                try:
                    tmp_input.unlink(missing_ok=True)
                except Exception:
                    pass

    def ensure_wav_24k(self, input_path: Path) -> Optional[Path]:
        """
        Ensures a given audio file is 24kHz 16-bit mono WAV.
        If it's already compatible, returns input_path.
        If it's MP3 or a WAV with a different sample rate / channel count, converts via ffmpeg.
        """
        if not input_path.exists():
            return None

        # Check if already valid 24k mono 16-bit PCM WAV
        try:
            with wave.open(str(input_path), "rb") as w:
                if w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 24000:
                    return input_path
        except Exception:
            pass

        # Convert via ffmpeg to 24k mono 16-bit PCM WAV
        converted_path = input_path.with_name(f"{input_path.stem}_24k.wav")
        if converted_path.exists() and converted_path.stat().st_size > 44:
            return converted_path

        try:
            cmd = [
                _get_ffmpeg_bin(), "-y", "-i", str(input_path),
                "-ac", "1",
                "-ar", "24000",
                "-c:a", "pcm_s16le",
                str(converted_path)
            ]
            res = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10.0
            )
            if res.returncode == 0 and converted_path.exists() and converted_path.stat().st_size > 44:
                return converted_path
        except Exception as e:
            logger.error(f"[CallConcatenator] ensure_wav_24k failed for {input_path}: {e}")

        return None

    def concatenate_call_audio(
        self,
        call_id: str,
        messages: List[Any],
        gap_ms: int = 400
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Concatenates turn WAVs into a single continuous call recording: call_{call_id}_full.wav
        Inserts gap_ms of silence (default 400ms) between turns.
        Returns: (audio_url_path, audio_markers)
        """
        turn_segments = []
        for idx, m in enumerate(messages):
            url = getattr(m, "audio_url", None)
            if not url:
                continue

            fpath = None
            if url.startswith("/api/audio/"):
                fname = os.path.basename(url)
                fpath = self.cache_dir / fname
            elif url.startswith("data:") and ";base64," in url:
                citizen_wav = self.cache_dir / f"call_{call_id}_turn_{idx}_citizen.wav"
                if citizen_wav.exists() and citizen_wav.stat().st_size > 44:
                    fpath = citizen_wav
                else:
                    try:
                        import base64
                        _, b64_data = url.split(";base64,", 1)
                        raw_bytes = base64.b64decode(b64_data)
                        if self.transcode_to_wav(raw_bytes, citizen_wav):
                            fpath = citizen_wav
                    except Exception as e:
                        logger.warning(f"Failed to transcode data URI for turn {idx}: {e}")
            elif os.path.exists(url):
                fpath = Path(url)

            if fpath and fpath.exists():
                wav_path = self.ensure_wav_24k(fpath)
                if wav_path and wav_path.exists():
                    role = getattr(m, "role", "citizen")
                    text = getattr(m, "text", "")
                    turn_segments.append((wav_path, role, text))

        if not turn_segments:
            return "", []

        output_filename = f"call_{call_id}_full.wav"
        output_filepath = self.cache_dir / output_filename
        tmp_output_filepath = self.cache_dir / f"tmp_{output_filename}"

        # 24kHz, 16-bit mono = 24000 samples/sec, 2 bytes/sample = 48000 bytes/sec
        silence_frame_count = int(24000 * (gap_ms / 1000.0))
        silence_bytes = b'\x00' * (silence_frame_count * 2)
        total_frames = 0
        markers = []

        try:
            with wave.open(str(tmp_output_filepath), "wb") as out_wav:
                out_wav.setnchannels(1)
                out_wav.setsampwidth(2)
                out_wav.setframerate(24000)

                for i, (path, role_obj, text) in enumerate(turn_segments):
                    if i > 0 and gap_ms > 0:
                        out_wav.writeframes(silence_bytes)
                        total_frames += silence_frame_count

                    start_sec = round(total_frames / 24000.0, 2)
                    with wave.open(str(path), "rb") as in_wav:
                        n_frames = in_wav.getnframes()
                        frames = in_wav.readframes(n_frames)
                        out_wav.writeframes(frames)
                        total_frames += n_frames
                    end_sec = round(total_frames / 24000.0, 2)

                    role_str = getattr(role_obj, "value", str(role_obj))
                    markers.append({
                        "turn_index": i,
                        "role": role_str,
                        "start_time": start_sec,
                        "end_time": end_sec,
                        "duration": round(end_sec - start_sec, 2),
                        "text": (text or "")[:140]
                    })

            # Replace tmp with final output atomically
            if tmp_output_filepath.exists():
                tmp_output_filepath.replace(output_filepath)

            return f"/api/audio/{output_filename}", markers
        except Exception as e:
            logger.error(f"[CallConcatenator] Concatenation failed: {e}")
            if tmp_output_filepath.exists():
                try:
                    tmp_output_filepath.unlink(missing_ok=True)
                except Exception:
                    pass
            return "", []


call_concatenator = CallConcatenator()

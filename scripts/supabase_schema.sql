-- ==============================================================================
-- SözLab (Oliy ta'lim, fan va innovatsiyalar vazirligi ovozli call-markazi)
-- Supabase PostgreSQL Schema Migration
-- ==============================================================================

-- 1. Create calls table
CREATE TABLE IF NOT EXISTS public.calls (
    id TEXT PRIMARY KEY,
    citizen_name TEXT NOT NULL,
    citizen_phone TEXT NOT NULL,
    operator_name TEXT,
    operator_id TEXT,
    status TEXT NOT NULL DEFAULT 'completed',
    primary_topic TEXT DEFAULT 'BOSHQA',
    sentiment TEXT DEFAULT 'NEUTRAL',
    duration_seconds INTEGER DEFAULT 0,
    ai_summary TEXT,
    resolved_by_ai BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- 2. Create call_transcripts table (individual dialog turns and live speech chunks)
CREATE TABLE IF NOT EXISTS public.call_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id TEXT NOT NULL REFERENCES public.calls(id) ON DELETE CASCADE,
    speaker_role TEXT NOT NULL, -- 'CITIZEN', 'OPERATOR', 'AI', 'SYSTEM'
    speaker_name TEXT,
    text TEXT NOT NULL,
    timestamp_offset_seconds NUMERIC(6, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- 3. Create performant indexes
CREATE INDEX IF NOT EXISTS idx_calls_status ON public.calls(status);
CREATE INDEX IF NOT EXISTS idx_calls_started_at ON public.calls(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_calls_operator_id ON public.calls(operator_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_call_id ON public.call_transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_created_at ON public.call_transcripts(created_at ASC);

-- 4. Enable Row Level Security (RLS) & Public Policies for API access
ALTER TABLE public.calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.call_transcripts ENABLE ROW LEVEL SECURITY;

-- Allow read & insert access for authenticated / service role & anon for call center logging
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'calls' AND policyname = 'Enable all operations for calls'
    ) THEN
        CREATE POLICY "Enable all operations for calls" ON public.calls
            FOR ALL USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'call_transcripts' AND policyname = 'Enable all operations for call_transcripts'
    ) THEN
        CREATE POLICY "Enable all operations for call_transcripts" ON public.call_transcripts
            FOR ALL USING (true) WITH CHECK (true);
    END IF;
END $$;

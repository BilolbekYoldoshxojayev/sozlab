'use client';

import React from 'react';

interface HighlightRule {
  type: 'citation' | 'right' | 'prohibition' | 'deadline';
  pattern: RegExp;
  className: string;
  label: string;
}

const HIGHLIGHT_RULES: HighlightRule[] = [
  // 1. Legal citations, Constitution articles, laws, decrees, Lex.uz links
  {
    type: 'citation',
    pattern: /\b(?:Konstitutsiya(?:ning|da|ga)?(?:\s+(?:50|51|52|77|\d+)-(?:modda(?:si|da|ga)?))?|\d+-(?:modda(?:si|da|ga)?)|O'?RQ-\d+|PF-\d+|VMQ-\d+|PQ-\d+|MJtK(?:\s+\d+-modda(?:si)?)?|(?:https?:\/\/)?lex\.uz[^\s,)]*|['"]?Pedagogning maqomi to'g'risida['"]?gi\s+Qonun(?:ga|da|i)?|['"]?Ta'lim to'g'risida['"]?gi\s+Qonun(?:ga|da|i)?|Prezident(?:ning)?\s+(?:Farmon(?:i|iga|da)?|Qaror(?:i|iga|da)?)|Vazirlar Mahkamasi(?:ning)?\s+Qaror(?:i|iga|da)?)/gi,
    className: 'bg-blue-900/35 text-blue-200 border-blue-500/50 hover:bg-blue-900/55 font-medium',
    label: 'Qonun & Nizom (Huquqiy asos)',
  },
  // 2. Rights granted, free benefits, 100% grants, budget coverage
  {
    type: 'right',
    pattern: /\b(?:100\s*(?:foiz|%)(?:\s+(?:bepul|davlat\s+budjetidan|qoplab\s+beriladi|qoplanadi))?|50\s*(?:foiz|%)\s+kompensatsiya|davlat\s+grant(?:i|lari|iga)?|bepul(?:\s+(?:ta'minlanadi|ta'lim|beriladi))?|davlat\s+budjetidan|to'liq\s+qoplanadi|qaytarish\s+shartisiz|ijtimoiy\s+himoya|imtiyoz(?:li|lar)?|stipendiya(?:lar)?|moddiy\s+yordam|ijara\s+kompensatsiyasi)/gi,
    className: 'bg-blue-800/25 text-white border-blue-400/40 hover:bg-blue-800/40 font-medium',
    label: 'Huquq & Imtiyoz (Davlat kafolati)',
  },
  // 3. Prohibitions, illegal actions, fines, zero-tolerance rules
  {
    type: 'prohibition',
    pattern: /\b(?:majburiy\s+mehnat(?:ga)?|pul\s+yig'ish(?:lar)?|yig'di-yig'di|qat'iyan\s+taqiqlanadi|qat'iyan\s+man\s+etiladi|taqiqlanadi|man\s+etiladi|noqonuniy|jarima(?:ga)?|javobgarlik(?:ka)?|BHMning\s+\d+\s+dan\s+\d+\s+baravarigacha|obuna\s+bo'lishga\s+majburlash|boshqa\s+ishlarga\s+jalb\s+qilish)/gi,
    className: 'bg-slate-800/80 text-blue-100 border-slate-600/70 hover:bg-slate-700/80 font-medium',
    label: 'Taqiqlangan & Jarima (Qonunbuzarlik)',
  },
  // 4. Critical deadlines, dates, GPA thresholds, action portals
  {
    type: 'deadline',
    pattern: /\b(?:my\.gov\.uz|hemis(?:-ochiq-talim)?|my\.maktab\.uz|bilim\.uz|dtm\.uz|uzbmb\.uz|GPA(?:\s+ball[i]?)?|\d{1,2}-(?:avgust|iyun|iyul|sentabr|oktabr|noyabr|dekabr|yanvar|fevral|mart|aprel|may)(?:ga qadar|gacha)?|\d+\s+(?:kunlik|kun|oy)\s+muddat(?:da)?|2024[–-]2026-yillar(?:da)?|mikrohudud|onlayn\s+ariza)/gi,
    className: 'bg-blue-950/70 text-blue-300 border-blue-700/60 hover:bg-blue-900/70 font-medium',
    label: 'Muddat & Portal (Muddati yoki platforma)',
  },
];

interface HighlightMatch {
  start: number;
  end: number;
  text: string;
  className: string;
  label: string;
}

function getMatches(text: string): HighlightMatch[] {
  const matches: HighlightMatch[] = [];

  for (const rule of HIGHLIGHT_RULES) {
    const regex = new RegExp(rule.pattern.source, 'gi');
    let m: RegExpExecArray | null;
    while ((m = regex.exec(text)) !== null) {
      matches.push({
        start: m.index,
        end: m.index + m[0].length,
        text: m[0],
        className: rule.className,
        label: rule.label,
      });
    }
  }

  // Sort by start index ascending, longer matches first on ties
  matches.sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));

  // Filter overlapping matches
  const nonOverlapping: HighlightMatch[] = [];
  let lastEnd = 0;
  for (const match of matches) {
    if (match.start >= lastEnd) {
      nonOverlapping.push(match);
      lastEnd = match.end;
    }
  }

  return nonOverlapping;
}

export function HighlightLegend() {
  return (
    <div
      className="flex flex-wrap items-center gap-2 p-2.5 rounded-xl text-[10px] transition-colors"
      style={{
        backgroundColor: 'var(--bg-subtle)',
        border: '1px solid var(--border-subtle)',
        color: 'var(--text-muted)',
      }}
    >
      <span className="font-bold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
        Tahlil belgisi:
      </span>
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold border bg-blue-900/35 text-blue-200 border-blue-500/50">
        ⚖️ Qonun &amp; Nizomlar
      </span>
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold border bg-blue-800/25 text-white border-blue-400/40">
        ✨ Huquq &amp; Grantlar
      </span>
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold border bg-slate-800/80 text-blue-100 border-slate-600/70">
        🚫 Taqiqlangan &amp; Jarimalar
      </span>
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold border bg-blue-950/70 text-blue-300 border-blue-700/60">
        📅 Muddat &amp; Portallar
      </span>
    </div>
  );
}

export default function TranscriptHighlightedText({ text }: { text: string }) {
  if (!text) return null;

  const matches = getMatches(text);
  if (matches.length === 0) {
    return <span className="text-inherit leading-relaxed">{text}</span>;
  }

  const elements: React.ReactNode[] = [];
  let currentIndex = 0;

  matches.forEach((match, idx) => {
    // Add text preceding match
    if (match.start > currentIndex) {
      elements.push(
        <span key={`text-${idx}-${currentIndex}`} className="text-inherit">
          {text.slice(currentIndex, match.start)}
        </span>
      );
    }

    // Add highlighted match
    elements.push(
      <mark
        key={`match-${idx}-${match.start}`}
        title={match.label}
        className={`inline-block px-1.5 py-0.5 mx-0.5 rounded-md font-semibold text-xs border transition-colors ${match.className}`}
      >
        {match.text}
      </mark>
    );

    currentIndex = match.end;
  });

  // Add remaining text
  if (currentIndex < text.length) {
    elements.push(
      <span key={`tail-${currentIndex}`} className="text-inherit">
        {text.slice(currentIndex)}
      </span>
    );
  }

  return <span className="text-inherit leading-relaxed">{elements}</span>;
}

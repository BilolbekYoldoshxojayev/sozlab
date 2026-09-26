-- ==============================================================================
-- SözLab (1006 / 1007 Ta'lim Ishonch Telefonlari)
-- Supabase PostgreSQL Complete Production Schema & Migration Script
-- Ingests:
-- 1. Calls with Serverless Audio Playback (data URIs & remote URLs) and Multi-LLM provider metadata
-- 2. Call Transcripts with Review Highlighting categories and legal citations
-- 3. Top-50 Education FAQs (Chapters 1-8)
-- 4. Education Legislation Encyclopedia (Sections 1-6, 62 Articles and Decrees)
-- 5. Complete Indexing, Row Level Security (RLS) policies, and Admin Wipe Procedure
-- ==============================================================================

-- 1. Calls Table
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
    audio_url TEXT,
    recording_data_uri TEXT,
    llm_provider_used TEXT DEFAULT 'groq',
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- 2. Call Transcripts Table
CREATE TABLE IF NOT EXISTS public.call_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id TEXT NOT NULL REFERENCES public.calls(id) ON DELETE CASCADE,
    speaker_role TEXT NOT NULL, -- 'CITIZEN', 'OPERATOR', 'AI', 'SYSTEM'
    speaker_name TEXT,
    text TEXT NOT NULL,
    timestamp_offset_seconds NUMERIC(6, 2) DEFAULT 0,
    highlight_category TEXT DEFAULT 'none', -- 'legal_citation', 'benefit_grant', 'warning_prohibition', 'deadline_threshold'
    citation_ref TEXT, -- e.g. 'CONST-50', 'VMQ-447', 'ORQ-901'
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- 3. Education FAQs Table (All 50 questions across 8 chapters from Top_50_Talim_Vazirligi_FAQ.pdf)
CREATE TABLE IF NOT EXISTS public.education_faqs (
    id INTEGER PRIMARY KEY,
    chapter INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    question TEXT NOT NULL,
    short_answer TEXT NOT NULL,
    constitutional_basis TEXT,
    law_basis TEXT,
    decree_basis TEXT,
    legal_basis TEXT NOT NULL,
    full_answer TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- 4. Education Legal Encyclopedia Table (All 62 articles & decrees across 6 sections from Ozbekiston_Talim_Qonunchiligi_Mukammal_Entsiklopediya.pdf)
CREATE TABLE IF NOT EXISTS public.education_encyclopedia (
    code TEXT PRIMARY KEY,
    section_id INTEGER NOT NULL,
    section_name TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    doc_number TEXT,
    doc_date TEXT,
    lex_url TEXT,
    summary TEXT NOT NULL,
    full_text TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    related_faq_ids INTEGER[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- 5. Performant Indexes
CREATE INDEX IF NOT EXISTS idx_calls_status ON public.calls(status);
CREATE INDEX IF NOT EXISTS idx_calls_started_at ON public.calls(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_calls_operator_id ON public.calls(operator_id);
CREATE INDEX IF NOT EXISTS idx_calls_llm_provider ON public.calls(llm_provider_used);

CREATE INDEX IF NOT EXISTS idx_transcripts_call_id ON public.call_transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_created_at ON public.call_transcripts(created_at ASC);
CREATE INDEX IF NOT EXISTS idx_transcripts_highlight ON public.call_transcripts(highlight_category);

CREATE INDEX IF NOT EXISTS idx_faqs_chapter ON public.education_faqs(chapter);
CREATE INDEX IF NOT EXISTS idx_encyclopedia_category ON public.education_encyclopedia(category);
CREATE INDEX IF NOT EXISTS idx_encyclopedia_section ON public.education_encyclopedia(section_id);

-- 6. Row Level Security (RLS) & Policies
ALTER TABLE public.calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.call_transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.education_faqs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.education_encyclopedia ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    -- Calls policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'calls' AND policyname = 'Enable all operations for calls'
    ) THEN
        CREATE POLICY "Enable all operations for calls" ON public.calls
            FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- Call transcripts policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'call_transcripts' AND policyname = 'Enable all operations for call_transcripts'
    ) THEN
        CREATE POLICY "Enable all operations for call_transcripts" ON public.call_transcripts
            FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- Education FAQs policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'education_faqs' AND policyname = 'Enable all operations for education_faqs'
    ) THEN
        CREATE POLICY "Enable all operations for education_faqs" ON public.education_faqs
            FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- Education Encyclopedia policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'education_encyclopedia' AND policyname = 'Enable all operations for education_encyclopedia'
    ) THEN
        CREATE POLICY "Enable all operations for education_encyclopedia" ON public.education_encyclopedia
            FOR ALL USING (true) WITH CHECK (true);
    END IF;
END $$;

-- 7. Admin Database Purge Stored Procedure
CREATE OR REPLACE FUNCTION public.purge_all_call_records()
RETURNS void AS $$
BEGIN
    TRUNCATE TABLE public.call_transcripts CASCADE;
    TRUNCATE TABLE public.calls CASCADE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execution to public / service role
GRANT EXECUTE ON FUNCTION public.purge_all_call_records() TO anon, authenticated, service_role;

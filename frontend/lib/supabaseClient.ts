/**
 * Supabase Client Configuration for SözLab Frontend
 */

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://lrltaamzlvjezfkwzwxc.supabase.co';
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_vsJPx9dRsBNfzaeYbR9UvQ_RTH3Ig4H';

export interface ArchivedCall {
  id: string;
  citizen_name: string;
  citizen_phone: string;
  operator_name?: string;
  operator_id?: string;
  status: string;
  primary_topic: string;
  sentiment: string;
  duration_seconds: number;
  ai_summary?: string;
  started_at: string;
  ended_at?: string;
  created_at: string;
}

export interface CallTranscriptItem {
  id: string;
  call_id: string;
  speaker_role: string;
  speaker_name?: string;
  text: string;
  timestamp_offset_seconds: number;
  created_at: string;
}

/**
 * Fetch calls directly from Supabase REST API
 */
export async function fetchSupabaseCalls(limit: number = 30): Promise<ArchivedCall[]> {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/calls?order=started_at.desc&limit=${limit}`, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      },
      cache: 'no-store',
    });
    if (!res.ok) {
      return [];
    }
    return await res.json();
  } catch (e) {
    console.warn('[Supabase Client Error]:', e);
    return [];
  }
}

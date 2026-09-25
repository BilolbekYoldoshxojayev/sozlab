export type CallStatus =
  | 'initiated'
  | 'ai_handling'
  | 'waiting_operator'
  | 'operator_handling'
  | 'completed'
  | 'transferred';

export type SentimentType = 'Ijobiy' | 'Neytral' | 'Salbiy';

export type TopicCategory =
  | 'Qabul va Hujjatlar'
  | 'Davlat Grantlari'
  | 'Kontrakt va Super-kontrakt'
  | 'Talabalar Turar Joyi (TTJ)'
  | 'Diplom Tan Olish (Nostrifikatsiya)'
  | 'Stipendiyalar va Kredit'
  | 'O\'qishni Ko\'chirish (Perevod)'
  | 'Umumiy Murojaat';

export type SpeakerRole = 'citizen' | 'ai' | 'operator' | 'system';

export interface Message {
  id: string;
  role: SpeakerRole;
  text: string;
  timestamp: string;
  audio_url?: string;
  sentiment?: SentimentType;
  detected_topic?: TopicCategory;
}

export interface CallRecord {
  id: string;
  citizen_name: string;
  citizen_phone: string;
  status: CallStatus;
  started_at: string;
  ended_at?: string;
  duration_seconds: number;
  assigned_operator?: string;
  queue_position?: number;
  transfer_reason?: string;
  messages: Message[];
  primary_topic: TopicCategory;
  overall_sentiment: SentimentType;
  resolution_summary?: string;
  resolved_by_ai: boolean;
  satisfaction_score?: number;
}

export interface OperatorRecord {
  id: string;
  name: string;
  role: string;
  status: 'online' | 'busy' | 'offline';
  active_calls_count: number;
  current_call_id?: string;
  handled_today: number;
}

export interface AudioTurnResponse {
  call_id: string;
  user_text: string;
  bot_text: string;
  transcribed_text?: string;
  ai_text?: string;
  confidence?: number;
  audio_url?: string;
  intent?: string;
  sentiment?: SentimentType;
  status: CallStatus;
  operator_name?: string;
  queue_position?: number;
}

export interface GhostMessageEvent {
  type: 'ghost_message' | 'ghost_turn';
  call_id: string;
  role: SpeakerRole | 'citizen' | 'bot' | 'operator';
  speaker?: string;
  text: string;
  audio_url?: string;
  timestamp?: string;
}

export interface NextCallCountdownEvent {
  type: 'next_call_countdown';
  duration: number;
  next_call_id: string;
  caller_name?: string;
  topic?: string;
}

export interface KnowledgeItem {
  id: string;
  topic: TopicCategory;
  title: string;
  summary: string;
  official_regulation: string;
  faq_questions: string[];
  action_steps: string[];
  links: string[];
}

export interface AnalyticsSummary {
  total_calls_today: number;
  ai_resolved_percentage: number;
  avg_call_duration_seconds: number;
  active_calls_count: number;
  waiting_operator_count: number;
  satisfaction_rate: number;
  topic_distribution: Record<string, number>;
  sentiment_distribution: Record<string, number>;
  hourly_call_volume: Array<{
    time: string;
    total: number;
    ai_handled: number;
    operator_handled: number;
  }>;
}

export interface DialogTurnResponse {
  call_id: string;
  ai_text: string;
  audio_url?: string;
  sentiment: SentimentType;
  intent: string;
  topic: TopicCategory;
  requires_operator: boolean;
  knowledge_references: string[];
  smart_suggestions: string[];
}


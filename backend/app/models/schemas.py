from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

def utc_now():
    return datetime.now(timezone.utc)

class CallStatus(str, Enum):
    INITIATED = "initiated"
    AI_HANDLING = "ai_handling"
    WAITING_OPERATOR = "waiting_operator"
    OPERATOR_HANDLING = "operator_handling"
    COMPLETED = "completed"
    TRANSFERRED = "transferred"

class OperatorStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class OperatorRecord(BaseModel):
    id: str
    name: str
    status: OperatorStatus = OperatorStatus.AVAILABLE
    current_call_id: Optional[str] = None
    calls_handled: int = 0
    joined_at: datetime = Field(default_factory=utc_now)

class SentimentType(str, Enum):
    POSITIVE = "Ijobiy"
    NEUTRAL = "Neytral"
    NEGATIVE = "Salbiy"

class TopicCategory(str, Enum):
    QABUL = "Qabul va Hujjatlar"
    GRANT = "Davlat Grantlari"
    KONTRAKT = "Kontrakt va Super-kontrakt"
    TTJ = "Talabalar Turar Joyi (TTJ)"
    NOSTRIFIKATSIYA = "Diplom Tan Olish (Nostrifikatsiya)"
    STIPENDIYA = "Stipendiyalar va Kredit"
    PEREVOD = "O'qishni Ko'chirish (Perevod)"
    BOSHQA = "Umumiy Murojaat"

class SpeakerRole(str, Enum):
    CITIZEN = "citizen"
    AI = "ai"
    OPERATOR = "operator"
    SYSTEM = "system"

class MessageSchema(BaseModel):
    id: str
    role: SpeakerRole
    text: str
    timestamp: datetime = Field(default_factory=utc_now)
    audio_url: Optional[str] = None
    sentiment: Optional[SentimentType] = None
    detected_topic: Optional[TopicCategory] = None

class CallRecord(BaseModel):
    id: str
    citizen_name: str = "Fuqaro"
    citizen_phone: str = "+998 90 123-45-67"
    status: CallStatus = CallStatus.INITIATED
    started_at: datetime = Field(default_factory=utc_now)
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    assigned_operator: Optional[str] = None
    messages: List[MessageSchema] = []
    primary_topic: TopicCategory = TopicCategory.BOSHQA
    overall_sentiment: SentimentType = SentimentType.NEUTRAL
    resolution_summary: Optional[str] = None
    resolved_by_ai: bool = True
    satisfaction_score: Optional[int] = Field(default=5, ge=1, le=5)

class KnowledgeItem(BaseModel):
    id: str
    topic: TopicCategory
    title: str
    summary: str
    official_regulation: str
    faq_questions: List[str]
    action_steps: List[str]
    links: List[str] = []

class AudioSynthesisRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"

class AudioSynthesisResponse(BaseModel):
    audio_url: str
    duration_estimate_sec: float
    cached: bool
    voice: str

class DialogTurnRequest(BaseModel):
    call_id: str
    user_text: str = Field(..., max_length=2000, description="Foydalanuvchi murojaati")
    voice_enabled: bool = True
    voice_name: Optional[str] = "uz-UZ-MadinaNeural"

class DialogTurnResponse(BaseModel):
    call_id: str
    ai_text: str
    status: Optional[str] = None
    audio_url: Optional[str] = None
    sentiment: SentimentType
    intent: str
    topic: TopicCategory
    requires_operator: bool
    knowledge_references: List[str] = []
    smart_suggestions: List[str] = []
    queue_position: Optional[int] = None
    assigned_operator: Optional[str] = None

class AudioTurnResponse(BaseModel):
    call_id: str
    transcribed_text: str
    ai_text: str
    user_text: str = ""
    bot_text: str = ""
    status: str = "ai_handling"
    operator_name: Optional[str] = None
    audio_url: Optional[str] = None
    sentiment: SentimentType
    intent: str
    topic: TopicCategory
    requires_operator: bool
    queue_position: Optional[int] = None
    assigned_operator: Optional[str] = None

    @model_validator(mode="after")
    def sync_aliases(self):
        if not self.user_text and self.transcribed_text:
            self.user_text = self.transcribed_text
        if not self.bot_text and self.ai_text:
            self.bot_text = self.ai_text
        if self.operator_name is None and self.assigned_operator:
            self.operator_name = self.assigned_operator
        return self

class AnalyticsSummary(BaseModel):
    total_calls_today: int
    ai_resolved_percentage: float
    avg_call_duration_seconds: int
    active_calls_count: int
    waiting_operator_count: int
    satisfaction_rate: float
    topic_distribution: Dict[str, int]
    sentiment_distribution: Dict[str, int]
    hourly_call_volume: List[Dict[str, Any]]

import { AnalyticsSummary, AudioTurnResponse, CallRecord, DialogTurnResponse, KnowledgeItem, OperatorRecord } from './types';

export function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    return `http://${host}:8000`;
  }
  return 'http://localhost:8000';
}

export function getWsBase(): string {
  if (process.env.NEXT_PUBLIC_WS_URL) return process.env.NEXT_PUBLIC_WS_URL;
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${host}:8000`;
  }
  return 'ws://localhost:8000';
}

export async function fetchCalls(status?: string, search?: string): Promise<CallRecord[]> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (search) params.append('search', search);

  const res = await fetch(`${getApiBase()}/api/calls?${params.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Qo\'ng\'iroqlarni yuklab bo\'lmadi');
  return res.json();
}

export async function fetchCall(callId: string): Promise<CallRecord> {
  const res = await fetch(`${getApiBase()}/api/calls/${callId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Qo\'ng\'iroq tafsilotlari topilmadi');
  return res.json();
}

export async function startNewCall(name: string, phone: string): Promise<CallRecord> {
  const res = await fetch(`${getApiBase()}/api/calls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, phone }),
  });
  if (!res.ok) throw new Error('Qo\'ng\'iroq boshlab bo\'lmadi');
  return res.json();
}

export async function sendDialogTurn(
  callId: string,
  userText: string,
  voiceEnabled = true,
  voiceName = 'uz-UZ-MadinaNeural'
): Promise<DialogTurnResponse> {
  const res = await fetch(`${getApiBase()}/api/calls/${callId}/turn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      call_id: callId,
      user_text: userText,
      voice_enabled: voiceEnabled,
      voice_name: voiceName,
    }),
  });
  if (!res.ok) throw new Error('Xabarni uzatib bo\'lmadi');
  return res.json();
}

export async function sendAudioTurn(
  callId: string,
  audioBlob: Blob,
  voiceEnabled = true,
  voiceName = 'uz-UZ-MadinaNeural'
): Promise<AudioTurnResponse> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'speech.webm');
  formData.append('file', audioBlob, 'speech.webm');
  formData.append('voice_enabled', voiceEnabled ? 'true' : 'false');
  formData.append('voice_name', voiceName);
  formData.append('voice', voiceName);

  const res = await fetch(`${getApiBase()}/api/calls/${callId}/audio-turn`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Ovozli xabarni qayta ishlab bo\'lmadi');
  return res.json();
}

export async function fetchOperators(): Promise<OperatorRecord[]> {
  const res = await fetch(`${getApiBase()}/api/calls/operators`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Operatorlarni yuklab bo\'lmadi');
  return res.json();
}

export async function transferToOperator(callId: string, reason?: string): Promise<CallRecord> {
  const res = await fetch(`${getApiBase()}/api/calls/${callId}/transfer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason: reason || 'Fuqaro operatorni so\'radi' }),
  });
  if (!res.ok) throw new Error('Operatorga yo\'naltirib bo\'lmadi');
  return res.json();
}

export async function operatorTakeover(callId: string, operatorName: string): Promise<CallRecord> {
  const res = await fetch(`${getApiBase()}/api/calls/${callId}/takeover`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operator_name: operatorName }),
  });
  if (!res.ok) throw new Error('Qo\'ng\'iroqni qabul qilib bo\'lmadi');
  return res.json();
}

export async function operatorSendMessage(
  callId: string,
  text: string,
  operatorName = 'Operator'
): Promise<CallRecord> {
  const res = await fetch(`${getApiBase()}/api/calls/${callId}/operator-message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, operator_name: operatorName }),
  });
  if (!res.ok) throw new Error('Operator xabari yuborilmadi');
  return res.json();
}

export async function completeCall(callId: string, summary?: string): Promise<CallRecord> {
  const res = await fetch(`${getApiBase()}/api/calls/${callId}/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ summary }),
  });
  if (!res.ok) throw new Error('Qo\'ng\'iroq yakunlanmadi');
  return res.json();
}

export async function fetchAnalytics(): Promise<AnalyticsSummary> {
  const res = await fetch(`${getApiBase()}/api/analytics`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Analitika yuklanmadi');
  return res.json();
}

export async function fetchKnowledge(): Promise<KnowledgeItem[]> {
  const res = await fetch(`${getApiBase()}/api/knowledge`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Bilimlar bazasi yuklanmadi');
  return res.json();
}

export function getCallWebSocketUrl(callId: string): string {
  return `${getWsBase()}/ws/call/${callId}`;
}

export function getOperatorWebSocketUrl(): string {
  return `${getWsBase()}/ws/operator`;
}

export function getAdminWebSocketUrl(): string {
  return `${getWsBase()}/ws/admin`;
}

export function getAudioFullUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return `${getApiBase()}${path}`;
}


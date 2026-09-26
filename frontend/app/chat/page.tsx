'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Scale, Zap, RotateCcw, Copy, Check } from 'lucide-react';
import { sendChatMessage } from '@/lib/api';
import { ChatMessageResponse } from '@/lib/types';
import TranscriptHighlightedText from '@/components/TranscriptHighlightedText';

interface ChatTurn {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  provider?: string;
  latency_ms?: number;
  citations?: Array<{
    title?: string;
    legal_basis?: string;
    chapter?: string;
  }>;
  timestamp: Date;
}

const QUICK_PROMPTS = [
  "Magistratura xotin-qizlar uchun kontrakt bepulmi?",
  "Bog'cha navbatini qanday tekshiraman?",
  "Bolam 1-sinfga necha yoshdan qabul qilinadi?",
  "Maktabda darsliklar bepulmi yoki ijara bormi?",
  "O'qishni ko'chirish (perevod) tartibi qanday?",
  "Pedagoglarni majburiy mehnatga jalb qilish taqiqlanganmi?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatTurn[]>([
    {
      id: 'welcome',
      role: 'assistant',
      text: "Assalomu alaykum, eshitaman. Ta'lim qonunchiligi bo'yicha qanday savolingiz bor?",
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputText).trim();
    if (!query || isLoading) return;

    const userMsg: ChatTurn = {
      id: `u-${Date.now()}`,
      role: 'user',
      text: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.text,
      }));

      const res: ChatMessageResponse = await sendChatMessage(query, historyPayload);

      const aiMsg: ChatTurn = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        text: res.response,
        provider: res.provider,
        latency_ms: res.latency_ms,
        citations: res.citations,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      const errorMsg: ChatTurn = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        text: "Kechirasiz, tizimda vaqtincha uzilish yuz berdi. Iltimos, qayta urinib ko'ring.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleReset = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        text: "Assalomu alaykum, eshitaman. Ta'lim qonunchiligi bo'yicha qanday savolingiz bor?",
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pt-3 pb-24 sm:pb-28 flex flex-col h-full overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-2xl bg-[#035B60]/10 text-[#035B60] flex items-center justify-center font-bold shadow-xs">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-extrabold text-slate-900">
              SözLab Rasmiy AI Chat
            </h1>
            <p className="text-[11px] text-slate-500 font-medium">
              Ta&apos;lim qonunchiligi (50 FAQ &amp; Ensiklopediya) bo&apos;yicha tezkor matnli maslahatchi
            </p>
          </div>
        </div>

        <button
          onClick={handleReset}
          className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-bold transition flex items-center gap-1.5"
          title="Suhbatni tozalash"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Tozalash</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 sm:pr-2 scrollbar-thin">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              className={`flex gap-3 text-sm ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-700 shrink-0 flex items-center justify-center mt-1 shadow-xs">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[88%] sm:max-w-[80%] rounded-2xl p-4 transition-all shadow-xs ${
                  isUser
                    ? 'bg-emerald-600 text-white rounded-tr-none font-medium'
                    : 'bg-white border border-slate-200 text-slate-900 rounded-tl-none'
                }`}
              >
                <div className="leading-relaxed whitespace-pre-wrap">
                  {isUser ? (
                    <span>{m.text}</span>
                  ) : (
                    <TranscriptHighlightedText text={m.text} />
                  )}
                </div>

                {!isUser && (m.provider || (m.citations && m.citations.length > 0)) && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500">
                    <div className="flex items-center gap-2 flex-wrap">
                      {m.provider && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-mono font-bold text-[10px]">
                          <Zap className="w-3 h-3 text-blue-600" />
                          <span>{m.provider}</span>
                        </span>
                      )}

                      {m.citations?.map((cit, idx) => (
                        <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[10px] font-semibold">
                          <Scale className="w-3 h-3 text-slate-500" />
                          <span className="truncate max-w-[160px]">{cit.legal_basis || cit.title}</span>
                        </span>
                      ))}
                    </div>

                    <button
                      onClick={() => handleCopy(m.id, m.text)}
                      className="p-1 rounded hover:bg-slate-100 transition"
                      title="Nusxa olish"
                    >
                      {copiedId === m.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="w-3.5 h-3.5 text-slate-400" />
                      )}
                    </button>
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 shrink-0 flex items-center justify-center mt-1 shadow-xs">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-3 text-sm justify-start">
            <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-700 shrink-0 flex items-center justify-center mt-1">
              <Bot className="w-4 h-4 animate-bounce" />
            </div>
            <div className="rounded-2xl rounded-tl-none p-4 bg-white border border-slate-200 text-slate-500 text-xs font-medium flex items-center gap-2 shadow-xs">
              <span className="w-2 h-2 rounded-full animate-ping bg-blue-600" />
              <span>Qonunchilik bazasidan javob tayyorlanmoqda...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Chips */}
      {messages.length <= 2 && (
        <div className="py-2 flex items-center gap-2 overflow-x-auto scrollbar-none shrink-0">
          {QUICK_PROMPTS.slice(0, 4).map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-semibold bg-white border border-slate-200 hover:border-emerald-500 text-slate-700 transition active:scale-95 shadow-2xs shrink-0"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Bar — with clearance for floating navbar */}
      <div className="pt-2 border-t border-slate-200 shrink-0">
        <div className="flex items-center gap-2 rounded-2xl bg-white border border-slate-200 p-2 shadow-sm focus-within:border-[#035B60] transition-all">
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ta'lim qonunchiligi bo'yicha savolingizni yozing..."
            className="flex-1 bg-transparent px-3 py-2 text-sm font-medium text-slate-900 placeholder-slate-400 focus:outline-none"
            disabled={isLoading}
          />

          <button
            onClick={() => handleSend()}
            disabled={!inputText.trim() || isLoading}
            className="p-3 rounded-xl bg-[#035B60] hover:bg-[#02373A] text-white font-bold transition active:scale-95 disabled:opacity-40 flex items-center justify-center shadow-md shadow-[#035B60]/20"
            title="Yuborish"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

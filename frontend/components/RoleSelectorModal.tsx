'use client';

import { useState } from 'react';
import { useRole, UserRole } from '@/lib/useRole';
import { User, Headphones, Shield, Check, X, Phone, Sparkles } from 'lucide-react';

interface RoleSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const operatorsList = [
  { id: 'op-1', name: 'Nargiza Qodirova', spec: 'Qabul va Kontrakt mutaxassisi' },
  { id: 'op-2', name: 'Bekzod Aliyev', spec: 'Nostrifikatsiya va Grantlar' },
  { id: 'op-3', name: 'Dilnoza Karimova', spec: 'TTJ va Ijtimoiy masalalar' },
];

export default function RoleSelectorModal({ isOpen, onClose }: RoleSelectorModalProps) {
  const { session, setRole, setCitizenProfile } = useRole();
  const [selectedRole, setSelectedRole] = useState<UserRole>(session.role);
  const [selectedOpId, setSelectedOpId] = useState<string>(session.operatorId || 'op-1');
  const [name, setName] = useState<string>(session.citizenName || 'Fuqaro');
  const [phone, setPhone] = useState<string>(session.citizenPhone || '+998 (90) 123-45-67');

  if (!isOpen) return null;

  const handleSave = () => {
    if (selectedRole === 'operator') {
      const op = operatorsList.find((o) => o.id === selectedOpId) || operatorsList[0];
      setRole('operator', op.id, op.name);
    } else if (selectedRole === 'citizen') {
      setCitizenProfile(name, phone);
      setRole('citizen');
    } else {
      setRole('admin');
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden text-slate-100">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white">Foydalanuvchi Rolini Tanlang</h3>
              <p className="text-xs text-slate-400">Xakatonda 3 ta alohida rolni sinab ko'rish imkoniyati</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Roles List */}
        <div className="p-5 space-y-3">
          {/* Citizen Option */}
          <div
            onClick={() => setSelectedRole('citizen')}
            className={`p-4 rounded-xl border cursor-pointer transition flex items-start space-x-3.5 ${
              selectedRole === 'citizen'
                ? 'bg-emerald-500/10 border-emerald-500/50 shadow-sm shadow-emerald-500/20'
                : 'bg-slate-800/50 border-slate-700/60 hover:bg-slate-800'
            }`}
          >
            <div className={`p-2.5 rounded-xl ${selectedRole === 'citizen' ? 'bg-emerald-500 text-white' : 'bg-slate-700 text-slate-300'}`}>
              <User className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">Fuqaro (Citizen)</span>
                {selectedRole === 'citizen' && <Check className="w-4 h-4 text-emerald-400" />}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                AI Vazirlik ovozli yordamchisiga qo'ng'iroq qilish, savol berish va kerak bo'lsa navbatga turish.
              </p>

              {selectedRole === 'citizen' && (
                <div className="mt-3 pt-3 border-t border-slate-700/60 grid grid-cols-2 gap-2" onClick={(e) => e.stopPropagation()}>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Ism:</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Telefon raqam:</label>
                    <input
                      type="text"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Operator Option */}
          <div
            onClick={() => setSelectedRole('operator')}
            className={`p-4 rounded-xl border cursor-pointer transition flex items-start space-x-3.5 ${
              selectedRole === 'operator'
                ? 'bg-blue-500/10 border-blue-500/50 shadow-sm shadow-blue-500/20'
                : 'bg-slate-800/50 border-slate-700/60 hover:bg-slate-800'
            }`}
          >
            <div className={`p-2.5 rounded-xl ${selectedRole === 'operator' ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-300'}`}>
              <Headphones className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">Inson-Operator (Call-Center Operator)</span>
                {selectedRole === 'operator' && <Check className="w-4 h-4 text-blue-400" />}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                AI yo'naltirgan fuqarolarni qabul qilish, real-vaqtda javob qaytarish va navbatni boshqarish.
              </p>

              {selectedRole === 'operator' && (
                <div className="mt-3 pt-3 border-t border-slate-700/60 space-y-1.5" onClick={(e) => e.stopPropagation()}>
                  <label className="text-[11px] text-slate-400 block">Qaysi operator sifatida kirasiz?</label>
                  <div className="grid grid-cols-1 gap-1.5">
                    {operatorsList.map((op) => (
                      <button
                        key={op.id}
                        type="button"
                        onClick={() => setSelectedOpId(op.id)}
                        className={`text-left px-2.5 py-1.5 rounded-lg border text-xs flex items-center justify-between transition ${
                          selectedOpId === op.id
                            ? 'bg-blue-500/20 border-blue-500/60 text-blue-200'
                            : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-600'
                        }`}
                      >
                        <div>
                          <div className="font-medium text-white">{op.name}</div>
                          <div className="text-[10px] text-slate-400">{op.spec}</div>
                        </div>
                        {selectedOpId === op.id && <Check className="w-3.5 h-3.5 text-blue-400" />}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Admin Option */}
          <div
            onClick={() => setSelectedRole('admin')}
            className={`p-4 rounded-xl border cursor-pointer transition flex items-start space-x-3.5 ${
              selectedRole === 'admin'
                ? 'bg-purple-500/10 border-purple-500/50 shadow-sm shadow-purple-500/20'
                : 'bg-slate-800/50 border-slate-700/60 hover:bg-slate-800'
            }`}
          >
            <div className={`p-2.5 rounded-xl ${selectedRole === 'admin' ? 'bg-purple-500 text-white' : 'bg-slate-700 text-slate-300'}`}>
              <Shield className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">Vazirlik Ma'muri (Admin / Rahbariyat)</span>
                {selectedRole === 'admin' && <Check className="w-4 h-4 text-purple-400" />}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Barcha operatorlar holati, AI samaradorlik ko'rsatkichlari, navbat oqimi va umumiy tizim nazorati.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="text-xs text-slate-400">
            Joriy rol: <strong className="text-white capitalize">{session.role}</strong>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
            >
              Bekor qilish
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 transition flex items-center space-x-1"
            >
              <span>Saqlash va O'tish</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

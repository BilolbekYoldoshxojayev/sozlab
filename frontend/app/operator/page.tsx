import OperatorQueue from '@/components/OperatorQueue';
import RoleProtectedPage from '@/components/RoleProtectedPage';
import { Headset } from 'lucide-react';

export default function OperatorPage() {
  return (
    <RoleProtectedPage allowedRoles={['operator']}>
      <div className="flex flex-col gap-6">
        {/* Page Header */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-blue-100 text-[#0b2b50]">
                <Headset className="w-5 h-5 text-blue-700" />
              </span>
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                Call Markaz Operator Boshqaruv Paneli
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Jonli efirda barcha qo&apos;ng&apos;iroqlarni monitoring qilish, murakkab holatlarda qo&apos;ng&apos;iroqni
              o&apos;ziga qabul qilish va AI taklif etgan tavsiyalar orqali tezkor yordam ko&apos;rsatish.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl text-xs font-semibold text-emerald-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Operator Navbatchi: Faol</span>
            </div>
          </div>
        </div>

        {/* Main Operator Queue System */}
        <OperatorQueue />
      </div>
    </RoleProtectedPage>
  );
}

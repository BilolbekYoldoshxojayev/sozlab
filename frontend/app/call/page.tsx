import CallSimulator from '@/components/CallSimulator';

export default function CallPage() {
  return (
    <div className="fixed inset-x-0 bottom-0 top-[86px] sm:top-[90px] z-30 overflow-hidden bg-slate-950">
      <CallSimulator />
    </div>
  );
}

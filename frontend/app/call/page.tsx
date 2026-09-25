import CallSimulator from '@/components/CallSimulator';
import RoleProtectedPage from '@/components/RoleProtectedPage';

export default function CallPage() {
  return (
    <RoleProtectedPage allowedRoles={['citizen']}>
      <div className="fixed inset-x-0 bottom-0 top-[86px] sm:top-[90px] z-30 overflow-hidden bg-slate-950">
        <CallSimulator />
      </div>
    </RoleProtectedPage>
  );
}

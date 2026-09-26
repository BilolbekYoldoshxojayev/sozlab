import CallSimulator from '@/components/CallSimulator';
import RoleProtectedPage from '@/components/RoleProtectedPage';

export default function CallPage() {
  return (
    <RoleProtectedPage allowedRoles={['citizen']}>
      <div className="w-full flex-1 flex flex-col min-h-[calc(100vh-8rem)] transition-colors">
        <CallSimulator />
      </div>
    </RoleProtectedPage>
  );
}

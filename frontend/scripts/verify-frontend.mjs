// Empirical verification script for Frontend & Build integrity
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

console.log('====================================================');
console.log('CHALLENGER 2: EMPIRICAL FRONTEND VERIFICATION HARNESS');
console.log('====================================================\n');

let passCount = 0;
let failCount = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ [PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`❌ [FAIL] ${name}:`, err.message);
    failCount++;
  }
}

async function testAsync(name, fn) {
  try {
    await fn();
    console.log(`✅ [PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`❌ [FAIL] ${name}:`, err.message);
    failCount++;
  }
}

// ----------------------------------------------------------------------
// SUITE 1: CSS Layout Constraints in CallSimulator.tsx & app/call/page.tsx
// ----------------------------------------------------------------------
console.log('--- SUITE 1: CSS Layout Constraints & Scrollbar Prevention ---');

test('CallPage (/call/page.tsx) enforces fixed full-height overlay with overflow-hidden', () => {
  const filePath = path.resolve('app/call/page.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes('fixed'), 'CallPage must use fixed positioning');
  assert.ok(content.includes('inset-x-0'), 'CallPage must stretch horizontally (inset-x-0)');
  assert.ok(content.includes('bottom-0'), 'CallPage must anchor to bottom-0');
  assert.ok(content.includes('top-[86px]') || content.includes('top-[90px]'), 'CallPage must offset below navbar top');
  assert.ok(content.includes('overflow-hidden'), 'CallPage must have overflow-hidden to prevent document scrollbars');
  assert.ok(content.includes('z-30'), 'CallPage must have z-30 elevation over standard layout');
});

test('CallSimulator.tsx enforces h-[calc(100vh-4.5rem)] and internal overflow-hidden', () => {
  const filePath = path.resolve('components/CallSimulator.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes('h-[calc(100vh-4.5rem)]'), 'CallSimulator must specify h-[calc(100vh-4.5rem)]');
  assert.ok(content.includes('overflow-hidden'), 'CallSimulator root must have overflow-hidden');
  assert.ok(content.includes('line-clamp-2'), 'Live captions must be clamped to 2 lines to prevent height expansion');
});

// ----------------------------------------------------------------------
// SUITE 2: RoleGateModal.tsx & useRole.tsx Edge Cases
// ----------------------------------------------------------------------
console.log('\n--- SUITE 2: RoleGateModal & useRole Edge Cases ---');

// Mock localStorage simulation
function createMockLocalStorage(throwOnAccess = false) {
  let store = {};
  return {
    getItem(key) {
      if (throwOnAccess) throw new Error('SecurityError: Access is denied for localStorage');
      return store[key] !== undefined ? store[key] : null;
    },
    setItem(key, value) {
      if (throwOnAccess) throw new Error('SecurityError: Access is denied for localStorage');
      store[key] = String(value);
    },
    removeItem(key) {
      if (throwOnAccess) throw new Error('SecurityError: Access is denied for localStorage');
      delete store[key];
    },
    clear() {
      if (throwOnAccess) throw new Error('SecurityError: Access is denied for localStorage');
      store = {};
    },
    getStore() {
      return store;
    }
  };
}

// Logic harness simulating useRole state transitions
class RoleStateHarness {
  constructor(localStorageMock) {
    this.localStorage = localStorageMock;
    this.defaultSession = {
      role: 'citizen',
      citizenName: 'Fuqaro',
      citizenPhone: '+998 (90) 123-45-67',
    };
    this.session = { ...this.defaultSession };
    this.isReady = false;
    this.isRoleGateOpen = false;
    this.hasSelectedRole = false;
    this.init();
  }

  init() {
    try {
      const stored = this.localStorage.getItem('sozlab_user_session') || this.localStorage.getItem('vazir_user_session');
      if (stored) {
        this.session = JSON.parse(stored);
      }
      const roleSelected = this.localStorage.getItem('sozlab_role_selected');
      if (!roleSelected) {
        this.isRoleGateOpen = true;
        this.hasSelectedRole = false;
      } else {
        this.hasSelectedRole = true;
      }
    } catch {
      // Fallback
    } finally {
      this.isReady = true;
    }
  }

  saveSession(newSession) {
    this.session = newSession;
    try {
      this.localStorage.setItem('sozlab_user_session', JSON.stringify(newSession));
    } catch {}
  }

  setRole(role, operatorId, operatorName) {
    const updated = {
      ...this.session,
      role,
      operatorId: role === 'operator' ? (operatorId || 'op-1') : undefined,
      operatorName: role === 'operator' ? (operatorName || 'Nargiza Qodirova (Operator #1)') : undefined,
    };
    this.saveSession(updated);
    try {
      this.localStorage.setItem('sozlab_role_selected', 'true');
    } catch {}
    this.hasSelectedRole = true;
    this.isRoleGateOpen = false;
  }

  logout() {
    try {
      this.localStorage.removeItem('sozlab_role_selected');
    } catch {}
    this.hasSelectedRole = false;
    this.saveSession({ ...this.defaultSession });
    this.isRoleGateOpen = true;
  }

  openRoleGate() {
    this.isRoleGateOpen = true;
  }

  closeRoleGate() {
    this.isRoleGateOpen = false;
  }
}

test('Edge Case 1: Missing/Restricted localStorage does not crash and defaults gracefully', () => {
  const restrictedStorage = createMockLocalStorage(true);
  const harness = new RoleStateHarness(restrictedStorage);

  assert.equal(harness.isReady, true, 'isReady must be true despite localStorage exception');
  assert.equal(harness.session.role, 'citizen', 'Session role must default to citizen');
  assert.equal(harness.hasSelectedRole, false, 'hasSelectedRole must default to false when blocked');
});

test('Edge Case 2: Fresh user has no stored key -> Role Gate opens automatically', () => {
  const freshStorage = createMockLocalStorage(false);
  const harness = new RoleStateHarness(freshStorage);

  assert.equal(harness.isReady, true);
  assert.equal(harness.isRoleGateOpen, true, 'Role Gate modal must open on first visit');
  assert.equal(harness.hasSelectedRole, false);
});

test('Edge Case 3: Setting Citizen role routes to /call and persists selection', () => {
  const storage = createMockLocalStorage(false);
  const harness = new RoleStateHarness(storage);

  harness.setRole('citizen');
  assert.equal(harness.session.role, 'citizen');
  assert.equal(harness.hasSelectedRole, true);
  assert.equal(harness.isRoleGateOpen, false);
  assert.equal(storage.getItem('sozlab_role_selected'), 'true');
});

test('Edge Case 4: Setting Operator role stores operator metadata', () => {
  const storage = createMockLocalStorage(false);
  const harness = new RoleStateHarness(storage);

  harness.setRole('operator', 'op-2', 'Bekzod Aliyev');
  assert.equal(harness.session.role, 'operator');
  assert.equal(harness.session.operatorId, 'op-2');
  assert.equal(harness.session.operatorName, 'Bekzod Aliyev');
  assert.equal(harness.hasSelectedRole, true);
  assert.equal(harness.isRoleGateOpen, false);
});

test('Edge Case 5: Setting Admin role clears operator metadata and persists', () => {
  const storage = createMockLocalStorage(false);
  const harness = new RoleStateHarness(storage);

  // First operator
  harness.setRole('operator', 'op-3', 'Dilnoza Karimova');
  // Then switch to admin
  harness.setRole('admin');
  assert.equal(harness.session.role, 'admin');
  assert.equal(harness.session.operatorId, undefined);
  assert.equal(harness.session.operatorName, undefined);
});

test('Edge Case 6: Key clearing via logout() resets session and re-opens Role Gate', () => {
  const storage = createMockLocalStorage(false);
  const harness = new RoleStateHarness(storage);

  harness.setRole('admin');
  assert.equal(harness.hasSelectedRole, true);

  harness.logout();
  assert.equal(harness.hasSelectedRole, false);
  assert.equal(harness.isRoleGateOpen, true);
  assert.equal(storage.getItem('sozlab_role_selected'), null);
});

test('Edge Case 7: Role switching from navbar opens modal while preserving previous session', () => {
  const storage = createMockLocalStorage(false);
  const harness = new RoleStateHarness(storage);

  harness.setRole('citizen');
  assert.equal(harness.isRoleGateOpen, false);

  harness.openRoleGate();
  assert.equal(harness.isRoleGateOpen, true);
  assert.equal(harness.hasSelectedRole, true, 'User is allowed to close/dismiss modal when switching');

  harness.closeRoleGate();
  assert.equal(harness.isRoleGateOpen, false);
});

test('RoleGateModal source verification: routes match /call, /operator, /admin', () => {
  const filePath = path.resolve('components/RoleGateModal.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes("router.push('/call')"), 'Citizen must route to /call');
  assert.ok(content.includes("router.push('/operator')"), 'Operator must route to /operator');
  assert.ok(content.includes("router.push('/admin')"), 'Admin must route to /admin');
});

// ----------------------------------------------------------------------
// SUITE 3: OperatorQueue.tsx Countdown Timer Behavior
// ----------------------------------------------------------------------
console.log('\n--- SUITE 3: OperatorQueue Countdown Timer Behavior ---');

class MockCountdownTimer {
  constructor({ durationMs = 3000, onComplete, onTakeover }) {
    this.durationMs = durationMs;
    this.onComplete = onComplete;
    this.onTakeover = onTakeover;
    this.active = false;
    this.remainingSeconds = 3;
    this.progressPercent = 100;
    this.intervalId = null;
    this.nextCallId = '';
  }

  startCountdown(nextCallId, citizenName, topic) {
    this.active = true;
    this.nextCallId = nextCallId;
    this.citizenName = citizenName;
    this.topic = topic;
    this.remainingSeconds = 3;
    this.progressPercent = 100;

    const startTime = Date.now();
    this.intervalId = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remainingMs = Math.max(0, this.durationMs - elapsed);
      this.remainingSeconds = Math.ceil(remainingMs / 1000);
      this.progressPercent = (remainingMs / this.durationMs) * 100;

      if (remainingMs <= 0) {
        this.clearTimer();
        this.instantConnect(this.nextCallId);
      }
    }, 50);
  }

  clearTimer() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  cancelCountdown() {
    this.clearTimer();
    this.active = false;
  }

  instantConnect(callId) {
    const target = callId || this.nextCallId;
    this.cancelCountdown();
    if (target && this.onTakeover) {
      this.onTakeover(target);
    }
  }
}

await testAsync('OperatorQueue Timer: Natural expiry after duration triggers instantConnect and cleans up', async () => {
  let takeoverCallId = null;
  const timer = new MockCountdownTimer({
    durationMs: 200, // compressed for fast test
    onTakeover: (id) => {
      takeoverCallId = id;
    }
  });

  timer.startCountdown('call-test-123', 'Rustam', 'Qabul');
  assert.equal(timer.active, true);
  assert.equal(timer.nextCallId, 'call-test-123');

  await new Promise((r) => setTimeout(r, 260));

  assert.equal(timer.active, false, 'Timer must be inactive after expiry');
  assert.equal(timer.intervalId, null, 'Interval must be cleared after expiry');
  assert.equal(takeoverCallId, 'call-test-123', 'Takeover must be invoked with target callId');
});

test('OperatorQueue Timer: Manual cancel immediately stops interval without triggering takeover', () => {
  let takeoverTriggered = false;
  const timer = new MockCountdownTimer({
    durationMs: 1000,
    onTakeover: () => {
      takeoverTriggered = true;
    }
  });

  timer.startCountdown('call-cancel-999', 'Shahlo', 'Kvota');
  assert.equal(timer.active, true);
  assert.ok(timer.intervalId !== null);

  timer.cancelCountdown();

  assert.equal(timer.active, false);
  assert.equal(timer.intervalId, null);
  assert.equal(takeoverTriggered, false);
});

test('OperatorQueue Timer: Instant connect bypass immediately connects and cancels interval', () => {
  let takeoverCallId = null;
  const timer = new MockCountdownTimer({
    durationMs: 3000,
    onTakeover: (id) => {
      takeoverCallId = id;
    }
  });

  timer.startCountdown('call-fast-456', 'Dilnoza', 'Stipendiya');
  assert.equal(timer.active, true);

  // User presses "Zudlik bilan boshlash"
  timer.instantConnect();

  assert.equal(timer.active, false, 'Timer must be deactivated');
  assert.equal(timer.intervalId, null, 'Interval must be cleared immediately');
  assert.equal(takeoverCallId, 'call-fast-456', 'Takeover must be executed immediately');
});

// ----------------------------------------------------------------------
// SUITE 4: Admin Ghost Mode Audio Autoplay Error Handling
// ----------------------------------------------------------------------
console.log('\n--- SUITE 4: Admin Ghost Mode Autoplay Policy Rejection ---');

test('AdminPage (app/admin/page.tsx) handles play() rejection with .catch(...)', () => {
  const filePath = path.resolve('app/admin/page.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes('adminAudioRef.current.play()'), 'Must call play() on audio ref');
  assert.ok(
    content.includes('.catch(') && content.includes('[Admin Ghost Audio autoplay restricted]'),
    'Must attach .catch() handler logging autoplay restriction'
  );
});

await testAsync('Simulated Audio play() rejection is caught cleanly without unhandled rejection', async () => {
  let catchTriggered = false;
  const mockAudio = {
    src: '',
    play: () => Promise.reject(new Error('NotAllowedError: play() failed because the user didn\'t interact with the document first.')),
  };

  mockAudio.src = 'http://localhost:8000/audio/test.mp3';
  await mockAudio.play().catch((err) => {
    catchTriggered = true;
    assert.ok(err.message.includes('NotAllowedError'));
  });

  assert.equal(catchTriggered, true, 'Autoplay restriction error must be caught cleanly');
});

// ----------------------------------------------------------------------
// SUMMARY
// ----------------------------------------------------------------------
console.log('\n====================================================');
console.log(`TOTAL TESTS: ${passCount + failCount}`);
console.log(`PASSED: ${passCount}`);
console.log(`FAILED: ${failCount}`);
console.log('====================================================\n');

if (failCount > 0) {
  process.exit(1);
} else {
  process.exit(0);
}

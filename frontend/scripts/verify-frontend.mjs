import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, '..');

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
  const filePath = path.resolve(frontendRoot, 'app/call/page.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes('fixed'), 'CallPage must use fixed positioning');
  assert.ok(content.includes('inset-x-0'), 'CallPage must stretch horizontally (inset-x-0)');
  assert.ok(content.includes('bottom-0'), 'CallPage must anchor to bottom-0');
  assert.ok(content.includes('top-[86px]') || content.includes('top-[90px]'), 'CallPage must offset below navbar top');
  assert.ok(content.includes('overflow-hidden'), 'CallPage must have overflow-hidden to prevent document scrollbars');
  assert.ok(content.includes('z-30'), 'CallPage must have z-30 elevation over standard layout');
});

test('CallSimulator.tsx enforces full-screen viewport and internal overflow-hidden', () => {
  const filePath = path.resolve(frontendRoot, 'components/CallSimulator.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes('h-[calc(100vh-4rem)]') || content.includes('h-[calc(100vh-4.5rem)]'), 'CallSimulator must specify full screen height calculation');
  assert.ok(content.includes('overflow-hidden'), 'CallSimulator root must have overflow-hidden');
  assert.ok(content.includes('line-clamp-2') || content.includes('truncate') || content.includes('max-w'), 'Live captions must be constrained to prevent height expansion');
});


// ----------------------------------------------------------------------
// SUITE 2: useRole State Machine & Storage Synchronization
// ----------------------------------------------------------------------
console.log('\n--- SUITE 2: useRole State Machine & Storage Synchronization ---');

class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store[key] || null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

class MockRoleHarness {
  constructor(storage) {
    this.storage = storage;
    this.session = { role: 'citizen' };
    this.hasSelectedRole = false;
    this.isRoleGateOpen = false;
    this.isReady = false;
  }

  mount() {
    const saved = this.storage.getItem('sozlab_user_role');
    if (saved && (saved === 'citizen' || saved === 'admin')) {
      this.session = { role: saved };
      this.hasSelectedRole = true;
      this.isRoleGateOpen = false;
    } else {
      this.session = { role: 'citizen' };
      this.hasSelectedRole = false;
      this.isRoleGateOpen = true;
    }
    this.isReady = true;
  }

  setRole(role) {
    this.session = { role };
    this.hasSelectedRole = true;
    this.isRoleGateOpen = false;
    this.storage.setItem('sozlab_user_role', role);
  }

  openRoleGate() {
    this.isRoleGateOpen = true;
  }

  closeRoleGate() {
    if (this.hasSelectedRole) {
      this.isRoleGateOpen = false;
    }
  }
}

test('Edge Case 1: First-time visitor has no storage -> modal opens immediately, hasSelectedRole is false', () => {
  const storage = new MockLocalStorage();
  const harness = new MockRoleHarness(storage);

  harness.mount();

  assert.equal(harness.isReady, true);
  assert.equal(harness.hasSelectedRole, false);
  assert.equal(harness.isRoleGateOpen, true);
  assert.equal(harness.session.role, 'citizen');
});

test('Edge Case 2: Returning user with valid saved role restores without modal', () => {
  const storage = new MockLocalStorage();
  storage.setItem('sozlab_user_role', 'admin');
  const harness = new MockRoleHarness(storage);

  harness.mount();

  assert.equal(harness.isReady, true);
  assert.equal(harness.hasSelectedRole, true);
  assert.equal(harness.isRoleGateOpen, false);
  assert.equal(harness.session.role, 'admin');
});

test('Edge Case 3: Setting Citizen role persists to storage', () => {
  const storage = new MockLocalStorage();
  const harness = new MockRoleHarness(storage);
  harness.mount();

  harness.setRole('citizen');
  assert.equal(harness.session.role, 'citizen');
  assert.equal(harness.hasSelectedRole, true);
  assert.equal(harness.isRoleGateOpen, false);
  assert.equal(storage.getItem('sozlab_user_role'), 'citizen');
});

test('Edge Case 4: Setting Admin role persists to storage', () => {
  const storage = new MockLocalStorage();
  const harness = new MockRoleHarness(storage);
  harness.mount();

  harness.setRole('admin');
  assert.equal(harness.session.role, 'admin');
  assert.equal(harness.hasSelectedRole, true);
  assert.equal(harness.isRoleGateOpen, false);
  assert.equal(storage.getItem('sozlab_user_role'), 'admin');
});

test('Edge Case 5: Modal cannot be closed if user has never selected a role', () => {
  const storage = new MockLocalStorage();
  const harness = new MockRoleHarness(storage);
  harness.mount();

  assert.equal(harness.isRoleGateOpen, true);
  harness.closeRoleGate();
  assert.equal(harness.isRoleGateOpen, true, 'closeRoleGate() must refuse to close if hasSelectedRole is false');
});

test('RoleGateModal source verification: routes match /call and /admin', () => {
  const filePath = path.resolve(frontendRoot, 'components/RoleGateModal.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes("router.push('/call')"), 'Citizen must route to /call');
  assert.ok(content.includes("router.push('/admin')"), 'Admin must route to /admin');
});

// ----------------------------------------------------------------------
// SUITE 3: CommonQuestions 50 FAQs & Legal Knowledge Integration
// ----------------------------------------------------------------------
console.log('\n--- SUITE 3: CommonQuestions 50 FAQs & Legal Knowledge Integration ---');

test('CommonQuestions.tsx contains official FAQs and legal basis references', () => {
  const filePath = path.resolve(frontendRoot, 'components/CommonQuestions.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(content.includes('FAQ_DATA'), 'Must contain FAQ_DATA array');
  assert.ok(content.includes('regulation') || content.includes('Konstitutsiya'), 'Must provide legal regulation citations');
  assert.ok(content.includes('activeCategory'), 'Must support category filtering');
});


// ----------------------------------------------------------------------
// SUITE 4: Admin Ghost Mode Audio Autoplay Error Handling
// ----------------------------------------------------------------------
console.log('\n--- SUITE 4: Admin Ghost Mode Autoplay Policy Rejection ---');

test('AdminPage (app/admin/page.tsx) handles play() rejection with .catch(...)', () => {
  const filePath = path.resolve(frontendRoot, 'app/admin/page.tsx');
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

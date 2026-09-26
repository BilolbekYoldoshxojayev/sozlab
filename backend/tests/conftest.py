import pytest
import shutil
from pathlib import Path
import sys

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.call_manager import call_manager

@pytest.fixture(autouse=True, scope="session")
def isolate_test_call_storage():
    """
    Session fixture that redirects CallManager's persistence directory
    away from production `backend/data/saved_calls` to an isolated `test_saved_calls`.
    Cleans up all test data on teardown so production storage is never polluted.
    """
    test_dir = backend_dir / "data" / "test_saved_calls"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Switch call_manager to test storage
    original_dir = call_manager.saved_calls_dir
    call_manager.saved_calls_dir = test_dir
    call_manager._calls.clear()
    
    yield
    
    # Restore and clean up
    call_manager.saved_calls_dir = original_dir
    if test_dir.exists():
        shutil.rmtree(test_dir, ignore_errors=True)

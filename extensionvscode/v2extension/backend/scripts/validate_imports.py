"""
Script para validar que todos los imports funcionen correctamente.

Ejecutar con Python 3.11+
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def validate_imports():
    """Validate all critical imports."""
    errors = []
    success = []

    # Test 1: Core config
    try:
        from app.core.config import settings
        success.append("✓ Core config")
    except Exception as e:
        errors.append(f"✗ Core config: {e}")

    # Test 2: Database
    try:
        from app.core.database import AsyncSessionLocal, init_db
        success.append("✓ Database core")
    except Exception as e:
        errors.append(f"✗ Database core: {e}")

    # Test 3: Models
    try:
        from app.models import (
            User, Course, Goal, Task, CodeSnapshot,
            Event, Embedding, RateLimitAudit
        )
        success.append("✓ Models (8 models)")
    except Exception as e:
        errors.append(f"✗ Models: {e}")

    # Test 4: Services
    try:
        from app.services.goal_service import GoalService
        from app.services.task_service import TaskService
        from app.services.rate_limit_audit_service import RateLimitAuditService
        success.append("✓ Services")
    except Exception as e:
        errors.append(f"✗ Services: {e}")

    # Test 5: Rate Limiter
    try:
        from app.core.rate_limiter import RateLimiter, TokenBucket, get_rate_limiter
        success.append("✓ Rate Limiter")
    except Exception as e:
        errors.append(f"✗ Rate Limiter: {e}")

    # Test 6: OpenAI Tracker
    try:
        from app.core.openai_tracker import OpenAITracker
        success.append("✓ OpenAI Tracker")
    except Exception as e:
        errors.append(f"✗ OpenAI Tracker: {e}")

    # Test 7: RAG Tools
    try:
        from app.agents.tools.rag_tools import (
            RAGTools, get_similar_goals, get_similar_code
        )
        success.append("✓ RAG Tools")
    except Exception as e:
        errors.append(f"✗ RAG Tools: {e}")

    # Test 8: LangGraph
    try:
        from app.agents.graph import create_agent_graph
        from app.agents.nodes import AgentNodes
        success.append("✓ LangGraph Agents")
    except Exception as e:
        errors.append(f"✗ LangGraph Agents: {e}")

    # Test 9: API Routes
    try:
        from app.api.routes import goals, tasks, code_snapshots, events
        from app.api.routes.admin import admin_router
        success.append("✓ API Routes")
    except Exception as e:
        errors.append(f"✗ API Routes: {e}")

    # Test 10: Middleware
    try:
        from app.middleware.rate_limit_middleware import RateLimitMiddleware
        success.append("✓ Middleware")
    except Exception as e:
        errors.append(f"✗ Middleware: {e}")

    # Test 11: Main app
    try:
        from app.main import app
        success.append("✓ FastAPI App")
    except Exception as e:
        errors.append(f"✗ FastAPI App: {e}")

    # Print results
    print("\n" + "="*60)
    print("IMPORT VALIDATION RESULTS")
    print("="*60)

    print(f"\n{'SUCCESS:':<20} {len(success)}/{len(success) + len(errors)}")
    for s in success:
        print(f"  {s}")

    if errors:
        print(f"\n{'ERRORS:':<20} {len(errors)}")
        for e in errors:
            print(f"  {e}")

    print("\n" + "="*60)

    if errors:
        print("\n⚠️  Some imports failed. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All imports successful! The application structure is valid.")
        sys.exit(0)


if __name__ == "__main__":
    print("Validating Python version...")
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required. Current version: {sys.version}")
        print("   Please use Python 3.11 or run with Docker.")
        sys.exit(1)

    print(f"✓ Python {sys.version.split()[0]}")
    print("\nValidating imports...")

    validate_imports()

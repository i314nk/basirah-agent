"""
Test script for Phase 6C.1 database setup.
Verifies Docker container, database connection, and basic operations.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def print_section(title):
    """Print section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_docker_installed():
    """Test if Docker is installed."""
    print_section("Step 1: Checking Docker Installation")

    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"[OK] Docker installed: {result.stdout.strip()}")
            return True
        else:
            print("[FAIL] Docker command failed")
            return False
    except FileNotFoundError:
        print("[FAIL] Docker not found. Please install Docker Desktop.")
        print("   Download from: https://www.docker.com/products/docker-desktop")
        return False
    except Exception as e:
        print(f"[FAIL] Error checking Docker: {e}")
        return False


def test_docker_compose_installed():
    """Test if Docker Compose is installed."""
    print_section("Step 2: Checking Docker Compose")

    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"[OK] Docker Compose installed: {result.stdout.strip()}")
            return True
        else:
            print("[FAIL] Docker Compose command failed")
            return False
    except FileNotFoundError:
        print("[FAIL] Docker Compose not found.")
        print("   It should be included with Docker Desktop.")
        return False
    except Exception as e:
        print(f"[FAIL] Error checking Docker Compose: {e}")
        return False


def test_docker_running():
    """Test if Docker daemon is running."""
    print_section("Step 3: Checking Docker Daemon")

    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("[OK] Docker daemon is running")
            return True
        else:
            print("[FAIL] Docker daemon is not running")
            print("   Please start Docker Desktop")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking Docker daemon: {e}")
        return False


def start_database_container():
    """Start the PostgreSQL container."""
    print_section("Step 4: Starting PostgreSQL Container")

    try:
        print("Starting container with docker-compose...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("[OK] Container started successfully")
            print("\nWaiting for PostgreSQL to be ready (15 seconds)...")
            time.sleep(15)
            return True
        else:
            print(f"[FAIL] Failed to start container")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"[FAIL] Error starting container: {e}")
        return False


def check_container_status():
    """Check if basirah_db container is running."""
    print_section("Step 5: Checking Container Status")

    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=basirah_db", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            print(f"[OK] Container status: {result.stdout.strip()}")
            return True
        else:
            print("[FAIL] Container is not running")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking container status: {e}")
        return False


def test_psycopg2_installed():
    """Test if psycopg2 is installed."""
    print_section("Step 6: Checking psycopg2 Installation")

    try:
        import psycopg2
        print(f"[OK] psycopg2 installed: version {psycopg2.__version__}")
        return True
    except ImportError:
        print("[FAIL] psycopg2 not installed")
        print("   Run: pip install -r requirements.txt")
        return False


def test_database_connection():
    """Test database connection."""
    print_section("Step 7: Testing Database Connection")

    try:
        from src.storage.database import get_db

        db = get_db()
        print("[OK] DatabaseManager initialized")

        # Test health check
        if db.health_check():
            print("[OK] Database connection successful")
            return True
        else:
            print("[FAIL] Database health check failed")
            return False
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Docker container is running: docker ps")
        print("2. Check container logs: docker logs basirah_db")
        print("3. Verify .env has correct DB credentials")
        return False


def test_database_schema():
    """Test if database schema exists."""
    print_section("Step 8: Verifying Database Schema")

    try:
        from src.storage.database import get_db

        db = get_db()

        # Check if tables exist
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """

        tables = db.execute_query(query)

        if tables:
            print(f"[OK] Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table['table_name']}")
            return True
        else:
            print("[FAIL] No tables found. Schema may not have been created.")
            print("   The schema should auto-create when container starts.")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking schema: {e}")
        return False


def test_basic_operations():
    """Test basic database operations."""
    print_section("Step 9: Testing Basic Operations")

    try:
        from src.storage.database import get_db

        db = get_db()

        # Test insert into companies
        print("Testing INSERT operation...")
        insert_query = """
        INSERT INTO companies (ticker, company_name, sector, industry)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker) DO UPDATE
        SET company_name = EXCLUDED.company_name
        RETURNING id
        """

        with db.get_cursor() as cur:
            cur.execute(insert_query, ('TEST', 'Test Company', 'Technology', 'Software'))
            result = cur.fetchone()
            company_id = result['id']

        print(f"[OK] INSERT successful (company_id: {company_id})")

        # Test select
        print("Testing SELECT operation...")
        select_query = "SELECT * FROM companies WHERE ticker = %s"
        result = db.execute_query(select_query, ('TEST',))

        if result:
            print(f"[OK] SELECT successful")
            print(f"   Retrieved: {result[0]['company_name']}")
        else:
            print("[FAIL] SELECT returned no results")
            return False

        # Test delete (cleanup)
        print("Testing DELETE operation...")
        delete_query = "DELETE FROM companies WHERE ticker = %s"
        rows = db.execute_update(delete_query, ('TEST',))

        print(f"[OK] DELETE successful ({rows} rows)")

        return True

    except Exception as e:
        print(f"[FAIL] Basic operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """Print test summary."""
    print_section("Test Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"\n[RESULTS] Results: {passed}/{total} tests passed")

    if failed > 0:
        print(f"\n[FAIL] Failed tests:")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")

    if passed == total:
        print("\n[OK] All tests passed! Database infrastructure is ready.")
        print("\n[NEXT] Next steps:")
        print("   1. Implementation is ready for Stage 2 (AnalysisStorage)")
        print("   2. View container logs: docker logs basirah_db")
        print("   3. Access database: docker exec -it basirah_db psql -U basirah_user -d basirah")
    else:
        print("\n[FAIL] Some tests failed. Please fix the issues above.")
        print("\n[FIXES] Common fixes:")
        print("   - Install Docker Desktop if not installed")
        print("   - Start Docker Desktop")
        print("   - Run: pip install -r requirements.txt")
        print("   - Check .env has correct credentials")


def main():
    """Run all tests."""
    print("\n" + "basirah Database Infrastructure Test".center(60))
    print("Phase 6C.1 - Analysis History Setup".center(60))

    results = {}

    # Run tests in sequence
    results['Docker Installed'] = test_docker_installed()
    if not results['Docker Installed']:
        print_summary(results)
        return

    results['Docker Compose Installed'] = test_docker_compose_installed()
    if not results['Docker Compose Installed']:
        print_summary(results)
        return

    results['Docker Running'] = test_docker_running()
    if not results['Docker Running']:
        print_summary(results)
        return

    results['Container Started'] = start_database_container()
    if not results['Container Started']:
        print_summary(results)
        return

    results['Container Status'] = check_container_status()

    results['psycopg2 Installed'] = test_psycopg2_installed()
    if not results['psycopg2 Installed']:
        print_summary(results)
        return

    results['Database Connection'] = test_database_connection()
    if not results['Database Connection']:
        print_summary(results)
        return

    results['Database Schema'] = test_database_schema()
    results['Basic Operations'] = test_basic_operations()

    print_summary(results)


if __name__ == "__main__":
    main()

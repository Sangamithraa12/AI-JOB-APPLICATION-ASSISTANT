"""Tests for SQLite Application Tracker and Database Operations (Feature H).

Covers:
- Database schema initialization
- CRUD operations (Create, Read, Update, Delete)
- Status validation and constraints
- Search keyword matching and status filtering
- Dashboard statistics calculation
"""

import os
import tempfile
import unittest
from pathlib import Path

from config import Config
from database import (
    init_db,
    add_application,
    get_applications,
    get_application_by_id,
    update_application,
    delete_application,
    get_application_stats,
    VALID_STATUSES
)

class TestApplicationTracker(unittest.TestCase):
    """Test suite for SQLite tracker persistence and analytics."""

    @classmethod
    def setUpClass(cls):
        """Use an isolated temporary SQLite database for testing."""
        import gc
        cls.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.test_db_path = Path(cls.temp_dir.name) / "test_tracker.db"
        Config.DATABASE_PATH = cls.test_db_path
        init_db(seed_sample_data=False)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary directory and database."""
        import gc
        gc.collect()
        try:
            cls.temp_dir.cleanup()
        except Exception:
            pass

    def setUp(self):
        """Clear table before each test for clean isolation."""
        from database.db import get_db
        with get_db() as conn:
            conn.execute("DELETE FROM applications")
            conn.commit()

    def test_add_and_retrieve_application(self):
        """Verify inserting an application and retrieving it by ID."""
        app_id = add_application(
            company="Test Corp",
            role="Automation Associate",
            application_date="2026-10-26",
            job_link="https://testcorp.com/jobs/1",
            status="Applied",
            notes="Initial submission."
        )
        self.assertIsInstance(app_id, int)
        self.assertGreater(app_id, 0)

        record = get_application_by_id(app_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["company"], "Test Corp")
        self.assertEqual(record["role"], "Automation Associate")
        self.assertEqual(record["status"], "Applied")

    def test_invalid_status_rejection(self):
        """Status outside the allowed list must raise a ValueError."""
        with self.assertRaises(ValueError):
            add_application(
                company="Acme Corp",
                role="Engineer",
                application_date="2026-10-26",
                status="InvalidStatus"
            )

    def test_update_application(self):
        """Verify updating existing application fields."""
        app_id = add_application(
            company="Nova Systems",
            role="Junior Dev",
            application_date="2026-10-10",
            status="Applied"
        )

        updated = update_application(
            app_id=app_id,
            company="Nova Systems",
            role="Junior Dev",
            application_date="2026-10-10",
            status="Interview",
            notes="Passed screening round."
        )
        self.assertTrue(updated)

        record = get_application_by_id(app_id)
        self.assertEqual(record["status"], "Interview")
        self.assertEqual(record["notes"], "Passed screening round.")

    def test_delete_application(self):
        """Verify application deletion."""
        app_id = add_application(
            company="Temp Labs",
            role="Intern",
            application_date="2026-10-01",
            status="Interested"
        )
        deleted = delete_application(app_id)
        self.assertTrue(deleted)

        record = get_application_by_id(app_id)
        self.assertIsNone(record)

    def test_search_and_filter(self):
        """Verify keyword search and status filtering."""
        add_application("Alpha Tech", "Backend Engineer", "2026-10-01", status="Applied", notes="FastAPI")
        add_application("Beta Solutions", "Data Analyst", "2026-10-02", status="Interview", notes="SQL")
        add_application("Gamma AI", "Backend Engineer", "2026-10-03", status="Offer", notes="Python")

        # Search by role keyword
        backend_apps = get_applications(search="Backend")
        self.assertEqual(len(backend_apps), 2)

        # Filter by status
        interview_apps = get_applications(status="Interview")
        self.assertEqual(len(interview_apps), 1)
        self.assertEqual(interview_apps[0]["company"], "Beta Solutions")

    def test_dashboard_statistics(self):
        """Verify metric calculation: totals, status counts, conversion rates."""
        add_application("Company A", "Role A", "2026-10-01", status="Applied")
        add_application("Company B", "Role B", "2026-10-02", status="Assessment")
        add_application("Company C", "Role C", "2026-10-03", status="Interview")
        add_application("Company D", "Role D", "2026-10-04", status="Offer")

        stats = get_application_stats()
        self.assertEqual(stats["total_applications"], 4)
        self.assertEqual(stats["interviews"], 1)
        self.assertEqual(stats["offers"], 1)
        self.assertEqual(stats["assessment"], 1)
        self.assertEqual(stats["applied"], 1)
        self.assertGreater(stats["interview_rate"], 0.0)
        self.assertGreater(stats["offer_rate"], 0.0)

if __name__ == "__main__":
    unittest.main()

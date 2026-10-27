import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from config import Config

VALID_STATUSES = [
    "Interested",
    "Applied",
    "Assessment",
    "Interview",
    "Offer",
    "Rejected"
]

def get_db_connection() -> sqlite3.Connection:
    """Establish and return a SQLite connection with row factory configured."""
    Config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(Config.DATABASE_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_db():
    """Context manager ensuring connection is closed properly on exit."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db(seed_sample_data: bool = True) -> None:
    """Initialize database tables and indexes. Seed sample data if empty."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                application_date TEXT NOT NULL,
                job_link TEXT,
                status TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_applications_date ON applications(application_date)
        """)
        conn.commit()

        # Check if table is empty and seed demo data
        if seed_sample_data:
            cursor.execute("SELECT COUNT(*) AS count FROM applications")
            row = cursor.fetchone()
            if row and row["count"] == 0:
                _seed_initial_applications(cursor)
                conn.commit()

def _seed_initial_applications(cursor: sqlite3.Cursor) -> None:
    """Seed realistic initial applications for demonstration purposes."""
    sample_apps = [
        (
            "Gokul Infocare",
            "AI Growth & Automation Associate",
            "2026-10-24",
            "https://gokulinfocare.com/careers/ai-associate",
            "Assessment",
            "Completed initial technical challenge. Preparing for project presentation."
        ),
        (
            "CloudScale AI Labs",
            "Junior Machine Learning Engineer",
            "2026-10-20",
            "https://cloudscale.ai/jobs/jr-mle",
            "Interview",
            "Round 1 screening completed. Technical interview scheduled for next week."
        ),
        (
            "Nexus FinTech Solutions",
            "Full-Stack Python Developer",
            "2026-10-18",
            "https://nexusfin.io/openings/python-dev",
            "Applied",
            "Submitted tailored resume and cover letter emphasizing Flask and API design."
        ),
        (
            "Synthetix Automation",
            "Prompt Engineer & Automation Intern",
            "2026-10-12",
            "https://synthetix.tech/careers",
            "Offer",
            "Received offer letter for 6-month graduate rotation. Decision pending review."
        ),
        (
            "Apex Data Systems",
            "Data Analyst Associate",
            "2026-10-05",
            "https://apexdata.org/jobs/analyst",
            "Rejected",
            "Received polite rejection email noting preference for candidates with 2+ years SQL experience."
        ),
        (
            "Elevate AI Studio",
            "Generative AI Solutions Specialist",
            "2026-10-25",
            "https://elevate-ai.studio/jobs/genai",
            "Interested",
            "Reviewing job description and skill overlap before customizing resume."
        )
    ]
    cursor.executemany("""
        INSERT INTO applications (company, role, application_date, job_link, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_apps)

def add_application(
    company: str,
    role: str,
    application_date: str,
    job_link: Optional[str] = None,
    status: str = "Applied",
    notes: Optional[str] = None
) -> int:
    """Insert a new job application. Returns new record ID."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")

    company = company.strip()
    role = role.strip()
    if not company or not role:
        raise ValueError("Company and Role are required fields.")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (company, role, application_date, job_link, status, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (company, role, application_date, job_link.strip() if job_link else "", status, notes.strip() if notes else ""))
        conn.commit()
        return cursor.lastrowid

def get_applications(search: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch applications with optional keyword search and status filter."""
    query = "SELECT * FROM applications WHERE 1=1"
    params: List[Any] = []

    if status and status in VALID_STATUSES:
        query += " AND status = ?"
        params.append(status)

    if search:
        search_term = f"%{search.strip()}%"
        query += " AND (company LIKE ? OR role LIKE ? OR notes LIKE ?)"
        params.extend([search_term, search_term, search_term])

    query += " ORDER BY application_date DESC, id DESC"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_application_by_id(app_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single application by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_application(
    app_id: int,
    company: str,
    role: str,
    application_date: str,
    job_link: Optional[str] = None,
    status: str = "Applied",
    notes: Optional[str] = None
) -> bool:
    """Update an existing application. Returns True if updated."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")

    company = company.strip()
    role = role.strip()
    if not company or not role:
        raise ValueError("Company and Role are required fields.")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE applications
            SET company = ?, role = ?, application_date = ?, job_link = ?, status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (company, role, application_date, job_link.strip() if job_link else "", status, notes.strip() if notes else "", app_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_application(app_id: int) -> bool:
    """Delete an application by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_application_stats() -> Dict[str, Any]:
    """Calculate and return application metrics and status distribution."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Total applications
        cursor.execute("SELECT COUNT(*) AS total FROM applications")
        total = cursor.fetchone()["total"]

        # Breakdown by status
        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM applications
            GROUP BY status
        """)
        status_counts = {status: 0 for status in VALID_STATUSES}
        for row in cursor.fetchall():
            status_counts[row["status"]] = row["count"]

        # Recent 5 applications
        cursor.execute("""
            SELECT id, company, role, application_date, status
            FROM applications
            ORDER BY application_date DESC, id DESC
            LIMIT 5
        """)
        recent_apps = [dict(row) for row in cursor.fetchall()]

        # Calculated conversion metrics
        applied_or_more = total - status_counts.get("Interested", 0)
        interview_count = status_counts.get("Interview", 0)
        offer_count = status_counts.get("Offer", 0)

        interview_rate = round((interview_count / applied_or_more * 100), 1) if applied_or_more > 0 else 0.0
        offer_rate = round((offer_count / applied_or_more * 100), 1) if applied_or_more > 0 else 0.0

        return {
            "total_applications": total,
            "status_counts": status_counts,
            "interviews": interview_count,
            "offers": offer_count,
            "applied": status_counts.get("Applied", 0),
            "assessment": status_counts.get("Assessment", 0),
            "interested": status_counts.get("Interested", 0),
            "rejected": status_counts.get("Rejected", 0),
            "interview_rate": interview_rate,
            "offer_rate": offer_rate,
            "recent_applications": recent_apps
        }

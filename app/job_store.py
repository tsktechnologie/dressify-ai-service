"""Durable SQLite job store for single-node development. Use Postgres for production."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

def _connect():
    db = os.getenv("JOB_DB_PATH", "dressify_jobs.sqlite3")
    conn = sqlite3.connect(db, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, type TEXT NOT NULL, status TEXT NOT NULL,
        inputs TEXT NOT NULL, result TEXT, error_code TEXT,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn

def create_job(kind: str, inputs: dict):
    now = datetime.now(timezone.utc).isoformat()
    job = dict(id=str(uuid4()), type=kind, status="queued", inputs=inputs,
               result=None, error_code=None, created_at=now, updated_at=now)
    with _connect() as db:
        db.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (job["id"], kind, "queued", json.dumps(inputs), None, None, now, now))
    return job

def get_job(job_id: str):
    with _connect() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if row is None:
        return None
    job = dict(row)
    job["inputs"] = json.loads(job["inputs"])
    job["result"] = json.loads(job["result"]) if job["result"] else None
    return job

def claim_next():
    """Atomically claim a queued job; one worker per job."""
    with _connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT id FROM jobs WHERE status='queued' ORDER BY created_at, id LIMIT 1").fetchone()
        if row is None:
            return None
        now = datetime.now(timezone.utc).isoformat()
        db.execute("UPDATE jobs SET status='processing', updated_at=? WHERE id=? AND status='queued'", (now, row["id"]))
        return row["id"]

def finish(job_id: str, status: str, result: dict | None = None, error_code: str | None = None):
    if status not in ("succeeded", "failed"):
        raise ValueError("Invalid terminal status")
    with _connect() as db:
        updated = db.execute(
            "UPDATE jobs SET status=?, result=?, error_code=?, updated_at=? WHERE id=? AND status='processing'",
            (status, json.dumps(result) if result else None, error_code,
             datetime.now(timezone.utc).isoformat(), job_id))
        if updated.rowcount != 1:
            raise ValueError("Job is not processing")

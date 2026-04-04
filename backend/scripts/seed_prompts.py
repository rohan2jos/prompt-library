"""
Seed script: loads data/prompts.seed.json into the prompts table.

Usage (from repo root):
    uv run backend/scripts/seed_prompts.py

Requires DATABASE_URL to be set via .env at the repo root, or exported in the
environment before running.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "psycopg2-binary>=2.9",
#   "python-dotenv>=1.0",
# ]
# ///

import json
import os
import sys
from pathlib import Path

# Load .env from repo root — no-op if python-dotenv is not installed
try:
    from dotenv import load_dotenv
    load_dotenv()  # searches upward from cwd (repo root) for .env
except ImportError:
    pass

import psycopg2
from psycopg2.extras import Json

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "data" / "prompts.seed.json"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    cwd = Path.cwd()
    print("ERROR: DATABASE_URL is not set.", file=sys.stderr)
    print(f"  cwd                : {cwd}", file=sys.stderr)
    print(f"  .env (cwd)         : {cwd / '.env'} — exists: {(cwd / '.env').exists()}", file=sys.stderr)
    print(f"  __file__           : {Path(__file__).resolve()}", file=sys.stderr)
    repo_env = Path(__file__).resolve().parents[2] / ".env"
    print(f"  .env (parents[2])  : {repo_env} — exists: {repo_env.exists()}", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Load seed data
# ---------------------------------------------------------------------------
with open(DATA_FILE) as f:
    prompts = json.load(f)

# ---------------------------------------------------------------------------
# Transform to match schema constraints:
#   prompt_type  CHECK IN ('text', 'other')
#   input_mode   CHECK IN ('text')
#   output_mode  CHECK IN ('json')
# ---------------------------------------------------------------------------
for p in prompts:
    p["prompt_type"] = "text"
    p["input_mode"]  = "text"
    p["output_mode"] = "json"

# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------
UPSERT_SQL = """
    INSERT INTO prompts
        (slug, title, description, category, tags, prompt_body,
         prompt_type, sandbox_mode, input_mode, output_mode)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (slug) DO UPDATE SET
        title        = EXCLUDED.title,
        description  = EXCLUDED.description,
        category     = EXCLUDED.category,
        tags         = EXCLUDED.tags,
        prompt_body  = EXCLUDED.prompt_body,
        prompt_type  = EXCLUDED.prompt_type,
        sandbox_mode = EXCLUDED.sandbox_mode,
        input_mode   = EXCLUDED.input_mode,
        output_mode  = EXCLUDED.output_mode,
        updated_at   = now()
    RETURNING xmax
"""

inserted = updated = 0
conn = psycopg2.connect(DATABASE_URL)

try:
    with conn:                        # auto-commit on success, rollback on error
        with conn.cursor() as cur:
            for p in prompts:
                cur.execute(UPSERT_SQL, (
                    p["slug"],
                    p["title"],
                    p["description"],
                    p["category"],
                    Json(p["tags"]),
                    p["prompt_body"],
                    p["prompt_type"],
                    p["sandbox_mode"],
                    p["input_mode"],
                    p["output_mode"],
                ))
                # xmax == 0  → row was freshly inserted
                # xmax != 0  → row already existed and was updated
                xmax = cur.fetchone()[0]
                if xmax == 0:
                    inserted += 1
                else:
                    updated += 1
finally:
    conn.close()

print(f"Done — inserted: {inserted}, updated: {updated}")

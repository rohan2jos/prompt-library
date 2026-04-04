# backend

Prompt Library backend MVP — read path (FastAPI + Supabase).

---

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.11. No venv or pip needed.

```bash
# install dependencies
uv sync
```

---

## Running the server

```bash
uv run uvicorn main:app --reload
```

---

## Database

Supabase is used as the hosted Postgres database. There is no local DB.

### First-time migration

The migration must be run manually via the Supabase Dashboard:

1. Open [Supabase Dashboard](https://supabase.com) → your project → **SQL Editor**
2. Paste the contents of:
   ```
   supabase/migrations/20260404000000_create_prompts_table.sql
   ```
3. Click **Run**

---

## Seeding data

1. Copy the environment reference file and fill in your values:
   ```bash
   cp env.local.reference .env
   # edit .env and set DATABASE_URL to your Supabase connection string
   ```

2. Run the seed script:
   ```bash
   uv run backend/scripts/seed_prompts.py
   ```

The script is idempotent — safe to run multiple times.

---

## Notes

- No ORM — all queries use direct SQL via `psycopg2`
- The schema is the source of truth, not the seed data
- Seed data is transformed on load to match schema constraints

from fastapi import APIRouter, HTTPException
from app.db.client import get_connection
from app.models.prompt import PromptDetail, PromptListItem, PromptListResponse

router = APIRouter()


@router.get("/prompts", response_model=PromptListResponse)
def list_prompts(
    q: str | None = None,
    sandbox_mode: str | None = None,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    conditions = []
    params = []

    if q:
        conditions.append(
            "(title ILIKE %s OR description ILIKE %s OR category ILIKE %s OR tags::text ILIKE %s)"
        )
        like = f"%{q}%"
        params.extend([like, like, like, like])

    if sandbox_mode:
        conditions.append("sandbox_mode = %s")
        params.append(sandbox_mode)

    if category:
        conditions.append("category = %s")
        params.append(category)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM prompts {where}", params)
            total = cur.fetchone()[0]

            cur.execute(
                f"""
                SELECT slug, title, description, category, tags, sandbox_mode
                FROM prompts
                {where}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

    items = [
        PromptListItem(
            slug=row[0],
            title=row[1],
            description=row[2],
            category=row[3],
            tags=row[4],
            sandbox_mode=row[5],
        )
        for row in rows
    ]

    return PromptListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{slug}", response_model=PromptDetail)
def get_prompt(slug: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT slug, title, description, category, tags, sandbox_mode,
                       prompt_body, prompt_type, input_mode, output_mode
                FROM prompts
                WHERE slug = %s
                """,
                (slug,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PromptDetail(
        slug=row[0],
        title=row[1],
        description=row[2],
        category=row[3],
        tags=row[4],
        sandbox_mode=row[5],
        prompt_body=row[6],
        prompt_type=row[7],
        input_mode=row[8],
        output_mode=row[9],
    )

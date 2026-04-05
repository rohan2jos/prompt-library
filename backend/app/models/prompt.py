from pydantic import BaseModel


class PromptListItem(BaseModel):
    slug: str
    title: str
    description: str
    category: str
    tags: list[str]
    sandbox_mode: str


class PromptDetail(PromptListItem):
    prompt_body: str
    prompt_type: str
    input_mode: str
    output_mode: str


class PromptListResponse(BaseModel):
    items: list[PromptListItem]
    total: int
    limit: int
    offset: int
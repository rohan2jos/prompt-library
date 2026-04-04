create extension if not exists "pgcrypto";

create table prompts (
  id           uuid        primary key default gen_random_uuid(),
  slug         text        unique not null,
  title        text        not null,
  description  text        not null,
  category     text        not null,
  tags         jsonb       not null,
  prompt_body  text        not null,
  prompt_type  text        not null check (prompt_type in ('text', 'other')),
  sandbox_mode text        not null check (sandbox_mode in ('run', 'copy_only')),
  input_mode   text        not null check (input_mode in ('text')),
  output_mode  text        not null check (output_mode in ('json')),
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index on prompts (created_at desc);
create index on prompts (category);
create index on prompts (sandbox_mode);
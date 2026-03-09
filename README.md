# Database Design Skill

Production-grade database schema design skill for AI coding assistants. Supports PostgreSQL, MySQL, and MongoDB with native SQL (no ORM). Use it when creating new databases, designing tables, defining relationships, indexing strategies, handling migrations, applying security hardening, or adding multi-tenancy.

---

## Installation

```bash
npx skills add https://github.com/rahmat1929/skill-database-design --skill database-design
```

### Manual install

Clone and copy to your preferred scope:

| Scope | Path |
|-------|------|
| Project (shared) | `.agents/skills/database-design/` |
| Personal (local) | `~/.cursor/skills/database-design/` |

```bash
git clone https://github.com/rahmat1929/skill-database-design.git
cp -r skill-database-design/ .agents/skills/database-design/
```

### Verify installation

Ask the agent:

> "Design a database for my new task management application."

If it responds by asking clarifying questions (e.g., about scale, multi-tenancy, compliance) or generating a structured schema with Mermaid ERDs, the skill is active.

---

## Skill Contents

```text
database-design/
├── SKILL.md                    # Main skill instructions (1100+ lines)
├── README.md                   # This file
├── CHANGELOG.md                # Version history
└── scripts/
    ├── validate_schema.py      # Schema validation (15 rules, JSON output)
    └── seed_generator.sql      # Sample seed data template
```

---

## How It Works

| Phase | What happens |
|-------|-------------|
| **1. Gather Context** | Asks clarifying questions about database engine, scale, read/write patterns, and compliance if not provided. |
| **2. Design & Normalize** | Defines core entities, relationships, attributes, and data types with Primary and Foreign Keys. |
| **3. Indexing & Triggers** | Creates indexes for performance, explicit constraints, custom ENUM types, and auto-updating triggers. |
| **4. Security & Audit** | Applies Row-Level Security, database roles, data encryption templates, and audit logging tables. |
| **5. Migration & Output** | Structures the output strictly with `UP`/`DOWN` migrations, seed data, SQL schemas, and Mermaid ERDs. |

---

## Usage Examples

### Example 1: New Database (from scratch)

**Prompt:**

> Design a PostgreSQL database for a task management application:
> - Entities: User, Workspace, Project, Task, Label, Comment, Attachment
> - Relationships: User to Workspaces (N:M), Workspaces to Projects (1:N), etc.
> - Need audit trail, soft delete, and RLS.

**What you get:**

- A comprehensive set of schemas with correct types (`TIMESTAMPTZ`, `UUID`).
- Migrations inside `database/migrations/`.
- Appropriate indexes.
- Mermaid ERD in `database/ERD.md`.
- `sample_data.sql` and `sample_data.md` for seed data.

---

### Example 2: Review & Improve Existing Schema

**Prompt:**

> Review my existing database schema and suggest improvements based on production best practices. Check for missing indexes on foreign keys, proper use of TIMESTAMPTZ, and naming conventions. [paste schema]

**What you get:**

- An analysis of the provided schema pointing out anti-patterns.
- Refactored schema SQL following the skill's strict rules (snake_case, plural tables).
- Migration scripts to convert old schema to new safely.

---

### Example 3: SaaS Multi-Tenant Platform

**Prompt:**

> Design a multi-tenant PostgreSQL database for a B2B project management tool:
> - Tenants with plans (free, starter, pro, enterprise)
> - Users scoped to tenants, with roles
> - Use shared database with tenant_id + Row-Level Security

**What you get:**

- Complete schema using the `shared DB + tenant_id` pattern.
- RLS policies to isolate data so users only see their tenant's data.
- Migrations, table constraints, and sample seed inserts.

---

## Output Structure

The skill enforces the following directory structure when generating new schemas:

```text
project/
├── database/                    
│   ├── migrations/
│   │   ├── 001_initial_schema.up.sql
│   │   ├── 001_initial_schema.down.sql
│   ├── seeds/
│   │   ├── sample_data.md             # Usage of tables with raw data and description
│   │   └── sample_data.sql            # Raw data SQL inserts
│   ├── schema.sql
│   ├── ERD.md                     # Mermaid ERD (ALWAYS use Mermaid)
│   └── SCHEMA.md                  # Table documentation
└── README.md
```

---

## Validation Checks & Scripts

Run the Python validator against any SQL file:

```bash
# Validate a single file
python scripts/validate_schema.py schema.sql

# Validate all SQL files in a directory
python scripts/validate_schema.py --dir ./database/schema/

# JSON output (for CI/CD pipelines)
python scripts/validate_schema.py --json schema.sql

# Strict mode (warnings = errors)
python scripts/validate_schema.py --strict schema.sql
```

**15 rules checked**: PRIMARY KEY, ON DELETE, `created_at`, `TIMESTAMPTZ`, no FLOAT, FK indexes, soft delete, CHECK constraints, snake_case, transactions, no `SELECT *`, reserved words, updated_at triggers, status type safety, VARCHAR sizing.

---

## Seed Data Generation

Load the sample seed data into your database:

```bash
psql -d your_database -f scripts/seed_generator.sql
```

The included template demonstrates realistic seed data patterns with proper relationships, UUIDs, and verification queries. Customize it for your domain.

---

## Supported Platforms

| Platform | Status |
|---|---|
| Claude | ✅ |
| ChatGPT | ✅ |
| Gemini | ✅ |

---

## Requirements

- Python 3.10+ (for validator, no pip dependencies)
- PostgreSQL 14+ (recommended, for UUID v7, JSONB, RLS)
- MySQL 8.0+ (if using MySQL)
- MongoDB 6.0+ (if using MongoDB)

---

## License

MIT

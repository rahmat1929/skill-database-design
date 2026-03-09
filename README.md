# Database Design Skill

> Production-grade database schema design skill for AI coding assistants.
> Supports PostgreSQL, MySQL, MongoDB — native SQL, no ORM.

## 📁 Skill Contents

```
database-design/
├── SKILL.md                    # Main skill instructions (1100+ lines)
└── scripts/
    ├── validate_schema.py      # Schema validation (15 rules, JSON output)
    └── seed_generator.sql      # Sample seed data template
```

## 🚀 Quick Start

### Scenario A: New Database (from scratch)

Copy-paste one of these prompts to your AI assistant:

#### Prompt 1 — Minimal (AI will ask clarifying questions)

```
Design a database for my new application.
```

> The skill will trigger **Step 0: Requirements Gathering** and ask you:
> - What database engine? (PostgreSQL, MySQL, MongoDB)
> - Expected scale?
> - Multi-tenancy needed?
> - Compliance requirements?
> - etc.

#### Prompt 2 — Detailed (skip clarification, go straight to design)

```
Design a PostgreSQL database for a task management application:
- Entities: User, Workspace, Project, Task, Label, Comment, Attachment
- Relationships:
  - User belongs to many Workspaces (N:M with roles)
  - Workspace has many Projects
  - Project has many Tasks
  - Task can have Labels (N:M), Comments, Attachments
  - Tasks support subtasks (self-referencing)
- Expected: 100K users, 1M tasks/year
- Read-heavy (task lists, dashboard views)
- Need audit trail for task status changes
- Soft delete on all major entities
- Deploy on Supabase
- Include: schema SQL, indexes, triggers, RLS policies, migrations, seed data, ERD diagram
```

#### Prompt 3 — Content Platform

```
Design a PostgreSQL database for a blog/content platform:
- Entities: User, Post, Category (hierarchical), Tag, Comment, Media
- Posts can have multiple Tags (N:M)
- Comments support threading (nested replies)
- Full-text search on post title and body
- Soft delete on Users and Posts
- Generate migrations and seed data
```

#### Prompt 4 — SaaS Multi-Tenant

```
Design a multi-tenant PostgreSQL database for a B2B project management tool:
- Tenants with plans (free, starter, pro, enterprise)
- Users scoped to tenants, with roles (owner, admin, member, viewer)
- Projects, Tasks, Comments (threaded)
- Use shared database with tenant_id + Row-Level Security
- Include role-based DB access (read-only, read-write, admin)
```

---

### Scenario B: Existing Database / Project

#### Prompt 1 — Review & Improve Existing Schema

```
Review my existing database schema and suggest improvements based on
production best practices. Check for:
- Missing indexes on foreign keys
- Missing ON DELETE behavior
- Proper use of TIMESTAMPTZ vs TIMESTAMP
- Soft delete implementation
- Naming conventions (snake_case)
- Security (RLS, sensitive data handling)
- Performance (index strategy, EXPLAIN ANALYZE recommendations)

Here's my current schema:
[paste your schema.sql or point to the file]
```

#### Prompt 2 — Add Feature to Existing Schema

```
I have an existing application database (PostgreSQL) with these tables:
users, projects, tasks.

I need to ADD a notification system on top of it:
- Users receive notifications for task assignments, comments, due dates
- Support read/unread status per user
- Support notification preferences (email, push, in-app)
- Don't break existing tables, only add new ones + migrations

Generate:
1. New tables (migration UP + DOWN)
2. Triggers for auto notification creation
3. Seed data for testing
4. Updated ERD including existing tables
```

#### Prompt 3 — Migrate from MySQL to PostgreSQL

```
I'm migrating from MySQL to PostgreSQL. Here's my current MySQL schema:
[paste MySQL schema]

Convert it to PostgreSQL with these improvements:
- Replace ENUM strings with PostgreSQL custom types
- Replace TIMESTAMP with TIMESTAMPTZ
- Add proper indexes (MySQL auto-indexes FKs, PostgreSQL doesn't)
- Add RLS policies for multi-tenant tables
- Generate migration scripts
```

#### Prompt 4 — Performance Optimization

```
My PostgreSQL database has performance issues. Here are the slow queries:
[paste EXPLAIN ANALYZE output]

Current schema:
[paste schema]

Help me:
1. Identify missing or suboptimal indexes
2. Suggest schema changes for better query performance
3. Recommend partial indexes, covering indexes, or materialized views
4. Write the migration to apply changes safely (zero-downtime)
```

---

## 🛠️ Schema Validator

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

**15 rules checked**: PRIMARY KEY, ON DELETE, created_at, TIMESTAMPTZ, no FLOAT, FK indexes, soft delete, CHECK constraints, snake_case, transactions, no SELECT *, reserved words, updated_at triggers, status type safety, VARCHAR sizing.

---

## 🌱 Seed Data

Load the sample seed data into your database:

```bash
psql -d your_database -f scripts/seed_generator.sql
```

The included template demonstrates realistic seed data patterns with proper relationships, UUIDs, and verification queries. Customize it for your domain.

---

## 🔧 Supported Platforms

| Platform | Status |
|---|---|
| Claude | ✅ |
| ChatGPT | ✅ |
| Gemini | ✅ |

## 📋 Requirements

- Python 3.10+ (for validator, no pip dependencies)
- PostgreSQL 14+ (recommended, for UUID v7, JSONB, RLS)
- MySQL 8.0+ (if using MySQL)
- MongoDB 6.0+ (if using MongoDB)

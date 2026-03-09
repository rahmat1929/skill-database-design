# Changelog

All notable changes to the **database-design** skill.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.0] - 2026-03-09

### 🚀 New Skill — Complete Rewrite

This is a ground-up rewrite of the original `database-schema-design` skill (v1.0.0).

### Added

- **Bilingual support** — English + Bahasa Indonesia throughout
- **Platform support** — Claude, ChatGPT, Gemini
- **Step 0: Requirements Gathering** — 10 clarifying questions before design begins
- **Multi-tenancy patterns** — Shared DB with `tenant_id` + RLS, schema-per-tenant
- **Security hardening** — Row-Level Security (RLS), role-based DB access, PII encryption with pgcrypto
- **Audit & history tracking** — Generic audit_log table with trigger, SCD Type 2 tier history
- **ENUM & type safety** — PostgreSQL custom ENUMs, CHECK constraints for status fields
- **Advanced indexing** — Partial, covering, GIN, GiST, BRIN, expression indexes + EXPLAIN ANALYZE guide
- **Schema validation checklist** — 20-point machine-readable checklist
- **Zero-downtime migration patterns** — Batch backfill, add nullable→backfill→constrain pattern
- **Edge cases & anti-patterns** — 5 detailed anti-patterns with bad/good comparisons
- **Database-specific sections** — PostgreSQL (JSONB, CTEs, window functions), MySQL (InnoDB, ENUM differences), MongoDB (schema validation with JSON Schema)
- **Loyalty system example** — Full worked example with tiers, points, rewards, redemptions
- **SaaS multi-tenant example** — Workspace-scoped project management with RLS
- **Python schema validator** (`scripts/validate_schema.py`) — 15 rules, JSON output, CI/CD ready
- **Seed data generator** (`scripts/seed_generator.sql`) — Realistic loyalty system data

### Changed (vs v1.0.0 `database-schema-design`)

- **Language**: Korean → English + Bahasa Indonesia
- **Steps**: 5 → 8 (added requirements gathering, security, audit, improved migrations)
- **Examples**: 2 (blog, chat) → 3 (loyalty, e-commerce, SaaS)
- **Constraints section**: Expanded from 6 to 18 rules (9 MUST + 9 MUST NOT)
- **Index coverage**: Basic B-tree → 6 index types with EXPLAIN ANALYZE interpretation
- **Migration patterns**: Basic UP/DOWN → Zero-downtime with batch backfill
- **Validator**: Bash (10 rules) → Python (15 rules, JSON, CI/CD, directory scan)
- **Size**: 692 lines (20KB) → 1100+ lines (50KB)

### Removed

- Korean-only content (replaced with bilingual EN/ID)
- ORM references (skill is now native SQL only, by design)
- `validate_schema.sh` (replaced by `validate_schema.py`)

---

## [1.0.0] - 2025-01-01

### Initial Release (`database-schema-design`)

- Korean language only
- 5 steps: entities, relationships, indexes, constraints, migrations
- 2 examples: blog platform, real-time chat (MongoDB)
- Basic bash validator (10 rules)
- Platforms: Claude, ChatGPT, Gemini

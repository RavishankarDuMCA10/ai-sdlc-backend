All code should refer to the technical design in the [technical requirement document](https://github.com/RavishankarDuMCA10/ai-sdlc/tree/main/docs/trd).

The code standard:
- Use the python programming language
- Use PostgreSQL
- No ORD (Object Relational Mapping) framework
- Use REST API as a communication protocol
- Use Python-based migrations for any table DDL or data setup. Store them in separate migration files, following the rule of one table per migration file (including its indexes and constraints). Use a migration framework such as Alembic (commonly used with SQLAlchemy) to manage schema changes and data migrations.

Working process:
- Ensure to use a clean code approach
- Always create unit tests whenever possible
- Ensure the unit test passes before submitting a pull request
- Use conventional commit on pull request title

"""Migration Manager drafts database and API schema migrations.
"""

from typing import Optional

class LocalMigrationManager:
    """Creates schema upgrade/downgrade templates and API breaking changes plans."""

    def generate_migration_plan(self, database: Optional[str]) -> str:
        """Returns database migration plan templates."""
        db_type = database or "SQL"
        return f"""# Database Schema & API Migration Plan

## Database: {db_type}
- Target: Current production schema
- Action: Upgrade application package and run migration script

### Migration Execution Steps
1. Take schema backup.
2. Run migration script.
3. Validate API compatibility.

### SQL / Schema Change Script
```sql
-- Add migration queries here
-- ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
```

### Rollback (Downgrade) Script
```sql
-- Alter schema to revert columns
-- ALTER TABLE users DROP COLUMN last_login;
```
"""

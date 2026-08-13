"""Database Extractor Module.

Extracts ORM models, SQL tables, columns, relationships, indexes, and constraints.
"""

import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class DatabaseExtractor:
    """Enterprise ORM Model & Database Schema Extractor."""

    def __init__(self) -> None:
        logger.info("database_extractor_initialized")

    def extract_database_schemas(self, file_path: str, source_code: str) -> List[Dict[str, Any]]:
        """Extracts SQLAlchemy / Prisma / SQL database table definitions."""
        tables: List[Dict[str, Any]] = []

        # SQLAlchemy Table Definition: __tablename__ = "users"
        tbl_match = re.search(r'__tablename__\s*=\s*["\']([^"\']+)["\']', source_code)
        if tbl_match:
            table_name = tbl_match.group(1)
            columns = []
            for col_match in re.finditer(r'([A-Za-z0-9_]+)\s*=\s*Column\(\s*([A-Za-z0-9_]+)', source_code):
                columns.append({
                    "column_name": col_match.group(1),
                    "data_type": col_match.group(2),
                })
            tables.append({
                "table_name": table_name,
                "columns": columns,
                "file_path": file_path,
            })

        # SQL DDL CREATE TABLE statements
        for sql_match in re.finditer(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z0-9_]+)\s*\(([^;]+)\)', source_code, re.IGNORECASE):
            table_name = sql_match.group(1)
            raw_cols = sql_match.group(2)
            columns = [{"column_name": line.strip().split()[0]} for line in raw_cols.split(",") if line.strip()]
            tables.append({
                "table_name": table_name,
                "columns": columns,
                "file_path": file_path,
            })

        logger.info("database_tables_extracted", file_path=file_path, count=len(tables))
        return tables

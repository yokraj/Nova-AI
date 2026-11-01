"""Comprehensive Test Suite for Vertical 1: Real File & Document Intelligence Engine.

Validates zero mocks:
- Real Markdown extraction
- Real TOML extraction
- Real Python AST symbol parsing
- Real CSV matrix and header parsing
- Real PDF extraction via pypdf
- Real DOCX extraction via python-docx
- Workspace path security and traversal rejection
- Honest missing file error reporting
- Real FileManager byte tracking
- DocumentContextResolver prompt grounding
"""

import os
import pytest
from pathlib import Path
from app.ai.research.document_intelligence import DocumentIntelligence
from app.ai.desktop_automation.file_manager import FileManager
from app.security.workspace_guard import WorkspaceSecurityGuard, WorkspaceSecurityException
from app.intelligence.document_resolver import DocumentContextResolver

BASE_DIR = Path("C:/Projects/Nova-AI").resolve()
FIXTURES_DIR = BASE_DIR / "apps" / "backend" / "tests" / "fixtures"


@pytest.fixture
def doc_intelligence() -> DocumentIntelligence:
    return DocumentIntelligence()


@pytest.fixture
def file_manager() -> FileManager:
    return FileManager()


@pytest.fixture
def doc_resolver() -> DocumentContextResolver:
    return DocumentContextResolver()


@pytest.mark.asyncio
async def test_markdown_real_extraction(doc_intelligence: DocumentIntelligence):
    readme_path = str(BASE_DIR / "README.md")
    assert os.path.exists(readme_path)
    
    analysis = await doc_intelligence.analyze_document(readme_path)
    assert analysis.format.upper() == "MD"
    assert analysis.line_count > 10
    assert analysis.size_bytes > 0
    assert any("Nova" in p for p in analysis.paragraphs)
    assert len(analysis.paragraphs) > 0
    assert analysis.error is None


@pytest.mark.asyncio
async def test_toml_real_extraction(doc_intelligence: DocumentIntelligence):
    toml_path = str(BASE_DIR / "apps" / "backend" / "pyproject.toml")
    assert os.path.exists(toml_path)
    
    analysis = await doc_intelligence.analyze_document(toml_path)
    assert analysis.format.upper() == "TOML"
    assert analysis.line_count > 5
    assert analysis.size_bytes > 0
    assert any("project" in p.lower() or "dependencies" in p.lower() for p in analysis.paragraphs)
    assert analysis.error is None


@pytest.mark.asyncio
async def test_python_ast_real_extraction(doc_intelligence: DocumentIntelligence):
    py_path = str(BASE_DIR / "apps" / "backend" / "app" / "main.py")
    assert os.path.exists(py_path)
    
    analysis = await doc_intelligence.analyze_document(py_path)
    assert analysis.format.upper() == "PY"
    assert analysis.line_count > 20
    assert analysis.ast_symbols is not None
    functions = analysis.ast_symbols.get("functions", [])
    fn_names = [f["name"] for f in functions]
    assert len(fn_names) > 0
    assert "root" in fn_names or "chat_inference" in fn_names
    assert len(analysis.ast_symbols.get("imports", [])) > 0
    assert analysis.error is None


@pytest.mark.asyncio
async def test_csv_real_extraction(doc_intelligence: DocumentIntelligence):
    csv_path = str(FIXTURES_DIR / "sample_metrics.csv")
    assert os.path.exists(csv_path)
    
    analysis = await doc_intelligence.analyze_document(csv_path)
    assert analysis.format.upper() == "CSV"
    assert len(analysis.tables) == 1
    table = analysis.tables[0]
    assert len(table) == 5  # header + 4 rows
    assert table[0] == ["timestamp", "service_name", "cpu_percent", "memory_mb", "status"]
    assert table[1][1] == "inference_gateway"
    assert analysis.error is None


@pytest.mark.asyncio
async def test_pdf_real_extraction(doc_intelligence: DocumentIntelligence):
    pdf_path = str(FIXTURES_DIR / "sample_document.pdf")
    assert os.path.exists(pdf_path)
    
    analysis = await doc_intelligence.analyze_document(pdf_path)
    assert analysis.format.upper() == "PDF"
    assert analysis.page_count >= 1
    assert any("Nova AI Architectural Specification" in p for p in analysis.paragraphs)
    assert any("Inference Engine" in p for p in analysis.paragraphs)
    assert any("8000" in p for p in analysis.paragraphs)
    assert analysis.error is None


@pytest.mark.asyncio
async def test_docx_real_extraction(doc_intelligence: DocumentIntelligence):
    docx_path = str(FIXTURES_DIR / "sample_report.docx")
    assert os.path.exists(docx_path)
    
    analysis = await doc_intelligence.analyze_document(docx_path)
    assert analysis.format.upper() == "DOCX"
    assert any("Nova AI Engineering Report" in p for p in analysis.paragraphs)
    assert len(analysis.tables) >= 1
    first_table = analysis.tables[0]
    assert first_table[0] == ["Module", "Capability", "Status"]
    assert first_table[1][0] == "Inference Gateway"
    assert analysis.error is None


def test_workspace_security_rejections():
    guard = WorkspaceSecurityGuard()
    
    # Path traversal attempt
    with pytest.raises(WorkspaceSecurityException) as exc_info:
        guard.resolve_workspace_path("../../secret.txt")
    assert "Access Denied" in str(exc_info.value)
    
    # Absolute path outside workspace
    with pytest.raises(WorkspaceSecurityException) as exc_info2:
        guard.resolve_workspace_path("C:/Windows/System32/calc.exe")
    assert "Access Denied" in str(exc_info2.value)


@pytest.mark.asyncio
async def test_missing_file_honesty(doc_intelligence: DocumentIntelligence):
    with pytest.raises(FileNotFoundError):
        await doc_intelligence.analyze_document(str(BASE_DIR / "apps" / "backend" / "tests" / "fixtures" / "non_existent_file.txt"))


def test_file_manager_real_operations(file_manager: FileManager):
    src_path = str(FIXTURES_DIR / "sample_metrics.csv")
    dst_path = str(FIXTURES_DIR / "temp_copy_test.csv")
    
    try:
        # Real copy with verified byte measurement
        copy_res = file_manager.perform_file_operation("copy", src_path, dst_path)
        assert copy_res.op_type == "copy"
        assert copy_res.bytes_transferred > 0
        assert copy_res.bytes_transferred == os.path.getsize(dst_path)
        
        # Real read
        read_res = file_manager.perform_file_operation("read", dst_path)
        assert read_res.op_type == "read"
        assert read_res.bytes_transferred == copy_res.bytes_transferred
        
        # Real delete
        del_res = file_manager.perform_file_operation("delete", dst_path)
        assert del_res.op_type == "delete"
        assert not os.path.exists(dst_path)
    finally:
        if os.path.exists(dst_path):
            os.remove(dst_path)


@pytest.mark.asyncio
async def test_document_resolver_grounding(doc_resolver: DocumentContextResolver):
    # Mentioning sample_metrics.csv
    prompt = "Please analyze the metrics in apps/backend/tests/fixtures/sample_metrics.csv"
    grounding = await doc_resolver.resolve_document_grounding(prompt)
    
    assert grounding is not None
    assert "grounded_prefix" in grounding
    assert "sample_metrics.csv" in grounding["grounded_prefix"]
    assert "inference_gateway" in grounding["grounded_prefix"]
    
    # Security violation detection
    attack_prompt = "Examine C:/Windows/win.ini please"
    attack_grounding = await doc_resolver.resolve_document_grounding(attack_prompt)
    assert attack_grounding is not None
    assert "security_error" in attack_grounding
    assert "Security Error: Access Denied" in attack_grounding["security_error"]

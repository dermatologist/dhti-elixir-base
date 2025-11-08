import base64
import io
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from src.dhti_elixir_base.rag.process import (
    FileProcessingRequest,
    combine_documents,
    process_file,
    search_vectorstore,
)


# DummyDoc for mocking document objects
class DummyDoc:
    def __init__(self, page_content):
        self.page_content = page_content
        self.metadata = {}


def test_process_file_pdf(monkeypatch):
    # Prepare a fake PDF file (base64-encoded string ending with .pdf)
    fake_pdf_content = b"%PDF-1.4 fake pdf content"
    fake_pdf_b64 = base64.b64encode(fake_pdf_content).decode("utf-8") + ".pdf"

    # Patch get_di to return a dummy text_splitter
    class DummyTextSplitter:
        def create_documents(self, texts):
            return [DummyDoc(text) for text in texts]

    monkeypatch.setattr(
        "src.dhti_elixir_base.rag.process.get_di",
        lambda name, *_: DummyTextSplitter() if name == "text_splitter" else None,
    )

    # Patch PDFMinerParser to return a dummy document
    dummy_doc = DummyDoc("dummy page content")
    monkeypatch.setattr(
        "src.dhti_elixir_base.rag.process.PDFMinerParser",
        lambda: type("X", (), {"lazy_parse": lambda self, blob: [dummy_doc]})(),
    )

    req = FileProcessingRequest(file=fake_pdf_b64, filename="test.pdf", year=2025)
    result = process_file(req)
    assert "dummy page content" in result["text"]
    assert isinstance(result["documents"], list)
    assert result["documents"][0].metadata["filename"] == "test.pdf"
    assert result["documents"][0].metadata["year"] == 2025


def test_process_file_zip(monkeypatch):
    # Create a zip file in memory containing a PDF file
    pdf_bytes = b"%PDF-1.4 fake pdf content"
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w") as zf:
        zf.writestr("file1.pdf", pdf_bytes)
    mem_zip.seek(0)
    fake_zip_b64 = base64.b64encode(mem_zip.read()).decode("utf-8")

    class DummyTextSplitter:
        def create_documents(self, texts):
            return [DummyDoc(text) for text in texts]

    monkeypatch.setattr(
        "src.dhti_elixir_base.rag.process.get_di",
        lambda name, *_: DummyTextSplitter() if name == "text_splitter" else None,
    )
    dummy_doc = DummyDoc("dummy page content from zip")

    # Use patch as context manager to ensure correct patching
    with patch(
        "src.dhti_elixir_base.rag.process.PDFMinerParser",
        return_value=type("X", (), {"lazy_parse": lambda self, blob: [dummy_doc]})(),
    ):
        req = FileProcessingRequest(
            file=fake_zip_b64, filename="archive.zip", year=2024
        )
        result = process_file(req)
        assert "dummy page content from zip" in result["text"]
        assert isinstance(result["documents"], list)
        assert result["documents"][0].metadata["filename"] == "archive.zip"
        assert result["documents"][0].metadata["year"] == 2024


def test_combine_documents():
    docs = [DummyDoc("page 1"), DummyDoc("page 2")]
    combined = combine_documents(docs, document_separator="\n---\n")
    assert "page 1" in combined and "page 2" in combined
    # combine_documents adds a separator after every document, so for two docs, expect two separators
    assert combined.count("---") == 2

    # Test empty input
    assert (
        combine_documents([])
        == "No information found. The vectorstore may still be indexing. Please try again later."
    )


def test_search_vectorstore(monkeypatch):
    # Patch get_di to return a dummy vectorstore retriever
    class DummyRetriever:
        def get_relevant_documents(self, query, k=5):
            return [DummyDoc(f"result for {query}")]

    class DummyVectorStore:
        def as_retriever(self):
            return DummyRetriever()

    def fake_get_di(name, *args, **kwargs):
        if name == "vectorstore":
            return DummyVectorStore()
        if name == "rag_k":
            return 3
        return None

    monkeypatch.setattr("src.dhti_elixir_base.rag.process.get_di", fake_get_di)
    results = search_vectorstore("test query")
    assert isinstance(results, list)
    assert "result for test query" in results[0].page_content

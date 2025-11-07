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


class DummyDoc:
    def __init__(self, page_content):
        self.page_content = page_content
        self.metadata = {}


class DummyTextSplitter:
    def create_documents(self, texts):
        # Return DummyDoc objects for each text
        return [DummyDoc(text) for text in texts]


@pytest.fixture
def pdf_bytes():
    # Minimal PDF file bytes
    return b"%PDF-1.4\n%EOF"


@pytest.fixture
def base64_pdf(pdf_bytes):
    return base64.b64encode(pdf_bytes).decode("utf-8")


@pytest.fixture
def base64_zip_with_pdf(pdf_bytes):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("test.pdf", pdf_bytes)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def test_process_file_single_pdf(monkeypatch, base64_pdf):
    # Patch PDFMinerParser in the correct namespace to avoid PDFMiner usage
    with patch(
        "src.dhti_elixir_base.rag.process.PDFMinerParser",
        return_value=MagicMock(lazy_parse=lambda blob: [DummyDoc("PDF content")]),
    ):
        request = FileProcessingRequest(
            file=base64_pdf + ".pdf", filename="file.pdf", year=2024
        )
        text_splitter = DummyTextSplitter()
        text, docs = process_file(request, text_splitter)
        assert "PDF content" in text
        assert len(docs) == 1
        assert docs[0].metadata["filename"] == "file.pdf"
        assert docs[0].metadata["year"] == 2024


def test_process_file_zip_with_pdf(monkeypatch, base64_zip_with_pdf):
    # Patch PDFMinerParser in the correct namespace to avoid PDFMiner usage
    with patch(
        "src.dhti_elixir_base.rag.process.PDFMinerParser",
        return_value=MagicMock(
            lazy_parse=lambda blob: [DummyDoc("Zipped PDF content")]
        ),
    ):
        request = FileProcessingRequest(
            file=base64_zip_with_pdf + ".zip", filename="archive.zip", year=2023
        )
        text_splitter = DummyTextSplitter()
        text, docs = process_file(request, text_splitter)
        assert "Zipped PDF content" in text
        assert len(docs) == 1
        assert docs[0].metadata["filename"] == "archive.zip"
        assert docs[0].metadata["year"] == 2023


def test_combine_documents_returns_combined_text():
    docs = [DummyDoc("Doc1"), DummyDoc("Doc2")]
    result = combine_documents(docs, document_separator="|")
    assert "Doc1" in result and "Doc2" in result
    assert "|" in result


def test_combine_documents_returns_no_info_for_empty():
    result = combine_documents([])
    assert "No information found" in result


def test_search_vectorstore_calls_retriever():
    mock_retriever = MagicMock()
    mock_retriever.get_relevant_documents.return_value = ["doc1", "doc2"]
    mock_query_engine = MagicMock()
    mock_query_engine.as_retriever.return_value = mock_retriever
    result = search_vectorstore(mock_query_engine, "query", k=2)
    assert result == ["doc1", "doc2"]
    mock_retriever.get_relevant_documents.assert_called_once_with("query", k=2)

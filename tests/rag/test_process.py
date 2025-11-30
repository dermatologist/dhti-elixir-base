import base64
from unittest.mock import MagicMock

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


def test_process_file_extracts_text_and_adds_to_vectorstore(monkeypatch):
    fake_pdf_content = b"%PDF-1.4 fake pdf content"
    fake_b64 = base64.b64encode(fake_pdf_content).decode("utf-8")
    request = FileProcessingRequest(file=fake_b64, filename="test.pdf", year=2025)

    class DummyParser:
        def lazy_parse(self, blob):
            return [DummyDoc("page1 content")]

    monkeypatch.setattr("src.dhti_elixir_base.rag.process.PDFMinerParser", DummyParser)

    dummy_splitter = MagicMock()
    dummy_splitter.create_documents.return_value = [DummyDoc("split content")]
    dummy_vectorstore = MagicMock()
    monkeypatch.setattr(
        "src.dhti_elixir_base.rag.process.get_di",
        lambda name, *args, **kwargs: (
            dummy_splitter if name == "text_splitter" else dummy_vectorstore
        ),
    )

    result = process_file(request)
    assert "page1 content" in result
    dummy_vectorstore.add_documents.assert_called()


def test_process_file_handles_vectorstore_exception(monkeypatch, caplog):
    fake_pdf_content = b"%PDF-1.4 fake pdf content"
    fake_b64 = base64.b64encode(fake_pdf_content).decode("utf-8")
    request = FileProcessingRequest(file=fake_b64, filename="test.pdf", year=2025)

    class DummyParser:
        def lazy_parse(self, blob):
            return [DummyDoc("page1 content")]

    monkeypatch.setattr("src.dhti_elixir_base.rag.process.PDFMinerParser", DummyParser)

    dummy_splitter = MagicMock()
    dummy_splitter.create_documents.return_value = [DummyDoc("split content")]
    dummy_vectorstore = MagicMock()
    dummy_vectorstore.add_documents.side_effect = Exception("vectorstore error")
    monkeypatch.setattr(
        "src.dhti_elixir_base.rag.process.get_di",
        lambda name, *args, **kwargs: (
            dummy_splitter if name == "text_splitter" else dummy_vectorstore
        ),
    )

    with caplog.at_level("ERROR"):
        result = process_file(request)
        assert "Error adding documents" in result



def test_combine_documents_returns_combined_text():
    docs = [DummyDoc("foo"), DummyDoc("bar")]
    combined = combine_documents(docs, document_separator="\n")
    assert "foo" in combined and "bar" in combined
    assert combined.count("foo") == 1


def test_combine_documents_returns_no_info_for_empty():
    combined = combine_documents([])
    assert "No information found" in combined


def test_search_vectorstore(monkeypatch):
    dummy_vectorstore = MagicMock()
    dummy_vectorstore.similarity_search.return_value = ["doc1", "doc2"]
    monkeypatch.setattr(
        "src.dhti_elixir_base.rag.process.get_di",
        lambda name, *args, **kwargs: dummy_vectorstore if name == "vectorstore" else 2,
    )
    result = search_vectorstore("query")
    assert result == ["doc1", "doc2"]

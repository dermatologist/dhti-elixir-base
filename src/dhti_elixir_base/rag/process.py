"""
Copyright 2025 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64
import logging

from langchain_community.document_loaders.parsers.pdf import PDFMinerParser
from langchain_core.document_loaders import Blob
from langchain_core.prompts import PromptTemplate
from langserve import CustomUserType
from pydantic import Field

from ..mydi import get_di

logger = logging.getLogger(__name__)


# *  Inherit from CustomUserType instead of BaseModel otherwise
#    the server will decode it into a dict instead of a pydantic model.
class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    # The extra field is used to specify a widget for the playground UI.
    file: str = Field(..., extra={"widget": {"type": "base64file"}})  # type: ignore
    filename: str = Field(
        default="", json_schema_extra={"widget": {"type": "text"}}
    )
    year: int = Field(
        default=0,
        json_schema_extra={"widget": {"type": "number"}},
    )


def process_file(request: FileProcessingRequest) -> str:
    """Extract the text from all pages of the PDF."""
    content = base64.b64decode(request.file.encode("utf-8"))
    blob = Blob(data=content)
    documents = list(PDFMinerParser().lazy_parse(blob))
    # Use list and join for O(n) instead of repeated string concatenation O(n²)
    page_contents = [doc.page_content for doc in documents]
    pages = "".join(page_contents)
    docs = get_di("text_splitter").create_documents([pages]) # type: ignore
    metadata = {"filename": request.filename, "year": request.year}
    _docs = []
    for doc in docs:
        doc.metadata = metadata
        _docs.append(doc)
    try:
        get_di("vectorstore").add_documents(_docs) # type: ignore
    except Exception as e:
        return f"Error adding documents to vectorstore: {e}"
    # return first 100 characters of the extracted text
    return pages[:100]


def combine_documents(documents: list, document_separator="\n\n") -> str:
    """Combine documents into a single string."""
    # Use list and join for O(n) instead of repeated string concatenation O(n²)
    parts = []
    DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}\n")
    for document in documents:
        filename = document.metadata.get("filename", "")
        year = document.metadata.get("year", 0)
        current_separator = f"[{filename} ({year})]\n\n" if filename and year else document_separator
        parts.append(
            DEFAULT_DOCUMENT_PROMPT.format(page_content=document.page_content)
            + current_separator
        )
    combined_text = "".join(parts)
    if len(combined_text) < 3:
        return "No information found. The vectorstore may still be indexing. Please try again later."
    return combined_text.strip()


def search_vectorstore(query: str) -> list:
    """Search the vectorstore for the given query."""
    vectorstore = get_di("vectorstore")
    return vectorstore.similarity_search(query, k=get_di("rag_k", 5))  # type: ignore

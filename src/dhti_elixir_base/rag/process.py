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
import io
import zipfile
import datetime
from langchain_community.document_loaders.parsers.pdf import PDFMinerParser
from langchain_core.document_loaders import Blob
from langserve import CustomUserType
from pydantic import Field
from langchain.schema import format_document
from langchain.prompts.prompt import PromptTemplate

# *  Inherit from CustomUserType instead of BaseModel otherwise
#    the server will decode it into a dict instead of a pydantic model.
class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    # The extra field is used to specify a widget for the playground UI.
    file: str = Field(..., json_schema_extra={"widget": {"type": "base64file"}})
    filename: str = Field(
        default="UNKNOWN", json_schema_extra={"widget": {"type": "text"}}
    )
    year: int = Field(
        default_factory=lambda: datetime.datetime.now().year,
        json_schema_extra={"widget": {"type": "number"}},
    )


def process_file(request: FileProcessingRequest, text_splitter) -> tuple[str, list]:
    """Extract text from all pages of PDF file(s) and split into chunks."""
    # if request.file is a single PDF file
    # if file has .pdf extension
    contents = []
    if request.file.endswith(".pdf"):
        content = base64.b64decode(request.file.encode("utf-8"))
        contents.append(content)
    # if request.file is a zip file containing multiple PDFs,
    # we need to extract the PDFs from the zip file
    if request.file.endswith(".zip"):
        zip_content = base64.b64decode(request.file.encode("utf-8"))
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for filename in z.namelist():
                if filename.endswith(".pdf"):
                    content = z.read(filename)
                    contents.append(content)

    text = ""
    docs = []
    for content in contents:
        blob = Blob(data=content)
        documents = list(PDFMinerParser().lazy_parse(blob))
        doc_text = ""
        for doc in documents:
            doc_text += doc.page_content
        text += doc_text + "\n"
        split_docs = text_splitter.create_documents([doc_text])
        metadata = {"filename": request.filename, "year": request.year}
        for doc in split_docs:
            doc.metadata = metadata
            docs.append(doc)
    return text, docs


def combine_documents(documents: list, document_separator="\n\n") -> str:
    """Combine documents into a single string."""
    combined_text = ""
    DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}\n")
    for document in documents:
        combined_text += format_document(document, DEFAULT_DOCUMENT_PROMPT) + document_separator
    if len(combined_text) < 3:
        return "No information found. The vectorstore may still be indexing. Please try again later."
    return combined_text.strip()


def search_vectorstore(query_engine, query: str, k: int) -> list:
    """Search the vectorstore for the given query."""
    return query_engine.as_retriever().get_relevant_documents(query, k=k)

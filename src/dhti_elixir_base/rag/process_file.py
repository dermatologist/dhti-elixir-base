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
import datetime
from langchain_community.document_loaders.parsers.pdf import PDFMinerParser
from langchain_core.document_loaders import Blob
from langserve import CustomUserType
from pydantic import Field

# *  Inherit from CustomUserType instead of BaseModel otherwise
#    the server will decode it into a dict instead of a pydantic model.
class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    # The extra field is used to specify a widget for the playground UI.
    file: str = Field(..., json_schema_extra={"widget": {"type": "base64file"}})
    authors: str = Field(
        default="UNKNOWN", json_schema_extra={"widget": {"type": "text"}}
    )
    year: int = Field(
        default_factory=lambda: datetime.datetime.now().year,
        json_schema_extra={"widget": {"type": "number"}},
    )


def process_file(request: FileProcessingRequest, text_splitter) -> tuple[str, list]:
    """Extract the text from the first page of the PDF."""
    content = base64.b64decode(request.file.encode("utf-8"))
    blob = Blob(data=content)
    documents = list(PDFMinerParser().lazy_parse(blob))
    text = ""
    for doc in documents:
        text += doc.page_content
    docs = text_splitter.create_documents([text])
    metadata = {"authors": request.authors, "year": request.year}
    docs = []
    for doc in docs:
        doc.page_content = doc.page_content
        doc.metadata = metadata
        docs.append(doc)
    return text, docs

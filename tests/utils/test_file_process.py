# Unit tests for FileProcessingRequest in file_process.py
import pytest
from pydantic import ValidationError

from src.dhti_elixir_base.utils.file_process import FileProcessingRequest


def test_file_processing_request_valid():
    # Valid base64 string and prompt
    req = FileProcessingRequest(file="dGVzdA==", prompt="Test prompt")
    assert req.file == "dGVzdA=="
    assert req.prompt == "Test prompt"


def test_file_processing_request_missing_file():
    # Missing 'file' field should raise ValidationError
    with pytest.raises(ValidationError):
        FileProcessingRequest(prompt="Test prompt")


def test_file_processing_request_missing_prompt():
    # Missing 'prompt' field should raise ValidationError
    with pytest.raises(ValidationError):
        FileProcessingRequest(file="dGVzdA==")


def test_file_processing_request_wrong_type():
    # Non-string types for fields should raise ValidationError
    with pytest.raises(ValidationError):
        FileProcessingRequest(file=123, prompt="Test prompt")
    with pytest.raises(ValidationError):
        FileProcessingRequest(file="dGVzdA==", prompt=456)

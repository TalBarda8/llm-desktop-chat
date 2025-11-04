"""
Unit tests for OllamaClient class
"""
import pytest
import json
from unittest.mock import Mock, patch
from src.api.ollama_client import OllamaClient
from src.utils.exceptions import OllamaConnectionError


class TestOllamaClient:
    """Test cases for OllamaClient class"""

    @pytest.fixture
    def client(self):
        """Create an OllamaClient instance"""
        return OllamaClient(base_url="http://localhost:11434")

    def test_initialization(self, client):
        """Test OllamaClient initializes correctly"""
        assert client.base_url == "http://localhost:11434"
        assert client.client is not None

    def test_initialization_strips_trailing_slash(self):
        """Test that trailing slash is removed from base_url"""
        client = OllamaClient(base_url="http://localhost:11434/")
        assert client.base_url == "http://localhost:11434"

    @patch('src.api.ollama_client.httpx.Client')
    def test_check_connection_success(self, mock_client_class):
        """Test successful connection check"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        result = client.check_connection()

        assert result is True
        mock_http_client.get.assert_called_once_with("http://localhost:11434/api/tags")

    @patch('src.api.ollama_client.httpx.Client')
    def test_check_connection_failure(self, mock_client_class):
        """Test connection check failure"""
        mock_http_client = Mock()
        mock_http_client.get.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        result = client.check_connection()

        assert result is False

    @patch('src.api.ollama_client.httpx.Client')
    def test_list_models_success(self, mock_client_class):
        """Test successful model listing"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2"},
                {"name": "mistral"},
                {"name": "codellama"}
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        models = client.list_models()

        assert len(models) == 3
        assert "llama2" in models
        assert "mistral" in models
        assert "codellama" in models

    @patch('src.api.ollama_client.httpx.Client')
    def test_list_models_empty(self, mock_client_class):
        """Test listing models when none available"""
        mock_response = Mock()
        mock_response.json.return_value = {"models": []}
        mock_response.raise_for_status = Mock()

        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        models = client.list_models()

        assert len(models) == 0

    @patch('src.api.ollama_client.httpx.Client')
    def test_list_models_http_error(self, mock_client_class):
        """Test list_models raises exception on HTTP error"""
        import httpx

        mock_http_client = Mock()
        mock_http_client.get.side_effect = httpx.HTTPError("Connection failed")
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()

        with pytest.raises(OllamaConnectionError, match="Failed to list models"):
            client.list_models()

    @patch('src.api.ollama_client.httpx.Client')
    def test_generate_stream_success(self, mock_client_class):
        """Test successful streaming generation"""
        # Mock streaming response
        mock_lines = [
            json.dumps({"message": {"content": "Hello"}, "done": False}),
            json.dumps({"message": {"content": " "}, "done": False}),
            json.dumps({"message": {"content": "World"}, "done": False}),
            json.dumps({"message": {"content": ""}, "done": True})
        ]

        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(mock_lines)
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=False)

        mock_http_client = Mock()
        mock_http_client.stream.return_value = mock_stream_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        chunks = list(client.generate_stream("llama2", messages))

        assert chunks == ["Hello", " ", "World"]
        mock_http_client.stream.assert_called_once()

    @patch('src.api.ollama_client.httpx.Client')
    def test_generate_stream_with_empty_content(self, mock_client_class):
        """Test streaming handles empty content chunks"""
        mock_lines = [
            json.dumps({"message": {"content": "Hello"}, "done": False}),
            json.dumps({"message": {"content": ""}, "done": False}),  # Empty content
            json.dumps({"message": {"content": "World"}, "done": False}),
            json.dumps({"message": {"content": ""}, "done": True})
        ]

        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(mock_lines)
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=False)

        mock_http_client = Mock()
        mock_http_client.stream.return_value = mock_stream_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        chunks = list(client.generate_stream("llama2", messages))

        # Empty content chunks should be filtered out
        assert chunks == ["Hello", "World"]

    @patch('src.api.ollama_client.httpx.Client')
    def test_generate_stream_invalid_json(self, mock_client_class):
        """Test streaming handles invalid JSON gracefully"""
        mock_lines = [
            json.dumps({"message": {"content": "Hello"}, "done": False}),
            "invalid json",  # Invalid line
            json.dumps({"message": {"content": "World"}, "done": False}),
            json.dumps({"message": {"content": ""}, "done": True})
        ]

        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(mock_lines)
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=False)

        mock_http_client = Mock()
        mock_http_client.stream.return_value = mock_stream_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        chunks = list(client.generate_stream("llama2", messages))

        # Should skip invalid JSON and continue
        assert chunks == ["Hello", "World"]

    @patch('src.api.ollama_client.httpx.Client')
    def test_generate_stream_http_error(self, mock_client_class):
        """Test generate_stream raises exception on HTTP error"""
        import httpx

        mock_stream_response = Mock()
        mock_stream_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=Mock(), response=Mock()
        )
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=False)

        mock_http_client = Mock()
        mock_http_client.stream.return_value = mock_stream_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        with pytest.raises(OllamaConnectionError, match="Streaming failed"):
            list(client.generate_stream("llama2", messages))

    @patch('src.api.ollama_client.httpx.Client')
    def test_generate_stream_request_payload(self, mock_client_class):
        """Test generate_stream sends correct request payload"""
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter([
            json.dumps({"message": {"content": "Hi"}, "done": True})
        ])
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=False)

        mock_http_client = Mock()
        mock_http_client.stream.return_value = mock_stream_response
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]

        list(client.generate_stream("mistral", messages))

        # Verify the request payload
        call_args = mock_http_client.stream.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "http://localhost:11434/api/chat"

        json_payload = call_args[1]["json"]
        assert json_payload["model"] == "mistral"
        assert json_payload["messages"] == messages
        assert json_payload["stream"] is True

    @patch('src.api.ollama_client.httpx.Client')
    def test_close_connection(self, mock_client_class):
        """Test closing the client connection"""
        mock_http_client = Mock()
        mock_client_class.return_value = mock_http_client

        client = OllamaClient()
        client.close()

        mock_http_client.close.assert_called_once()


# Run tests with: pytest tests/test_ollama_client.py -v

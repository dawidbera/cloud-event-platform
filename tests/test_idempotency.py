import pytest
from unittest.mock import MagicMock, patch
from shared.kafka.idempotency import IdempotencyManager

@pytest.fixture
def mock_redis():
    with patch("shared.kafka.idempotency.redis.from_url") as mock_from_url:
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        yield mock_client

def test_idempotency_new_event(mock_redis):
    # Setup
    manager = IdempotencyManager("redis://localhost:6379/0")
    # set returns True when nx=True and key is new
    mock_redis.set.return_value = True
    
    # Act
    is_processed = manager.is_processed("event-123")
    
    # Assert
    assert is_processed is False
    mock_redis.set.assert_called_once_with(
        "idempotency:event:event-123", "PROCESSING", nx=True, ex=manager.ttl
    )

def test_idempotency_duplicate_event(mock_redis):
    # Setup
    manager = IdempotencyManager("redis://localhost:6379/0")
    # set returns None/False when nx=True and key exists
    mock_redis.set.return_value = False
    
    # Act
    is_processed = manager.is_processed("event-123")
    
    # Assert
    assert is_processed is True
    mock_redis.set.assert_called_once_with(
        "idempotency:event:event-123", "PROCESSING", nx=True, ex=manager.ttl
    )

def test_idempotency_mark_completed(mock_redis):
    manager = IdempotencyManager("redis://localhost:6379/0")
    manager.mark_completed("event-123")
    
    mock_redis.set.assert_called_once_with(
        "idempotency:event:event-123", "COMPLETED", ex=manager.ttl
    )

def test_idempotency_mark_failed(mock_redis):
    manager = IdempotencyManager("redis://localhost:6379/0")
    manager.mark_failed("event-123")
    
    mock_redis.delete.assert_called_once_with("idempotency:event:event-123")

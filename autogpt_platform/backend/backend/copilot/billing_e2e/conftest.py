"""The fake provider and the platform ledger each billing scenario runs on."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from .ledger import PlatformLedger
from .provider import FakeProvider


@pytest_asyncio.fixture(loop_scope="function")
async def provider() -> AsyncIterator[FakeProvider]:
    async with FakeProvider() as fake:
        yield fake


@pytest.fixture
def ledger(monkeypatch: pytest.MonkeyPatch) -> PlatformLedger:
    ledger = PlatformLedger()
    ledger.install(monkeypatch)
    return ledger


@pytest.fixture(autouse=True)
def _no_memory(mocker):
    """No billing turn reads or writes Graphiti memory. A turn's memory write
    otherwise starts a background ingestion worker whose LLM calls fail
    without credentials, and the test waits out the worker's idle timeout
    (``graphiti.ingest._WORKER_IDLE_TIMEOUT``, 60 s) on Python 3.11."""
    for module in ("backend.copilot.sdk.service", "backend.copilot.baseline.service"):
        mocker.patch(f"{module}.enqueue_conversation_turn", new=mocker.AsyncMock())
        mocker.patch(
            f"{module}.fetch_warm_context", new=mocker.AsyncMock(return_value="")
        )

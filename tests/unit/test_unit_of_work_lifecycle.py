import pytest

from app.persistence.unit_of_work import SqlAlchemyUnitOfWork


class FakeSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1

    async def close(self) -> None:
        self.closes += 1


@pytest.mark.asyncio
async def test_uncommitted_exit_rolls_back_and_closes() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        _ = uow.system_state

    assert session.rollbacks == 1
    assert session.closes == 1


@pytest.mark.asyncio
async def test_explicit_commit_commits_and_closes() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        await uow.commit()

    assert session.commits == 1
    assert session.closes == 1


@pytest.mark.asyncio
async def test_exception_exit_rolls_back() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    with pytest.raises(RuntimeError):
        async with uow:
            raise RuntimeError("boom")

    assert session.rollbacks == 1
    assert session.closes == 1


@pytest.mark.asyncio
async def test_repository_access_after_exit_fails() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        _ = uow.audit_logs
        _ = uow.candles
        _ = uow.economic_events

    with pytest.raises(RuntimeError):
        _ = uow.audit_logs
    with pytest.raises(RuntimeError):
        _ = uow.candles
    with pytest.raises(RuntimeError):
        _ = uow.economic_events


@pytest.mark.asyncio
async def test_repeated_active_entry_is_rejected() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        with pytest.raises(RuntimeError):
            await uow.__aenter__()


@pytest.mark.asyncio
async def test_work_after_commit_before_exception_rolls_back_open_transaction() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async def commit_then_fail() -> None:
        async with uow:
            await uow.commit()
            _ = uow.system_state
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await commit_then_fail()

    assert session.commits == 1
    assert session.rollbacks == 1
    assert session.closes == 1

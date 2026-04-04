import asyncio

from rpg_narrative_server.infrastructure.runtime.message_runtime import MessageRuntime


def test_check_cooldown_allows_first_call(monkeypatch):
    runtime = MessageRuntime()

    monkeypatch.setattr("time.time", lambda: 100)

    assert runtime.check_cooldown("user1", seconds=10) is True


def test_check_cooldown_blocks_within_window(monkeypatch):
    runtime = MessageRuntime()

    times = [100, 105]

    monkeypatch.setattr("time.time", lambda: times.pop(0))

    assert runtime.check_cooldown("user1", 10) is True
    assert runtime.check_cooldown("user1", 10) is False


def test_check_cooldown_allows_after_window(monkeypatch):
    runtime = MessageRuntime()

    times = [100, 120]

    monkeypatch.setattr("time.time", lambda: times.pop(0))

    assert runtime.check_cooldown("user1", 10) is True
    assert runtime.check_cooldown("user1", 10) is True


def test_should_warn_first_time(monkeypatch):
    runtime = MessageRuntime()

    monkeypatch.setattr("time.time", lambda: 100)

    assert runtime.should_warn("channel1", debounce=10) is True


def test_should_warn_blocked(monkeypatch):
    runtime = MessageRuntime()

    times = [100, 105]

    monkeypatch.setattr("time.time", lambda: times.pop(0))

    assert runtime.should_warn("channel1", 10) is True
    assert runtime.should_warn("channel1", 10) is False


def test_should_warn_after_debounce(monkeypatch):
    runtime = MessageRuntime()

    times = [100, 120]

    monkeypatch.setattr("time.time", lambda: times.pop(0))

    assert runtime.should_warn("channel1", 10) is True
    assert runtime.should_warn("channel1", 10) is True


def test_get_lock_creates_lock():
    runtime = MessageRuntime()

    lock = runtime.get_lock("channel1")

    assert isinstance(lock, asyncio.Lock)


def test_get_lock_reuses_same_instance():
    runtime = MessageRuntime()

    lock1 = runtime.get_lock("channel1")
    lock2 = runtime.get_lock("channel1")

    assert lock1 is lock2


def test_get_lock_different_channels():
    runtime = MessageRuntime()

    lock1 = runtime.get_lock("channel1")
    lock2 = runtime.get_lock("channel2")

    assert lock1 is not lock2

from unittest.mock import patch

from murmur_core.injection import YdotoolInjector


def test_ydotool_injector_uses_stdin_and_socket_env():
    injector = YdotoolInjector("/tmp/murmur-test.sock", key_delay="2", key_hold="3")
    with patch("murmur_core.injection.subprocess.run") as run:
        run.return_value.returncode = 0
        result = injector.insert("hello", trailing_space=True)

    assert result.ok
    args, kwargs = run.call_args
    assert args[0][:3] == ["ydotool", "type", "-d"]
    assert kwargs["input"] == b"hello "
    assert kwargs["env"]["YDOTOOL_SOCKET"] == "/tmp/murmur-test.sock"

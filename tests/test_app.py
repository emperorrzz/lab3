import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"


def run_cli(*args, input=None):
    return subprocess.run(
        [sys.executable, str(APP), *args], input=input,
        capture_output=True, text=True, encoding="utf-8",
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
        timeout=10,
    )


def test_calculation():
    result = run_cli("--amount", "120000", "--rate", "0", "--years", "1")
    assert result.returncode == 0
    assert "10000.00" in result.stdout
    assert "120000.00" in result.stdout


def test_interactive_input():
    result = run_cli(input="120000\n0\n1\n")
    assert result.returncode == 0
    assert "10000.00" in result.stdout


def test_invalid_amount():
    assert run_cli("--amount", "-1", "--rate", "12", "--years", "20").returncode == 2


def test_invalid_number():
    assert run_cli("--amount", "abc").returncode == 2


def test_fractional_years():
    assert run_cli("--amount", "100000", "--rate", "12", "--years", "1.5").returncode == 2


def test_version():
    result = run_cli("--version")
    assert result.returncode == 0
    assert result.stdout.strip()


def test_missing_input_does_not_hang():
    assert run_cli(input="").returncode == 2

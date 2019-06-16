import pathlib
import subprocess
import sys


pip_bin = pathlib.Path(sys.executable).parent / "pip3"


def is_venv():
    if hasattr(sys, "real_prefix"):
        return True
    if hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix:
        return True
    return False


def install(package, *, user=False, upgrade=False):
    command = [pip_bin, "--disable-pip-version-check", "install", package]
    if upgrade:
        command.append("--upgrade")
    if user:
        command.append("--user")
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b""):
        yield line.decode("utf-8").rstrip()


def uninstall(package):
    command = [pip_bin, "--disable-pip-version-check", "uninstall", "-y", package]
    output = subprocess.check_output(command)
    return output.decode("utf-8").rstrip()


def installed(*, user=False):
    command = [pip_bin, "--disable-pip-version-check", "list"]
    if user:
        command.append("--user")
    output = subprocess.check_output(command)
    output = output.decode("utf-8").rstrip()
    lines = output.split("\n")[2:]
    return [l.split(" ")[0].strip().lower() for l in lines]

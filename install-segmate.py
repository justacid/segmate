import os
import pathlib
import platform
import shutil
import sys
import subprocess
import urllib.request
import venv
import zipfile


version = "0.10.1"
download_url = "https://github.com/justacid/segmate/archive/{0}.zip".format(version)
filename = "{0}.zip".format(version)

desktop_file = """
[Desktop Entry]
Version={0}
Type=Application
Name=Segmate
Comment=Semantic segmentation annotation tool
Exec={1}
Icon={2}
Terminal=false
Categories=Development;Education;Science;
"""

vbs_shortcut = \
"""Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{0}"
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{1}"
    oLink.Description = "Segmate semantic annotation tool"
    oLink.IconLocation = "{2}"
oLink.Save
"""

def get_data_dir():
    if platform.system() == "Darwin":
        raise NotImplementedError()
    if platform.system() == "Windows":
        return pathlib.Path(os.path.expandvars(r"%appdata%")) / "segmate"
    if platform.system() == "Linux":
        return os.environ.get("XDG_DATA_HOME",
                              pathlib.Path("~/.local/share/segmate").expanduser())

def pip_install(data_dir, package=None, *, use_requirements=False):
    if platform.system() == "Windows":
        pip_path = str(data_dir / "segmate" / "Scripts" / "pip")
    else:
        pip_path = str(data_dir / "segmate" / "bin" / "pip")
    command = [pip_path, "--disable-pip-version-check", "install"]
    if use_requirements:
        req_file = str(data_dir / version / "segmate-{0}".format(version) / "requirements.txt")
        command.extend(["-r", req_file])
    else:
        command.append(str(package))
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b""):
        print(line.decode("utf-8").rstrip())


def create_desktop_file(data_dir):
    d_path = pathlib.Path("~/.local/share/applications/segmate.desktop").expanduser()
    bin_path = data_dir / "segmate" / "bin" / "segmate"
    pyvers = "python{0}.{1}".format(sys.version_info[0], sys.version_info[1])
    icon_path = data_dir / "segmate" / "lib" / pyvers / \
                "site-packages" / "segmate" / "icons" / "app-icon.png"
    with open(d_path, "w") as df:
        df.write(desktop_file.format(version, str(bin_path), str(icon_path)))


def create_shortcut(data_dir):
    location = os.path.expandvars("%HOMEDRIVE%%HOMEPATH%\\Desktop\\Segmate.lnk")
    icon_path = data_dir / "segmate" / "Lib" / \
                "site-packages" / "segmate" / "icons" / "app-icon.ico"
    bin_path = data_dir / "segmate" / "Scripts" / "segmate"
    vbs_script = vbs_shortcut.format(location, bin_path, icon_path)
    with open(data_dir / "create_shortcut.vbs", "w") as csf:
        csf.write(vbs_script)
    subprocess.call("cmd /c {0}".format(str(data_dir / "create_shortcut.vbs")))


def main():
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)

    print("Downloading 'Segmate'...")
    urllib.request.urlretrieve(download_url, data_dir / filename)
    print("Extracting...")
    with zipfile.ZipFile(data_dir / filename) as zf:
        zf.extractall(data_dir / version)
    print("Creating virtual environment...")
    venv.create(data_dir / "segmate",
                system_site_packages=True, clear=True, with_pip=True)
    print("Installing dependencies...")
    pip_install(data_dir, use_requirements=True)
    print("Installing 'Segmate'...")
    pip_install(data_dir, data_dir / version / "segmate-{0}".format(version))

    print("Cleaning up...")
    shutil.rmtree(data_dir / version)
    os.remove(data_dir / filename)

    if platform.system() == "Linux":
        print("Creating .desktop file...")
        create_desktop_file(data_dir)

    if platform.system() == "Windows":
        print("Creating desktop shortcut...")
        create_shortcut(data_dir)

if __name__ == "__main__":
    main()

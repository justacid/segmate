# Segmate

Segmate is a (semantic) segmentation annotation tool that is fast, efficient,
light-weight, and supports graphics drawing tablets. Segmate is entirely written
in Python in order to take advantage of its vast scientific computing and machine
learning ecosystems. A plugin architecture provides infinite extensibility.
![segmate](https://user-images.githubusercontent.com/9140377/63302764-43f26c80-c2de-11e9-8349-120e53539c24.png)
Requires Python 3.5+

## Installation

### Linux
The easiest way is to simply run
```
curl -sSL https://raw.githubusercontent.com/justacid/segmate/master/install-segmate.py | python
```
This installs Segmate to `~/.local/share/segmate` and generates a .desktop file that is copied
to `~/.local/share/applications`. Of course you can first download `install-segmate.py` manually,
then mark it executable with `chmod +x` and run it.

### Windows
Download `install-segmate.py` and execute the script: `python install-segmate.py`.
This installs Segmate to `%appdata%/segmate` and creates a shortcut to the executable on
the desktop.

### MacOs
No install script support, yet. Help wanted.

### Packaging
I would like to provide pre-built Flatpaks, Snaps or AppImages on Linux and a stand-alone
application for Windows, but could not get any of these to work yet. Help wanted.

## Manual install
```
git clone https://github.com/justacid/segmate.git
cd segmate
python -m venv venv
source venv/bin/activate
pip install ../segmate
```

The virtual environment must be active to run segmate.
You can now run `segmate` on your terminal.

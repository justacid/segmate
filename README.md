# Segmate

## Install as user (recommended)

```
git clone https://github.com/justacid/segmate.git
pip install segmate --user
```

Don't forget to add `~/.local/bin` to your path.
You can now run `segmate` on your terminal.

## Install in virtual environment
```
git clone https://github.com/justacid/segmate.git
cd segmate
python -m venv venv
source venv/bin/activate
pip install ../segmate
```

The virtual environment must be active to run segmate.
You can now run `segmate` on your terminal.

## Install for development
As before, but additionally pass the `-e` flag to pip.

## Uninstall
Simply uninstall with pip: `pip uninstall segmate`

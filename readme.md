# TP4 — README

Simple README for the project. Contains two recommended ways to run the server: a quick local setup using a Python virtual environment, or running a Singularity image.

## Quick install & launch (venv)
Copy-and-paste commands:

```bash
# create + activate venv
python3 -m venv .venv
source .venv/bin/activate

# upgrade pip and install dependencies
pip install --upgrade pip
pip install flask requests matplotlib

# note: sqlite3 is part of the Python standard library (no pip needed).
# If you need the sqlite CLI on Debian/Ubuntu:
# sudo apt-get install -y sqlite3

# Run app
python3 server.py
```

## Build & run with Singularity
Download Singularity/Apptainer (installation instructions): https://apptainer.org/

From the repository root (where `server.def` is located), build and run:

```bash
# build the image (requires root or fakeroot)
singularity build --fakeroot server.sif server.def

# run the container
singularity run server.sif
```

If your server listens on a port, map or expose as required by your environment. Use `--fakeroot` if your system supports it or build as root.

## Notes
- The sqlite3 database file (if used) will be created locally unless your code places it elsewhere; ensure file permissions are correct.
- Modify commands above to match actual filenames (entrypoint, requirements, def file) in this repository.

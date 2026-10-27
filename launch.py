"""Double-click start.bat on Windows, or run python launch.py on any OS."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
if sys.version_info < (3,11):
    raise SystemExit('Please install Python 3.11 or newer.')
venv=ROOT/'.venv'
python=venv/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not python.exists():
    subprocess.run([sys.executable,'-m','venv',str(venv)],check=True)
marker=venv/'construct-requirements.txt'
requirements=(ROOT/'backend/requirements.txt').read_text()
if not marker.exists() or marker.read_text()!=requirements:
    subprocess.run([str(python),'-m','pip','install','-r','backend/requirements.txt'],check=True)
    marker.write_text(requirements)
if not (ROOT/'frontend/dist/index.html').exists():
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    if not npm: raise SystemExit('Node.js 20.19+ or 22.12+ is needed to build the frontend. Install Node.js, then retry.')
    subprocess.run([npm,'ci'],cwd=ROOT/'frontend',check=True)
    subprocess.run([npm,'run','build'],cwd=ROOT/'frontend',check=True)

url='http://127.0.0.1:8000'
try:
    with urllib.request.urlopen(url+'/api/health',timeout=1) as response:
        existing=response.read().decode()
    if 'image_generation' in existing and 'model' in existing:
        print('ConstructAI is already running at '+url)
        webbrowser.open(url)
        raise SystemExit(0)
except (OSError, TimeoutError):
    pass

def open_when_ready():
    for _ in range(60):
        try:
            with urllib.request.urlopen(url+'/api/health',timeout=1):
                webbrowser.open(url)
                return
        except (OSError, TimeoutError): time.sleep(.5)

print('ConstructAI: '+url+'\nKeep this window open. Press Ctrl+C to stop.')
threading.Thread(target=open_when_ready,daemon=True).start()
try:
    subprocess.run([str(python),'-m','uvicorn','main:app','--app-dir','backend','--host','127.0.0.1','--port','8000'],check=True)
except KeyboardInterrupt:
    print('\nConstructAI stopped.')

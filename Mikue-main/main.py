from pathlib import Path
import os
import runpy


APP_DIR = Path(__file__).parent / "Miku bot unfinished" / "files"

os.chdir(APP_DIR)
runpy.run_path("bot.py", run_name="__main__")

@echo off
title Building VISION with Nuitka...

echo ==========================================
echo         Building VISION.exe
echo ==========================================

set MAIN_FILE=vision_v4.py
set OUTPUT_NAME=VISION

python -m nuitka ^
--standalone ^
--onefile ^
--mingw64 ^
--follow-imports ^
--enable-plugin=tk-inter ^
--output-filename=%OUTPUT_NAME%.exe ^
--include-data-dir=jarvis_functions=jarvis_functions ^
--include-data-dir=ui=ui ^
--include-data-dir=sound_files=sound_files ^
--include-data-dir=output=output ^
--include-data-dir=account=account ^
--include-data-dir=build=build ^
--include-data-file=.env=.env ^
--include-data-file=requirements.txt=requirements.txt ^
--include-data-file=README.md=README.md ^
--include-data-file=jarvis_functions/essential_functions/config.json=jarvis_functions/essential_functions/config.json ^
--include-data-file=jarvis_functions/essential_functions/contacts.json=jarvis_functions/essential_functions/contacts.json ^
--include-data-file=jarvis_functions/essential_functions/important_files/ffmpeg.exe=jarvis_functions/essential_functions/important_files/ffmpeg.exe ^
--include-data-file=jarvis_functions/essential_functions/important_files/ffprobe.exe=jarvis_functions/essential_functions/important_files/ffprobe.exe ^
--include-data-file=jarvis_functions/essential_functions/important_files/ffplay.exe=jarvis_functions/essential_functions/important_files/ffplay.exe ^
--include-data-file=jarvis_functions/essential_functions/important_files/flac.exe=jarvis_functions/essential_functions/important_files/flac.exe ^
%MAIN_FILE%

echo ==========================================
echo     BUILD COMPLETED: %OUTPUT_NAME%.exe
echo ==========================================
pause

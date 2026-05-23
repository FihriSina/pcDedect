@echo off

cd /d %~dp0

python -m PyInstaller ^
--onefile ^
--windowed ^
--hidden-import customtkinter ^
--hidden-import PIL ^
--hidden-import cairosvg ^
--collect-submodules customtkinter ^
--collect-submodules PIL ^
--collect-submodules cairosvg ^
--add-data "assets;assets" ^
app\donanim_gui_vFinal.py

pause
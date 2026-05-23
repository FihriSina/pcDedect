@echo off
cd /d %~dp0

if not exist dist\donanim_gui_vFinal.exe (
    echo HATA: dist\donanim_gui_vFinal.exe bulunamadi.
    echo Once build.bat dosyasini calistir.
    pause
    exit /b
)

if not exist release mkdir release

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'dist\donanim_gui_vFinal.exe' -DestinationPath 'release\DonanimBilgi_Portable.zip' -Force"

echo.
echo Portable ZIP olusturuldu:
echo release\DonanimBilgi_Portable.zip
pause
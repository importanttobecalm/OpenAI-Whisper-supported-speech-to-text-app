@echo off
echo ====================================
echo  Whisper Web Arayuzu Baslatiliyor
echo ====================================
echo.

REM Python'un kurulu olduğunu kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python 3.10 veya uzeri yukleyin.
    pause
    exit /b 1
)

echo Python bulundu.
echo.

REM Bagimliliklar yuklu mu kontrol et
echo Bagimliliklari kontrol ediliyor...
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Gradio bulunamadi. Bagimliliklar yukleniyor...
    echo.
    pip install -r whisper_app\requirements.txt
    if errorlevel 1 (
        echo.
        echo HATA: Bagimliliklar yuklenemedi!
        pause
        exit /b 1
    )
)

echo.
echo ====================================
echo  Web arayuzu baslatiliyor...
echo  Tarayicinizda otomatik acilacak
echo  Kapatmak icin Ctrl+C basin
echo ====================================
echo.

REM FFmpeg'i PATH'e ekle
set "FFMPEG_PATH=%~dp0FFmpeg 64-bit static Windows build from www.gyan.dev\bin"
if exist "%FFMPEG_PATH%" (
    echo FFmpeg bulundu: %FFMPEG_PATH%
    set "PATH=%FFMPEG_PATH%;%PATH%"
    echo FFmpeg PATH'e eklendi
    echo.
) else (
    echo UYARI: FFmpeg bulunamadi! MP3/M4A dosyalari calismiyor olabilir.
    echo.
)

REM Web arayuzunu baslat
python web_ui.py

pause

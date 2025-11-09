#!/bin/bash

# Whisper Transcription - Mac .app Oluşturucu
# Bu script Mac için çift tıklanabilir .app dosyası oluşturur

echo "🎙️  Whisper Transcription - Mac App Oluşturucu"
echo "================================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Hata kontrolü
set -e

# Script'in bulunduğu dizin
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📂 Proje dizini: ${NC}$PROJECT_DIR"
echo ""

# py2app kontrolü
echo -e "${YELLOW}🔍 py2app kontrolü yapılıyor...${NC}"
if ! python3 -c "import py2app" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  py2app bulunamadı. Yükleniyor...${NC}"
    pip3 install py2app
fi
echo -e "${GREEN}✅ py2app hazır${NC}"
echo ""

# setup.py dosyası oluştur
echo -e "${YELLOW}📝 setup.py dosyası oluşturuluyor...${NC}"
cat > "$SCRIPT_DIR/setup_app.py" << 'EOF'
"""
py2app setup script for Whisper Transcription
"""
from setuptools import setup

APP = ['whisper_app_launcher.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',  # Eğer varsa
    'plist': {
        'CFBundleName': 'Whisper Transcription',
        'CFBundleDisplayName': 'Whisper Transcription',
        'CFBundleGetInfoString': 'Ses-Metin Dönüştürücü',
        'CFBundleIdentifier': 'com.whisper.transcription',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '2025',
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
    },
    'packages': ['tkinter', 'pathlib', 'threading'],
    'includes': ['tkinter', 'tkinter.ttk'],
}

setup(
    name='WhisperTranscription',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF
echo -e "${GREEN}✅ setup.py oluşturuldu${NC}"
echo ""

# .app dosyası oluştur
echo -e "${YELLOW}🔨 .app dosyası oluşturuluyor (bu biraz zaman alabilir)...${NC}"
cd "$SCRIPT_DIR"
python3 setup_app.py py2app

if [ -d "dist/Whisper Transcription.app" ]; then
    echo -e "${GREEN}✅ .app dosyası başarıyla oluşturuldu!${NC}"
    echo ""
    echo -e "${BLUE}📍 Konum: ${NC}$SCRIPT_DIR/dist/Whisper Transcription.app"
    echo ""
    echo -e "${GREEN}🎉 Tamamlandı!${NC}"
    echo ""
    echo -e "${YELLOW}Kullanım:${NC}"
    echo "1. 'dist' klasöründeki 'Whisper Transcription.app' dosyasını Applications klasörüne taşıyın"
    echo "2. Uygulamaya çift tıklayın"
    echo "3. İlk açılışta 'Güvenilmeyen geliştirici' uyarısı alabilirsiniz."
    echo "   Bu durumda: Sistem Tercihleri > Güvenlik > 'Yine de Aç' butonuna tıklayın"
    echo ""
else
    echo -e "${RED}❌ Hata: .app dosyası oluşturulamadı${NC}"
    exit 1
fi

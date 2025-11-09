#!/bin/bash

# Whisper Transcription - Hızlı Başlangıç (Mac)
# Bu dosyayı çift tıklayarak direkt çalıştırabilirsiniz

echo "🎙️  Whisper Transcription - Hızlı Başlangıç"
echo "==========================================="
echo ""

# Script'in bulunduğu dizin
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Python launcher'ı çalıştır
echo "▶️  Uygulama başlatılıyor..."
echo ""

cd "$SCRIPT_DIR"
python3 whisper_app_launcher.py

# Hata durumunda mesaj göster
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Hata: Uygulama başlatılamadı"
    echo ""
    echo "Çözüm önerileri:"
    echo "1. Python 3 kurulu mu kontrol edin: python3 --version"
    echo "2. Gerekli kütüphaneleri yükleyin: pip3 install -r $PROJECT_DIR/requirements_audio.txt"
    echo "3. README_MAC.md dosyasını okuyun"
    echo ""
    read -p "Devam etmek için bir tuşa basın..."
fi

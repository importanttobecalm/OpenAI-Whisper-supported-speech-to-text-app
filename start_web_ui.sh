#!/bin/bash

echo "===================================="
echo " Whisper Web Arayüzü Başlatılıyor"
echo "===================================="
echo ""

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "HATA: Python bulunamadı!"
    echo "Lütfen Python 3.10 veya üzeri yükleyin."
    exit 1
fi

echo "Python bulundu: $(python3 --version)"
echo ""

# Bağımlılık kontrolü
echo "Bağımlılıklar kontrol ediliyor..."
if ! python3 -c "import gradio" &> /dev/null; then
    echo ""
    echo "Gradio bulunamadı. Bağımlılıklar yükleniyor..."
    echo ""
    pip3 install -r whisper_app/requirements.txt

    if [ $? -ne 0 ]; then
        echo ""
        echo "HATA: Bağımlılıklar yüklenemedi!"
        exit 1
    fi
fi

echo ""
echo "===================================="
echo " Web arayüzü başlatılıyor..."
echo " Tarayıcınızda otomatik açılacak"
echo " Kapatmak için Ctrl+C basın"
echo "===================================="
echo ""

# Web arayüzünü başlat
python3 web_ui.py

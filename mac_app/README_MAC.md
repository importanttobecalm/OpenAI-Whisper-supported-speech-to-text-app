# 🎙️ Whisper Transcription - Mac Kullanım Kılavuzu

Mac için tek tıkla çalışan uygulama oluşturma ve kullanım rehberi.

## 📋 İçindekiler

1. [Gereksinimler](#gereksinimler)
2. [Kurulum](#kurulum)
3. [Mac .app Dosyası Oluşturma](#mac-app-dosyası-oluşturma)
4. [Kullanım](#kullanım)
5. [Sorun Giderme](#sorun-giderme)

---

## 🔧 Gereksinimler

- **macOS**: 10.13 (High Sierra) veya üzeri
- **Python**: 3.8 veya üzeri (genellikle Mac'te hazır gelir)
- **Xcode Command Line Tools** (otomatik yüklenecek)

Homebrew ile Python kurulumu (opsiyonel):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

---

## 📦 Kurulum

### Adım 1: Terminal'i Açın

**Finder** → **Uygulamalar** → **Yardımcı Programlar** → **Terminal**

### Adım 2: Proje Dizinine Gidin

```bash
cd ~/Desktop/SpeechToText/mac_app
```

veya projenizin bulunduğu dizine göre yolu değiştirin.

### Adım 3: Gerekli Python Kütüphanelerini Yükleyin

```bash
# Ana proje dizinine dön
cd ..

# Ses işleme kütüphaneleri
pip3 install -r requirements_audio.txt

# Gemini AI kütüphaneleri (opsiyonel)
pip3 install -r requirements_gemini.txt
```

---

## 🚀 Mac .app Dosyası Oluşturma

### Otomatik Yöntem (Önerilen)

Terminal'de:

```bash
cd ~/Desktop/SpeechToText/mac_app
chmod +x create_mac_app.sh
./create_mac_app.sh
```

Bu script otomatik olarak:
- ✅ py2app'i yükler
- ✅ .app dosyasını oluşturur
- ✅ `dist/` klasöründe hazır uygulamayı bulundurur

### Manuel Yöntem

```bash
cd ~/Desktop/SpeechToText/mac_app

# py2app'i yükle
pip3 install py2app

# .app dosyası oluştur
python3 setup_app.py py2app
```

---

## 📱 Kullanım

### Yöntem 1: .app Dosyası ile (Önerilen)

1. **Uygulamayı Kopyala**
   ```bash
   # dist/ klasöründen Applications'a kopyala
   cp -r "dist/Whisper Transcription.app" /Applications/
   ```

2. **Uygulamayı Aç**
   - Finder'da **Applications** klasörüne gidin
   - **Whisper Transcription** uygulamasına çift tıklayın

3. **İlk Açılış (Güvenlik Uyarısı)**
   
   macOS ilk açılışta "güvenilmeyen geliştirici" uyarısı verebilir:
   
   - **Sistem Tercihleri** → **Güvenlik ve Gizlilik**
   - "Yine de Aç" veya "Open Anyway" butonuna tıklayın
   
   veya Terminal'den:
   ```bash
   xattr -cr "/Applications/Whisper Transcription.app"
   ```

4. **Gemini API Anahtarı (Opsiyonel)**
   
   - Uygulama açıldığında API anahtarı alanına anahtarınızı girin
   - "💾 Kaydet" butonuna tıklayın
   - Anahtar güvenli şekilde `~/.whisper_app_env` dosyasında saklanır

5. **Web Arayüzünü Başlat**
   
   - "🚀 Web Arayüzünü Başlat" butonuna tıklayın
   - Tarayıcınızda otomatik olarak açılacak
   - Ses dosyalarınızı yükleyin ve transkribe edin!

### Yöntem 2: Python Script ile

Direkt olarak launcher'ı çalıştırabilirsiniz:

```bash
cd ~/Desktop/SpeechToText/mac_app
python3 whisper_app_launcher.py
```

---

## 🎨 Özellikler

### Ana Launcher Özellikleri

- ✅ **Tek Tıkla Başlatma**: .app dosyası ile kolay erişim
- ✅ **GUI Arayüz**: Modern, kullanıcı dostu Tkinter arayüzü
- ✅ **API Key Yönetimi**: Gemini API anahtarını güvenle kaydedin
- ✅ **Otomatik Tarayıcı**: Web arayüzü otomatik açılır
- ✅ **Durum Takibi**: Sunucu durumunu anlık görün

### Web Arayüzü Özellikleri

- 🎤 **Ses Formatları**: MP3, WAV, M4A, FLAC, OGG
- 🤖 **Whisper Modelleri**: tiny, base, small, medium, large-v3, turbo
- 🌍 **Çoklu Dil**: Türkçe, İngilizce, Almanca, Fransızca ve daha fazlası
- 📝 **Çıktı Formatları**: TXT, JSON, SRT (altyazı)
- ⚡ **GPU Desteği**: CUDA ile hızlandırılmış işleme (varsa)
- 🤖 **Gemini AI İyileştirme**: Noktalama ve dilbilgisi düzeltme

---

## 🔧 Sorun Giderme

### "Python bulunamadı" Hatası

```bash
# Python 3 kurulu mu kontrol edin
python3 --version

# Değilse Homebrew ile yükleyin
brew install python@3.11
```

### "Modül bulunamadı" Hatası

```bash
# Tüm gereksinimleri yeniden yükleyin
pip3 install -r ../requirements_audio.txt
pip3 install -r ../requirements_gemini.txt
```

### ".app Dosyası Açılmıyor"

```bash
# Güvenlik özniteliklerini temizle
xattr -cr "/Applications/Whisper Transcription.app"

# Veya Sistem Tercihleri'nden manuel olarak izin verin
```

### "Port Kullanımda" Hatası

Başka bir uygulama 7865 portunu kullanıyor olabilir:

```bash
# Portu kullanan işlemi bul
lsof -i :7865

# İşlemi sonlandır (PID değerini değiştirin)
kill -9 <PID>
```

### FFmpeg Bulunamadı

```bash
# Homebrew ile FFmpeg yükle
brew install ffmpeg

# Kontrol et
ffmpeg -version
```

### GPU/CUDA Sorunları

Mac'te CUDA yerine MPS (Metal Performance Shaders) kullanılır:

```python
# web_ui.py içinde device seçimini kontrol edin
device = "mps"  # Mac için
```

### Gemini API Hatası

- API anahtarınızı kontrol edin: https://makersuite.google.com/app/apikey
- Kaydedilen anahtarı görmek için:
  ```bash
  cat ~/.whisper_app_env
  ```

---

## 📚 Ek Bilgiler

### Klasör Yapısı

```
mac_app/
├── whisper_app_launcher.py    # Ana launcher script
├── create_mac_app.sh           # .app oluşturma scripti
├── README_MAC.md               # Bu dosya
├── setup_app.py                # py2app setup (otomatik oluşturulur)
├── build/                      # Geçici build dosyaları
└── dist/
    └── Whisper Transcription.app  # Çalıştırılabilir uygulama
```

### Dosya Boyutları

- **.app dosyası**: ~5-10 MB (Python runtime dahil)
- **Whisper modelleri**: Model boyutuna göre (indirildikçe)
  - tiny: ~75 MB
  - small: ~461 MB
  - large-v3: ~2.9 GB

### Performans İpuçları

1. **İlk Kullanım**: Model indirilirken biraz bekleyin
2. **Model Seçimi**: Türkçe için en az "small" model kullanın
3. **GPU**: Mac'te "CPU" modu seçin (veya MPS desteği varsa)
4. **Büyük Dosyalar**: 1 saat+ dosyalar için "medium" veya daha küçük model tercih edin

---

## 🆘 Destek

Sorun yaşıyorsanız:

1. **Logları kontrol edin**: Terminal çıktısını inceleyin
2. **Gereksinimleri doğrulayın**: Python ve kütüphaneler güncel mi?
3. **Script'i test edin**: Önce `python3 whisper_app_launcher.py` ile deneyin

---

## 📝 Lisans

Bu proje kişisel kullanım içindir.

---

**Keyifli Kullanımlar! 🎉**

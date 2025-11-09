"""
Whisper Streaming - Web Arayüzü
Basit ve kullanıcı dostu ses-metin dönüştürme arayüzü
"""

import gradio as gr
import logging
from pathlib import Path
import tempfile
from typing import Tuple, Optional
import time
import os

from whisper_app import WhisperProcessor, WhisperConfig
from gemini_enhancer import GeminiEnhancer


# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Global processor (model önbelleği için)
current_processor = None
current_config = None


def format_timestamp(seconds: float) -> str:
    """Saniyeyi okunabilir zaman formatına çevir (HH:MM:SS)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_gpu_info() -> str:
    """GPU bilgilerini al."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return f"GPU: {gpu_name} ({gpu_memory:.1f}GB) - {gpu_count} cihaz tespit edildi"
        else:
            return "GPU bulunamadı - CPU modu kullanılacak"
    except Exception as e:
        return f"GPU bilgisi alınamadı: {e}"


def create_processor(model_size: str, device: str, language: str) -> WhisperProcessor:
    """Processor oluştur veya mevcut olanı döndür."""
    global current_processor, current_config

    # Ayarlar değişmediyse mevcut processor'ı kullan
    if current_processor is not None:
        if (current_config.model_size == model_size and
            current_config.device == device and
            current_config.language == language):
            logger.info("Mevcut model kullanılıyor")
            return current_processor

    # Yeni processor oluştur
    logger.info(f"Yeni model yükleniyor: {model_size} ({device})")
    config = WhisperConfig(
        model_size=model_size,
        device=device,
        language=language,
        vac_enabled=True,
        include_timestamps=True,
        num_workers=8,  # Increased workers for better GPU utilization
        device_index=0,  # Primary GPU
    )

    current_config = config
    current_processor = WhisperProcessor(config)

    return current_processor


def transcribe_audio(
    audio_file,
    model_size: str,
    language: str,
    device: str,
    output_format: str,
    use_gemini: bool = False,
    gemini_api_key: Optional[str] = None,
) -> Tuple[str, Optional[str], str]:
    """
    Ses dosyasını transkribe et.

    Returns:
        Tuple[transkripsiyon metni, indirilebilir dosya yolu, durum mesajı]
    """
    try:
        if audio_file is None:
            return "", None, "❌ Lütfen bir ses dosyası yükleyin!"

        start_time = time.time()

        # Processor oluştur
        status_msg = f"🔄 Model yükleniyor: {model_size}..."
        logger.info(status_msg)

        processor = create_processor(model_size, device, language)

        # Transkripsiyon yap
        status_msg = "🎯 Transkripsiyon yapılıyor..."
        logger.info(f"Ses dosyası işleniyor: {audio_file}")

        result = processor.transcribe(Path(audio_file))

        # İşlem süresi
        processing_time = time.time() - start_time

        # Çıktı formatına göre dosya oluştur
        output_file = None

        if output_format == "Text (.txt)":
            # Text dosyası oluştur
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                f.write(result.full_text)
                output_file = f.name

        elif output_format == "JSON (.json)":
            # JSON dosyası oluştur
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
                result.to_json(Path(f.name))
                output_file = f.name

        elif output_format == "Altyazı (.srt)":
            # SRT dosyası oluştur
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.srt', encoding='utf-8') as f:
                result.to_srt(Path(f.name))
                output_file = f.name

        # Gemini ile metin iyileştirme (opsiyonel)
        enhanced_text = ""
        gemini_status = ""
        if use_gemini:
            try:
                logger.info("🤖 Gemini API ile metin iyileştiriliyor...")
                enhancer = GeminiEnhancer(api_key=gemini_api_key)
                enhanced_text = enhancer.enhance_transcript(
                    result.full_text,
                    language=language
                )
                gemini_status = "✓ Uygulandı"
                logger.info("✓ Gemini iyileştirme tamamlandı")
            except ValueError as e:
                logger.warning(f"Gemini API anahtarı hatası: {e}")
                gemini_status = "✗ API anahtarı eksik"
            except Exception as e:
                logger.warning(f"Gemini iyileştirme hatası: {e}")
                gemini_status = "✗ Hata oluştu"
        else:
            gemini_status = "✗ Kullanılmadı"
        
        # Zaman bazlı segment çıktısı oluştur (orijinal)
        formatted_text = ""
        for segment in result.segments:
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            formatted_text += f"[{start_time} - {end_time}] {segment.text.strip()}\n\n"

        # Başarı mesajı
        status_msg = f"""
✅ **Transkripsiyon Tamamlandı!**

📊 **İstatistikler:**
- **Dil:** {result.language.upper()}
- **Süre:** {result.duration:.2f} saniye
- **İşlem Süresi:** {processing_time:.2f} saniye
- **Hız:** {result.duration/processing_time:.2f}x gerçek zamanlı
- **Segment Sayısı:** {len(result.segments)}
- **Model:** {model_size}
- **Cihaz:** {device.upper()}
- **Gemini İyileştirme:** {gemini_status}

💡 **İpucu:** Dosyayı indirmek için aşağıdaki "İndir" butonuna tıklayın.
        """

        # Gemini kullanıldıysa iyileştirilmiş metni göster, değilse orijinali
        display_text = enhanced_text if (use_gemini and enhanced_text) else formatted_text.strip()
        
        return display_text, output_file, status_msg

    except Exception as e:
        logger.error(f"Hata: {e}", exc_info=True)
        error_msg = f"""
❌ **Hata Oluştu!**

**Hata Mesajı:** {str(e)}

**Olası Çözümler:**
- GPU hatası alıyorsanız, "CPU" modunu seçin
- Bellek hatası alıyorsanız, daha küçük bir model seçin (tiny veya base)
- Ses dosyası formatını kontrol edin
        """
        return "", None, error_msg


# Gradio arayüzü
def create_ui():
    """Gradio arayüzü oluştur."""

    with gr.Blocks(
        title="Whisper Transkripsiyon",
        theme=gr.themes.Soft(),
    ) as demo:

        # GPU bilgisini al
        gpu_info = get_gpu_info()

        gr.Markdown(f"""
        # 🎙️ Whisper Ses-Metin Dönüştürücü

        Ses dosyalarınızı metne dönüştürün. MP3, WAV, M4A, FLAC formatları desteklenir.

        **💻 Sistem:** {gpu_info}
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Ses Dosyası Yükle")

                audio_input = gr.Audio(
                    label="Ses Dosyası",
                    type="filepath",
                    sources=["upload", "microphone"],
                )

                gr.Markdown("### ⚙️ Ayarlar")

                model_dropdown = gr.Dropdown(
                    choices=[
                        "tiny",
                        "base",
                        "small",
                        "medium",
                        "large-v3",
                        "turbo",
                    ],
                    value="small",
                    label="Model",
                    info="Türkçe için en az 'small' model önerilir (daha iyi noktalama)"
                )

                language_dropdown = gr.Dropdown(
                    choices=[
                        "auto (Otomatik Algıla)",
                        "tr (Türkçe)",
                        "en (İngilizce)",
                        "de (Almanca)",
                        "fr (Fransızca)",
                        "es (İspanyolca)",
                        "it (İtalyanca)",
                        "ar (Arapça)",
                        "ru (Rusça)",
                        "zh (Çince)",
                    ],
                    value="auto (Otomatik Algıla)",
                    label="Dil",
                    info="Varsayılan: Otomatik algılama"
                )

                device_dropdown = gr.Dropdown(
                    choices=["cuda (GPU)", "cpu (CPU)"],
                    value="cuda (GPU)",
                    label="İşlemci",
                    info="GPU varsa 5-10x daha hızlı"
                )

                output_format_dropdown = gr.Dropdown(
                    choices=[
                        "Text (.txt)",
                        "JSON (.json)",
                        "Altyazı (.srt)",
                    ],
                    value="Text (.txt)",
                    label="Çıktı Formatı",
                    info="İndirilecek dosya formatı"
                )
                
                gr.Markdown("### 🤖 Gemini AI İyileştirme (Opsiyonel)")
                
                gemini_checkbox = gr.Checkbox(
                    label="Gemini ile Metin İyileştir",
                    value=False,
                    info="Noktalama, dilbilgisi ve akıcılık iyileştirmesi"
                )
                
                gemini_api_key_input = gr.Textbox(
                    label="Gemini API Anahtarı",
                    placeholder="API anahtarınızı buraya girin (veya GEMINI_API_KEY ortam değişkeni)",
                    type="password",
                    visible=False
                )
                
                # Checkbox değiştiğinde API key input'unu göster/gizle
                def toggle_api_key(use_gemini):
                    return gr.update(visible=use_gemini)
                
                gemini_checkbox.change(
                    fn=toggle_api_key,
                    inputs=[gemini_checkbox],
                    outputs=[gemini_api_key_input]
                )

                transcribe_btn = gr.Button(
                    "🚀 Transkribe Et",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=1):
                gr.Markdown("### 📝 Transkripsiyon Sonucu")

                status_output = gr.Markdown(
                    value="⏳ Ses dosyası yükleyip 'Transkribe Et' butonuna basın...",
                )

                text_output = gr.Textbox(
                    label="Metin",
                    lines=15,
                    placeholder="Transkripsiyon burada görünecek...",
                    show_copy_button=True,
                )

                file_output = gr.File(
                    label="💾 Dosyayı İndir",
                )

        gr.Markdown("""
        ---
        ### 📊 Model Karşılaştırması

        | Model | Hız | Kalite | GPU Bellek | Kullanım |
        |-------|-----|--------|------------|----------|
        | tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Hızlı test |
        | base | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | Günlük kullanım |
        | small | ⚡⚡⭐ | ⭐⭐⭐⭐ | ~2GB | İyi kalite |
        | medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | Yüksek kalite |
        | large-v3 | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | En iyi kalite |
        | turbo | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ~6GB | Optimize edilmiş (large-v3) |

        ### 💡 İpuçları
        - **İlk kullanımda** model indirilecektir, biraz zaman alabilir
        - **GPU yoksa** CPU modunu seçin (daha yavaş ama çalışır)
        - **Bellek hatası** alırsanız daha küçük model deneyin
        - **Otomatik dil algılama** çoğu durumda iyi çalışır
        - **turbo modeli** large-v3'ün optimize edilmiş versiyonudur (8x daha hızlı)
        - **Türkçe için** en az 'small' model kullanın (daha iyi noktalama ve dilbilgisi)
        - **Dili manuel seçin** (tr) otomatik algılama yerine daha iyi sonuç için
        
        ### 🤖 Gemini İyileştirme
        - **Gemini API** transkripsiyon sonrası metni akıcılaştırır ve düzeltir
        - **API anahtarı** için: https://makersuite.google.com/app/apikey
        - **GEMINI_API_KEY** ortam değişkeni ayarlarsanız her seferinde girmek zorunda kalmazsınız
        - Gemini kullanımı **opsiyonel**dir, checkbox'ı işaretlemeyin normal transkripsiyon için

        ### ⚡ GPU Optimizasyonları (Otomatik Aktif)
        - **TF32 desteği** - Ampere+ GPU'larda %20 daha hızlı
        - **float16 precision** - Bellek kullanımını yarıya indirir
        - **CUDA cache** - Model yeniden yüklemeyi önler

        ### 🎯 Desteklenen Formatlar
        - **Ses:** MP3, WAV, M4A, FLAC, OGG
        - **Çıktı:** TXT (düz metin), JSON (detaylı), SRT (altyazı)
        """)

        # Event handler
        def process_transcription(audio, model, lang, device, format, use_gemini, api_key):
            # Dil kodunu ayıkla
            lang_code = lang.split("(")[0].strip()
            if lang_code == "auto":
                lang_code = "auto"

            # Cihaz kodunu ayıkla
            device_code = device.split("(")[0].strip()

            return transcribe_audio(
                audio, 
                model, 
                lang_code, 
                device_code, 
                format,
                use_gemini=use_gemini,
                gemini_api_key=api_key if api_key else None
            )

        transcribe_btn.click(
            fn=process_transcription,
            inputs=[
                audio_input,
                model_dropdown,
                language_dropdown,
                device_dropdown,
                output_format_dropdown,
                gemini_checkbox,
                gemini_api_key_input,
            ],
            outputs=[text_output, file_output, status_output],
        )

        # Örnek sesler (opsiyonel)
        gr.Markdown("""
        ---
        ### 🎤 Nasıl Kullanılır?
        1. Ses dosyanızı yükleyin (veya mikrofon ile kaydedin)
        2. Model ve dil seçeneklerini ayarlayın
        3. "Transkribe Et" butonuna basın
        4. Sonucu görüntüleyin ve indirin
        """)

    return demo


def main():
    """Ana fonksiyon."""

    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("\n" + "="*70)
    print(" WHISPER TRANSKRIPSIYON WEB ARAYUZU ".center(70, "="))
    print("="*70 + "\n")

    print(">> Web arayuzu baslatiliyor...")
    print(">> Tarayicinizda otomatik olarak acilacak")
    print(">> Kapatmak icin Ctrl+C basin\n")

    # Arayüzü oluştur ve başlat
    demo = create_ui()

    demo.launch(
        server_name="127.0.0.1",  # Localhost
        server_port=7865,          # Daha yüksek port
        share=False,               # Genel paylaşım kapalı
        inbrowser=True,            # Tarayıcıda otomatik aç
        show_error=True,           # Hataları göster
    )


if __name__ == "__main__":
    main()

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

    # Dark mode için custom CSS
    custom_css = """
    .dark {
        --body-text-color: #e0e0e0;
        --block-title-text-color: #ffffff;
    }
    footer {visibility: hidden}
    """

    with gr.Blocks(
        title="Whisper Transkripsiyon",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:

        # GPU bilgisini al
        gpu_info = get_gpu_info()

        gr.Markdown(f"""
        # 🎙️ Whisper Ses-Metin Dönüştürücü | Speech-to-Text Converter

        Ses dosyalarınızı metne dönüştürün. MP3, WAV, M4A, FLAC formatları desteklenir.  
        Convert your audio files to text. MP3, WAV, M4A, FLAC formats supported.

        **💻 Sistem | System:** {gpu_info}
        """)
        
        # Nasıl Kullanılır - En üstte
        gr.Markdown("""
        ---
        ### 🎤 Nasıl Kullanılır? | How to Use?
        1. **Ses dosyanızı yükleyin** (veya mikrofon ile kaydedin) | Upload your audio file (or record with microphone)
        2. **Model ve dil seçeneklerini ayarlayın** | Configure model and language options
        3. **"Transkribe Et" butonuna basın** | Click "Transcribe" button
        4. **Sonucu görüntüleyin ve indirin** | View and download the result
        ---
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Ses Dosyası Yükle | Upload Audio File")

                audio_input = gr.Audio(
                    label="Ses Dosyası | Audio File",
                    type="filepath",
                    sources=["upload", "microphone"],
                )

                gr.Markdown("### ⚙️ Ayarlar | Settings")

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
                    info="Türkçe için 'small' önerilir | 'small' recommended for Turkish"
                )

                language_dropdown = gr.Dropdown(
                    choices=[
                        "auto (Otomatik Algıla | Auto Detect)",
                        "tr (Türkçe | Turkish)",
                        "en (İngilizce | English)",
                        "de (Almanca | German)",
                        "fr (Fransızca | French)",
                        "es (İspanyolca | Spanish)",
                        "it (İtalyanca | Italian)",
                        "ar (Arapça | Arabic)",
                        "ru (Rusça | Russian)",
                        "zh (Çince | Chinese)",
                    ],
                    value="auto (Otomatik Algıla | Auto Detect)",
                    label="Dil | Language",
                    info="Varsayılan: Otomatik | Default: Auto detection"
                )

                device_dropdown = gr.Dropdown(
                    choices=["cuda (GPU)", "cpu (CPU)"],
                    value="cuda (GPU)",
                    label="İşlemci | Processor",
                    info="GPU 5-10x daha hızlı | GPU is 5-10x faster"
                )

                output_format_dropdown = gr.Dropdown(
                    choices=[
                        "Text (.txt)",
                        "JSON (.json)",
                        "Altyazı | Subtitle (.srt)",
                    ],
                    value="Text (.txt)",
                    label="Çıktı Formatı | Output Format",
                    info="İndirilecek dosya formatı | Download file format"
                )
                
                gr.Markdown("### 🤖 Gemini AI İyileştirme | Enhancement (Opsiyonel | Optional)")
                
                gemini_checkbox = gr.Checkbox(
                    label="Gemini ile Metin İyileştir | Enhance with Gemini",
                    value=False,
                    info="Noktalama ve dilbilgisi | Punctuation & grammar"
                )
                
                gemini_api_key_input = gr.Textbox(
                    label="Gemini API Anahtarı | Gemini API Key",
                    placeholder="API anahtarınızı buraya girin | Enter your API key",
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
                    "🚀 Transkribe Et | Transcribe",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=1):
                gr.Markdown("### 📝 Transkripsiyon Sonucu | Transcription Result")

                status_output = gr.Markdown(
                    value="⏳ Ses dosyası yükleyin ve 'Transkribe Et' butonuna basın | Upload audio and click 'Transcribe' button...",
                )

                text_output = gr.Textbox(
                    label="Metin | Text",
                    lines=15,
                    placeholder="Transkripsiyon burada görünecek... | Transcription will appear here...",
                    show_copy_button=True,
                )

                file_output = gr.File(
                    label="💾 Dosyayı İndir | Download File",
                )

        gr.Markdown("""
        ---
        ### 📊 Model Karşılaştırması | Model Comparison

        | Model | Hız\|Speed | Kalite\|Quality | GPU Bellek\|VRAM | Kullanım\|Usage |
        |-------|-----|--------|------------|----------|
        | tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Hızlı test\|Quick test |
        | base | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | Günlük\|Daily use |
        | small | ⚡⚡⭐ | ⭐⭐⭐⭐ | ~2GB | İyi kalite\|Good quality |
        | medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | Yüksek\|High quality |
        | large-v3 | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | En iyi\|Best quality |
        | turbo | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ~6GB | Optimize\|Optimized |

        ### 💡 İpuçları | Tips
        - **İlk kullanımda** model indirilir | Model downloads on first use
        - **GPU yoksa** CPU modunu seçin | Choose CPU if no GPU
        - **Bellek hatası** için küçük model | Use smaller model for memory errors
        - **turbo modeli** 8x daha hızlı | turbo is 8x faster
        - **Türkçe için** 'small' veya üstü | Use 'small' or above for Turkish
        
        ### 🤖 Gemini İyileştirme | Gemini Enhancement
        - Metni akıcılaştırır ve düzeltir | Improves fluency and corrects text
        - API anahtarı | API key: https://makersuite.google.com/app/apikey
        - Opsiyonel özellik | Optional feature

        ### 🎯 Desteklenen Formatlar | Supported Formats
        - **Ses\|Audio:** MP3, WAV, M4A, FLAC, OGG
        - **Çıktı\|Output:** TXT, JSON, SRT (altyazı\|subtitle)
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
        show_api=False,            # API dokümantasyonunu gizle
    )


if __name__ == "__main__":
    main()

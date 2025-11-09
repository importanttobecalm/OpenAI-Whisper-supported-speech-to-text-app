"""
Gemini API ile Konuşma Metni İyileştirme
Transkripsiyon sonrası metni noktalama, dilbilgisi ve akıcılık açısından iyileştirir
"""

import os
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiEnhancer:
    """Gemini API ile metin iyileştirme sınıfı."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Gemini API anahtarı. Belirtilmezse GEMINI_API_KEY ortam değişkeni kullanılır.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Gemini API anahtarı bulunamadı! "
                "Lütfen GEMINI_API_KEY ortam değişkenini ayarlayın veya "
                "api_key parametresini kullanın."
            )
        
        # Gemini API'yi yapılandır
        genai.configure(api_key=self.api_key)
        
        # Model oluştur (Gemini 2.5 Pro - en güçlü model)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("Gemini API başarıyla yapılandırıldı")
    
    def enhance_transcript(
        self, 
        transcript: str, 
        language: str = "tr",
        add_punctuation: bool = True,
        fix_grammar: bool = True,
        improve_fluency: bool = True,
        add_paragraphs: bool = True
    ) -> str:
        """
        Transkripsiyon metnini iyileştir.
        
        Args:
            transcript: İyileştirilecek transkripsiyon metni
            language: Dil kodu (tr, en, vb.)
            add_punctuation: Noktalama işaretleri ekle
            fix_grammar: Dilbilgisi hatalarını düzelt
            improve_fluency: Akıcılığı iyileştir
            add_paragraphs: Paragraf düzenlemesi yap
            
        Returns:
            İyileştirilmiş metin
        """
        if not transcript or not transcript.strip():
            logger.warning("Boş transkripsiyon metni alındı")
            return transcript
        
        # Prompt oluştur
        prompt = self._build_prompt(
            transcript, 
            language, 
            add_punctuation, 
            fix_grammar, 
            improve_fluency,
            add_paragraphs
        )
        
        try:
            logger.info("Gemini API ile metin iyileştiriliyor...")
            
            # Gemini'ye gönder
            response = self.model.generate_content(prompt)
            
            enhanced_text = response.text.strip()
            
            logger.info("Metin başarıyla iyileştirildi")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Gemini API hatası: {e}", exc_info=True)
            # Hata durumunda orijinal metni döndür
            return transcript
    
    def _build_prompt(
        self, 
        transcript: str, 
        language: str,
        add_punctuation: bool,
        fix_grammar: bool,
        improve_fluency: bool,
        add_paragraphs: bool
    ) -> str:
        """Gemini için prompt oluştur."""
        
        # Dil isimlerini belirle
        lang_names = {
            "tr": "Türkçe",
            "en": "İngilizce",
            "de": "Almanca",
            "fr": "Fransızca",
            "es": "İspanyolca",
            "it": "İtalyanca",
            "ar": "Arapça",
            "ru": "Rusça",
            "zh": "Çince"
        }
        lang_name = lang_names.get(language, "belirlenen dil")
        
        # Görevleri belirle
        tasks = []
        if add_punctuation:
            tasks.append("noktalama işaretleri ekle")
        if fix_grammar:
            tasks.append("dilbilgisi hatalarını düzelt")
        if improve_fluency:
            tasks.append("cümleleri daha akıcı hale getir")
        if add_paragraphs:
            tasks.append("metni anlamlı paragraflara böl")
        
        tasks_str = ", ".join(tasks) if tasks else "metni düzenle"
        
        prompt = f"""Sen bir konuşma metni editörüsün. Aşağıdaki ses-metin dönüştürme (speech-to-text) çıktısını iyileştir.

DİL: {lang_name}

GÖREVLER:
- {tasks_str}
- Konuşma tarzını koru (günlük dil, resmi dil, vs.)
- İçeriği değiştirme, sadece format ve dilbilgisini iyileştir
- Anlam kaybı yaşanmamalı
- Doğal ve okunabilir bir metin oluştur

ORİJİNAL METİN:
{transcript}

İYİLEŞTİRİLMİŞ METİN:
"""
        
        return prompt
    
    def enhance_with_context(
        self,
        transcript: str,
        context: str,
        language: str = "tr"
    ) -> str:
        """
        Bağlam bilgisi ile metni iyileştir.
        
        Args:
            transcript: İyileştirilecek metin
            context: Bağlam bilgisi (örn: "Bu bir üniversite dersi kaydıdır")
            language: Dil kodu
            
        Returns:
            İyileştirilmiş metin
        """
        lang_names = {
            "tr": "Türkçe",
            "en": "İngilizce",
        }
        lang_name = lang_names.get(language, "belirlenen dil")
        
        prompt = f"""Sen bir konuşma metni editörüsün. Aşağıdaki ses-metin dönüştürme çıktısını iyileştir.

DİL: {lang_name}
BAĞLAM: {context}

GÖREVLER:
- Noktalama işaretleri ekle
- Dilbilgisi hatalarını düzelt
- Bağlama uygun terimler ve ifadeler kullan
- Metni anlamlı paragraflara böl
- Konuşma tarzını koru
- İçeriği değiştirme, sadece düzenle

ORİJİNAL METİN:
{transcript}

İYİLEŞTİRİLMİŞ METİN:
"""
        
        try:
            logger.info("Gemini API ile bağlamsal metin iyileştirme yapılıyor...")
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API hatası: {e}", exc_info=True)
            return transcript


def enhance_text_simple(transcript: str, api_key: Optional[str] = None, language: str = "tr") -> str:
    """
    Basit kullanım için yardımcı fonksiyon.
    
    Args:
        transcript: İyileştirilecek metin
        api_key: Gemini API anahtarı (opsiyonel)
        language: Dil kodu
        
    Returns:
        İyileştirilmiş metin
    """
    enhancer = GeminiEnhancer(api_key=api_key)
    return enhancer.enhance_transcript(transcript, language=language)


# Test için
if __name__ == "__main__":
    # API anahtarını ortam değişkeninden al
    test_api_key = os.getenv("GEMINI_API_KEY")
    
    if not test_api_key:
        print("⚠️ GEMINI_API_KEY ortam değişkeni ayarlanmamış!")
        print("   Kullanım: set GEMINI_API_KEY=your_api_key_here")
    else:
        # Test metni
        test_text = """
        merhaba bugün sizlere makine öğrenmesi hakkında konuşacağım makine öğrenmesi 
        yapay zekanın bir alt dalıdır ve bilgisayarların verilerden öğrenmesini sağlar 
        bu teknoloji günümüzde birçok alanda kullanılmaktadır örneğin görüntü tanıma 
        doğal dil işleme ve öneri sistemleri gibi
        """
        
        print("🧪 Test ediliyor...\n")
        print("📝 Orijinal Metin:")
        print(test_text)
        print("\n" + "="*70 + "\n")
        
        try:
            enhancer = GeminiEnhancer(api_key=test_api_key)
            enhanced = enhancer.enhance_transcript(test_text, language="tr")
            
            print("✨ İyileştirilmiş Metin:")
            print(enhanced)
            print("\n✅ Test başarılı!")
            
        except Exception as e:
            print(f"\n❌ Test başarısız: {e}")

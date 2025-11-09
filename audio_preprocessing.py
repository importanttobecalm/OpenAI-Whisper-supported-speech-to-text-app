"""
Ses Dosyası Ön İşleme Scripti
- Desibel seviyesi normalizasyonu
- Ekolayzer ile ses parlaklığı artırma
- Gürültü azaltma
- Kompresyon
"""

import os
import sys
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

# FFmpeg yolunu ayarla
FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "FFmpeg 64-bit static Windows build from www.gyan.dev", "bin")
if os.path.exists(FFMPEG_PATH):
    AudioSegment.converter = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
    AudioSegment.ffprobe = os.path.join(FFMPEG_PATH, "ffprobe.exe")
from scipy.signal import butter, sosfilt
import noisereduce as nr
import librosa
import soundfile as sf


class AudioPreprocessor:
    def __init__(self, target_dbfs=-20.0):
        """
        Args:
            target_dbfs: Hedef desibel seviyesi (varsayılan: -20 dBFS)
        """
        self.target_dbfs = target_dbfs
    
    def load_audio(self, file_path):
        """Ses dosyasını yükle"""
        audio = AudioSegment.from_file(file_path)
        return audio
    
    def normalize_audio(self, audio):
        """Ses seviyesini normalize et"""
        # Peak normalization
        audio = normalize(audio)
        
        # Target dBFS'e ayarla
        change_in_dbfs = self.target_dbfs - audio.dBFS
        audio = audio.apply_gain(change_in_dbfs)
        
        return audio
    
    def apply_equalizer(self, audio, brightness_boost=6.0):
        """
        Ekolayzer uygula - sesi parlak ve net yap
        Args:
            brightness_boost: Yüksek frekans artışı (dB cinsinden)
        """
        # NumPy array'e dönüştür
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        sample_rate = audio.frame_rate
        
        # Stereo ise mono yap
        if audio.channels == 2:
            samples = samples.reshape((-1, 2)).mean(axis=1)
        
        # High-shelf filter (3kHz üstü frekansları artır)
        # Konuşma netliği için kritik bölge
        sos = self._design_highshelf_filter(sample_rate, cutoff=3000, gain_db=brightness_boost)
        filtered = sosfilt(sos, samples)
        
        # Mid-boost filter (1-3kHz arası - insan sesi için optimal)
        sos_mid = self._design_peaking_filter(sample_rate, center=2000, gain_db=3.0, q=1.5)
        filtered = sosfilt(sos_mid, filtered)
        
        # Yeniden AudioSegment'e dönüştür
        filtered = np.clip(filtered, -32768, 32767).astype(np.int16)
        
        processed_audio = AudioSegment(
            filtered.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        
        return processed_audio
    
    def _design_highshelf_filter(self, fs, cutoff, gain_db, order=2):
        """High-shelf filter tasarla"""
        nyq = fs / 2
        normalized_cutoff = cutoff / nyq
        
        # Gain'i linear scale'e çevir
        gain = 10 ** (gain_db / 20)
        
        # Butterworth high-pass filter + gain
        sos = butter(order, normalized_cutoff, btype='high', output='sos')
        return sos
    
    def _design_peaking_filter(self, fs, center, gain_db, q):
        """Peaking EQ filter (band-boost)"""
        nyq = fs / 2
        normalized_center = center / nyq
        bandwidth = normalized_center / q
        
        # Band-pass filter
        low = normalized_center - bandwidth / 2
        high = normalized_center + bandwidth / 2
        
        sos = butter(2, [low, high], btype='band', output='sos')
        return sos
    
    def reduce_noise(self, file_path):
        """
        Gelişmiş gürültü azaltma (spectral subtraction)
        """
        # librosa ile yükle (daha iyi kalite)
        y, sr = librosa.load(file_path, sr=None)
        
        # Gürültü azaltma uygula
        reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8, stationary=True)
        
        return reduced_noise, sr
    
    def apply_compression(self, audio, threshold=-20.0, ratio=4.0):
        """
        Dinamik aralık kompresyonu
        Args:
            threshold: Kompresyon başlangıç seviyesi (dBFS)
            ratio: Kompresyon oranı
        """
        return compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
    
    def process_full(self, input_path, output_path, apply_nr=True, brightness_boost=6.0):
        """
        Tam ön işleme pipeline
        
        Args:
            input_path: Giriş ses dosyası yolu
            output_path: Çıkış ses dosyası yolu
            apply_nr: Gürültü azaltma uygula (True/False)
            brightness_boost: Parlaklık artışı miktarı (dB)
        """
        print(f"İşleniyor: {input_path}")
        
        # 1. Gürültü azaltma (opsiyonel ama önerilen)
        if apply_nr:
            print("  → Gürültü azaltılıyor...")
            cleaned_audio, sr = self.reduce_noise(input_path)
            
            # Geçici dosyaya kaydet
            temp_path = "temp_cleaned.wav"
            sf.write(temp_path, cleaned_audio, sr)
            
            audio = self.load_audio(temp_path)
            os.remove(temp_path)
        else:
            audio = self.load_audio(input_path)
        
        # 2. Normalizasyon
        print("  → Ses seviyesi normalize ediliyor...")
        audio = self.normalize_audio(audio)
        
        # 3. Ekolayzer (parlaklık)
        print("  → Ekolayzer uygulanıyor (parlaklık artırılıyor)...")
        audio = self.apply_equalizer(audio, brightness_boost=brightness_boost)
        
        # 4. Kompresyon
        print("  → Dinamik aralık kompresyonu...")
        audio = self.apply_compression(audio)
        
        # 5. Son normalizasyon
        audio = self.normalize_audio(audio)
        
        # Kaydet
        audio.export(output_path, format="wav")
        print(f"✓ Tamamlandı: {output_path}")
        
        return output_path


def process_directory(input_dir, output_dir, **kwargs):
    """Bir klasördeki tüm ses dosyalarını işle"""
    preprocessor = AudioPreprocessor()
    
    # Desteklenen formatlar
    audio_extensions = ('.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac')
    
    # Output klasörünü oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    # Tüm ses dosyalarını bul ve işle
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(audio_extensions):
            input_path = os.path.join(input_dir, filename)
            output_filename = f"processed_{os.path.splitext(filename)[0]}.wav"
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                preprocessor.process_full(input_path, output_path, **kwargs)
            except Exception as e:
                print(f"✗ Hata ({filename}): {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ses dosyası ön işleme")
    parser.add_argument("input", help="Giriş dosyası veya klasör")
    parser.add_argument("-o", "--output", help="Çıkış dosyası veya klasör", default="output")
    parser.add_argument("--no-noise-reduction", action="store_true", help="Gürültü azaltma yapma")
    parser.add_argument("--brightness", type=float, default=6.0, help="Parlaklık artışı (dB, varsayılan: 6.0)")
    parser.add_argument("--target-db", type=float, default=-20.0, help="Hedef desibel seviyesi (varsayılan: -20.0)")
    
    args = parser.parse_args()
    
    preprocessor = AudioPreprocessor(target_dbfs=args.target_db)
    
    # Tek dosya mı klasör mü?
    if os.path.isfile(args.input):
        # Tek dosya işle
        output_path = args.output if args.output != "output" else f"processed_{os.path.basename(args.input)}"
        preprocessor.process_full(
            args.input,
            output_path,
            apply_nr=not args.no_noise_reduction,
            brightness_boost=args.brightness
        )
    elif os.path.isdir(args.input):
        # Klasör işle
        process_directory(
            args.input,
            args.output,
            apply_nr=not args.no_noise_reduction,
            brightness_boost=args.brightness
        )
    else:
        print(f"Hata: '{args.input}' bulunamadı!")

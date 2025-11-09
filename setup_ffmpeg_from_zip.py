"""
Indirilen FFmpeg ZIP dosyasindan kurulum
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path


def find_ffmpeg_zip():
    """Downloads klasöründe FFmpeg ZIP'ini bul."""
    downloads = Path.home() / "Downloads"

    if downloads.exists():
        # ffmpeg ile başlayan ZIP dosyalarını bul
        zips = list(downloads.glob("ffmpeg*.zip"))
        if zips:
            # En son indirilenini al
            latest = max(zips, key=lambda p: p.stat().st_mtime)
            return latest

    return None


def extract_and_setup(zip_path):
    """ZIP'i çıkart ve kur."""
    print(f"\nZIP dosyasi: {zip_path}")

    # Kurulum dizini
    install_dir = Path.home() / "ffmpeg"
    install_dir.mkdir(parents=True, exist_ok=True)

    print(f"Kurulum dizini: {install_dir}")
    print()

    # ZIP'i çıkart
    print("Dosyalar cikartiliyor...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Toplam dosya sayısı
            total = len(zip_ref.namelist())
            print(f"Toplam {total} dosya cikartiliyor...")

            zip_ref.extractall(install_dir)

        print("Cikarma tamamlandi!")
    except Exception as e:
        print(f"HATA: {e}")
        return False

    # İçindeki ana klasörü bul
    extracted_folders = [f for f in install_dir.iterdir() if f.is_dir() and f.name.startswith("ffmpeg")]

    if not extracted_folders:
        print("HATA: FFmpeg klasoru bulunamadi!")
        return False

    main_folder = extracted_folders[0]
    bin_source = main_folder / "bin"

    if not bin_source.exists():
        print("HATA: bin klasoru bulunamadi!")
        return False

    # bin klasörünü ana dizine kopyala
    bin_dest = install_dir / "bin"

    if bin_dest.exists():
        shutil.rmtree(bin_dest)

    shutil.copytree(bin_source, bin_dest)
    print(f"\nbin klasoru tasindi: {bin_dest}")

    # Ana klasörü sil (artık gereksiz)
    shutil.rmtree(main_folder)

    # PATH'e ekle (bu oturum için)
    current_path = os.environ.get('PATH', '')
    if str(bin_dest) not in current_path:
        os.environ['PATH'] = f"{bin_dest};{current_path}"
        print(f"PATH'e eklendi (bu oturum icin): {bin_dest}")

    return bin_dest


def test_ffmpeg():
    """FFmpeg'i test et."""
    print("\nFFmpeg test ediliyor...")
    print("="*50)
    result = os.system("ffmpeg -version")
    print("="*50)
    return result == 0


def main():
    print("\n" + "="*70)
    print(" FFMPEG KURULUM (INDIRILEN ZIP'TEN) ".center(70, "="))
    print("="*70 + "\n")

    # ZIP'i bul
    zip_path = find_ffmpeg_zip()

    if zip_path:
        print(f"FFmpeg ZIP bulundu: {zip_path.name}")
        print(f"Boyut: {zip_path.stat().st_size / (1024*1024):.1f} MB")
        print()

        response = input("Bu dosyayi kullanalim mi? (E/H): ").strip().lower()
        if response not in ['e', 'y', 'yes', 'evet']:
            zip_path = None

    # Manuel yol girişi
    if not zip_path:
        print("\nZIP dosyasinin tam yolunu girin:")
        print("Ornek: C:\\Users\\username\\Downloads\\ffmpeg-release-essentials.zip")
        zip_input = input("\nZIP yolu: ").strip().strip('"')

        zip_path = Path(zip_input)

        if not zip_path.exists():
            print(f"\nHATA: Dosya bulunamadi: {zip_path}")
            return

    # Kurulumu yap
    bin_path = extract_and_setup(zip_path)

    if not bin_path:
        print("\nKURULUM BASARISIZ!")
        return

    # Test et
    if test_ffmpeg():
        print("\n" + "="*70)
        print(" KURULUM BASARILI! ".center(70, "="))
        print("="*70)
        print()
        print(f"FFmpeg kuruldu: {bin_path}")
        print()
        print("ONEMLI:")
        print("- Bu oturum icin PATH eklendi")
        print("- Yeni terminal actiginizda tekrar eklenmesi gerekebilir")
        print()
        print("KALICI OLARAK EKLEMEK ICIN:")
        print("1. Windows Ayarlari > Sistem > Hakkinda")
        print("2. 'Gelismis sistem ayarlari' > 'Ortam Degiskenleri'")
        print("3. 'Path' degiskenini secin > 'Duzenle' > 'Yeni'")
        print(f"4. Ekleyin: {bin_path}")
        print()
        print("SIMDI WEB ARAYUZUNU CALISTIRABILIRSINIZ:")
        print("  python web_ui.py")
        print()
    else:
        print("\nUYARI: FFmpeg test edilemedi!")
        print(f"Manuel kontrol edin: {bin_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nIptal edildi")
    except Exception as e:
        print(f"\n\nHATA: {e}")
        import traceback
        traceback.print_exc()

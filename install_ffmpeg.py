"""
FFmpeg otomatik kurulum scripti (Windows)
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path


def download_file(url, destination):
    """Dosyayı indir."""
    print(f"Indiriliyor: {url}")
    print("Bu birkaç dakika sürebilir...")

    try:
        urllib.request.urlretrieve(url, destination, reporthook=download_progress)
        print("\nIndirme tamamlandi!")
        return True
    except Exception as e:
        print(f"\nHata: {e}")
        return False


def download_progress(block_num, block_size, total_size):
    """İndirme ilerlemesini göster."""
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100)
    sys.stdout.write(f"\rIlerleme: {percent:.1f}%")
    sys.stdout.flush()


def extract_zip(zip_path, extract_to):
    """ZIP dosyasını çıkart."""
    print(f"\nCikartiliyor: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Cikarma tamamlandi!")
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False


def add_to_path(directory):
    """PATH'e ekle (sadece mevcut session için)."""
    current_path = os.environ.get('PATH', '')
    if directory not in current_path:
        os.environ['PATH'] = f"{directory};{current_path}"
        print(f"PATH'e eklendi: {directory}")
        return True
    return False


def main():
    print("\n" + "="*70)
    print(" FFMPEG OTOMATIK KURULUM ".center(70, "="))
    print("="*70 + "\n")

    # FFmpeg URL (güncel stable release)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

    # Kurulum dizini
    install_dir = Path.home() / "ffmpeg"
    download_path = Path.home() / "ffmpeg.zip"

    print("FFmpeg kurulacak dizin:", install_dir)
    print()

    # Zaten kurulu mu kontrol et
    if (install_dir / "bin" / "ffmpeg.exe").exists():
        print("FFmpeg zaten kurulu!")
        print(f"Konum: {install_dir / 'bin'}")

        # PATH'e ekle
        add_to_path(str(install_dir / "bin"))

        print("\nTest ediliyor...")
        os.system("ffmpeg -version")
        return

    # Dizini oluştur
    install_dir.mkdir(parents=True, exist_ok=True)

    # FFmpeg'i indir
    print("1. FFmpeg indiriliyor...")
    if not download_file(ffmpeg_url, download_path):
        print("\nINDIRME BASARISIZ!")
        print("Manuel kurulum icin: https://www.gyan.dev/ffmpeg/builds/")
        return

    # ZIP'i çıkart
    print("\n2. Dosyalar cikartiliyor...")
    if not extract_zip(download_path, install_dir):
        print("\nCIKARMA BASARISIZ!")
        return

    # İndirilen ZIP'in içindeki ana klasörü bul
    extracted_folders = [f for f in install_dir.iterdir() if f.is_dir()]
    if extracted_folders:
        main_folder = extracted_folders[0]

        # bin klasörünü ana dizine taşı
        bin_source = main_folder / "bin"
        bin_dest = install_dir / "bin"

        if bin_source.exists():
            shutil.copytree(bin_source, bin_dest, dirs_exist_ok=True)
            print(f"Dosyalar tasindi: {bin_dest}")

    # ZIP dosyasını sil
    if download_path.exists():
        download_path.unlink()
        print("Gecici dosyalar silindi")

    # PATH'e ekle (mevcut session için)
    bin_path = install_dir / "bin"
    if bin_path.exists():
        add_to_path(str(bin_path))

        print("\n" + "="*70)
        print(" KURULUM TAMAMLANDI! ".center(70, "="))
        print("="*70)
        print()
        print(f"FFmpeg kuruldu: {bin_path}")
        print()
        print("ONEMLI: PATH kalici olarak eklenmedi!")
        print()
        print("Kalici olarak eklemek icin:")
        print("1. Windows Ayarlari > Sistem > Hakkinda > Gelismis sistem ayarlari")
        print("2. 'Ortam Degiskenleri' butonuna tiklayin")
        print("3. 'Path' degiskenini secin ve 'Duzenle' tiklayin")
        print("4. 'Yeni' tiklayin ve ekleyin:")
        print(f"   {bin_path}")
        print()
        print("VEYA bu scripti her seferinde calistirin")
        print()

        # Test et
        print("Test ediliyor...")
        os.system("ffmpeg -version")
        print()
        print("Simdi web_ui.py'yi tekrar calistirabilirsiniz!")
    else:
        print("\nHATA: bin klasoru bulunamadi!")
        print("Manuel kurulum yapmaniz gerekebilir")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKurulum iptal edildi")
    except Exception as e:
        print(f"\n\nBEKLENMEYEN HATA: {e}")
        import traceback
        traceback.print_exc()

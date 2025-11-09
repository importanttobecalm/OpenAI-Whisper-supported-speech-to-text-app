#!/usr/bin/env python3
"""
Whisper Transcription - Mac Application Launcher
Tek tıkla çalışan Mac uygulaması için launcher
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
from pathlib import Path
import webbrowser
import time

class WhisperAppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Transcription")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Ortala pencereyi
        self.center_window()
        
        # Stil
        style = ttk.Style()
        style.theme_use('aqua')  # Mac native tema
        
        self.server_process = None
        self.server_url = "http://127.0.0.1:7865"
        
        self.create_widgets()
        
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Arayüz öğelerini oluştur"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#0066cc", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🎙️ Whisper Transcription",
            font=("Helvetica", 24, "bold"),
            bg="#0066cc",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Ana içerik
        content_frame = tk.Frame(self.root, padx=30, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Açıklama
        desc_label = tk.Label(
            content_frame,
            text="Ses dosyalarını metne dönüştürün",
            font=("Helvetica", 14),
            fg="#666666"
        )
        desc_label.pack(pady=(0, 30))
        
        # Gemini API Key Section
        api_frame = ttk.LabelFrame(content_frame, text="🤖 Gemini API Ayarları (Opsiyonel)", padding=15)
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        api_info = tk.Label(
            api_frame,
            text="Gemini ile metin iyileştirme için API anahtarınızı girin",
            font=("Helvetica", 10),
            fg="#666666"
        )
        api_info.pack(anchor=tk.W, pady=(0, 10))
        
        self.api_key_var = tk.StringVar()
        api_entry_frame = tk.Frame(api_frame)
        api_entry_frame.pack(fill=tk.X)
        
        self.api_key_entry = ttk.Entry(
            api_entry_frame,
            textvariable=self.api_key_var,
            show="*",
            font=("Helvetica", 11)
        )
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        save_api_btn = ttk.Button(
            api_entry_frame,
            text="💾 Kaydet",
            command=self.save_api_key
        )
        save_api_btn.pack(side=tk.LEFT)
        
        api_link = tk.Label(
            api_frame,
            text="API anahtarı alın: makersuite.google.com/app/apikey",
            font=("Helvetica", 9),
            fg="#0066cc",
            cursor="hand2"
        )
        api_link.pack(anchor=tk.W, pady=(5, 0))
        api_link.bind("<Button-1>", lambda e: webbrowser.open("https://makersuite.google.com/app/apikey"))
        
        # Durum
        self.status_label = tk.Label(
            content_frame,
            text="⏳ Hazır - Başlatmak için butona tıklayın",
            font=("Helvetica", 12),
            fg="#666666"
        )
        self.status_label.pack(pady=20)
        
        # Butonlar
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            button_frame,
            text="🚀 Web Arayüzünü Başlat",
            command=self.start_server,
            font=("Helvetica", 14, "bold"),
            bg="#0066cc",
            fg="white",
            padx=30,
            pady=15,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Durdur",
            command=self.stop_server,
            font=("Helvetica", 12),
            bg="#dc3545",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED,
            relief=tk.FLAT
        )
        self.stop_btn.pack(pady=5)
        
        # Footer bilgi
        info_text = "Uygulama tarayıcınızda otomatik açılacak"
        info_label = tk.Label(
            content_frame,
            text=info_text,
            font=("Helvetica", 10),
            fg="#999999"
        )
        info_label.pack(side=tk.BOTTOM, pady=10)
        
        # API anahtarını yükle
        self.load_api_key()
        
    def save_api_key(self):
        """API anahtarını kaydet"""
        api_key = self.api_key_var.get().strip()
        
        if not api_key:
            messagebox.showwarning("Uyarı", "API anahtarı boş olamaz")
            return
            
        # .env dosyasına kaydet
        env_path = Path.home() / ".whisper_app_env"
        try:
            with open(env_path, "w") as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
            
            # Ortam değişkenine de ekle
            os.environ["GEMINI_API_KEY"] = api_key
            
            messagebox.showinfo("Başarılı", "API anahtarı kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", f"API anahtarı kaydedilemedi: {e}")
    
    def load_api_key(self):
        """Kaydedilmiş API anahtarını yükle"""
        env_path = Path.home() / ".whisper_app_env"
        
        if env_path.exists():
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            self.api_key_var.set(api_key)
                            os.environ["GEMINI_API_KEY"] = api_key
                            break
            except Exception:
                pass
    
    def check_dependencies(self):
        """Gerekli kütüphaneleri kontrol et"""
        try:
            import gradio
            import whisper
            return True
        except ImportError as e:
            missing = str(e).split("'")[1]
            response = messagebox.askyesno(
                "Eksik Kütüphane",
                f"'{missing}' kütüphanesi yüklü değil.\n\nŞimdi yüklemek ister misiniz?"
            )
            if response:
                self.install_dependencies()
                return False
            return False
    
    def install_dependencies(self):
        """Gerekli kütüphaneleri yükle"""
        self.status_label.config(text="📦 Kütüphaneler yükleniyor...", fg="#ff8c00")
        self.start_btn.config(state=tk.DISABLED)
        
        def install():
            try:
                # requirements.txt dosyasını bul
                app_dir = Path(__file__).parent.parent
                req_files = [
                    app_dir / "requirements_audio.txt",
                    app_dir / "requirements_gemini.txt"
                ]
                
                for req_file in req_files:
                    if req_file.exists():
                        subprocess.check_call([
                            sys.executable, "-m", "pip", "install", "-r", str(req_file)
                        ])
                
                self.status_label.config(
                    text="✅ Kütüphaneler yüklendi! Tekrar başlatın.",
                    fg="#28a745"
                )
                messagebox.showinfo(
                    "Başarılı",
                    "Gerekli kütüphaneler yüklendi!\nŞimdi uygulamayı başlatabilirsiniz."
                )
                
            except Exception as e:
                self.status_label.config(text="❌ Yükleme başarısız", fg="#dc3545")
                messagebox.showerror("Hata", f"Kütüphane yüklenemedi:\n{e}")
            finally:
                self.start_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=install, daemon=True)
        thread.start()
    
    def start_server(self):
        """Web sunucusunu başlat"""
        if not self.check_dependencies():
            return
        
        self.status_label.config(text="🔄 Başlatılıyor...", fg="#ff8c00")
        self.start_btn.config(state=tk.DISABLED)
        
        def run_server():
            try:
                # web_ui.py dosyasının yolunu bul
                app_dir = Path(__file__).parent.parent
                web_ui_path = app_dir / "web_ui.py"
                
                if not web_ui_path.exists():
                    raise FileNotFoundError("web_ui.py bulunamadı")
                
                # Python scripti çalıştır
                self.server_process = subprocess.Popen(
                    [sys.executable, str(web_ui_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(app_dir)
                )
                
                # Sunucunun başlamasını bekle
                time.sleep(3)
                
                # Tarayıcıda aç
                webbrowser.open(self.server_url)
                
                self.status_label.config(
                    text="✅ Çalışıyor - Tarayıcınızda açıldı",
                    fg="#28a745"
                )
                self.stop_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                self.status_label.config(text="❌ Başlatılamadı", fg="#dc3545")
                self.start_btn.config(state=tk.NORMAL)
                messagebox.showerror("Hata", f"Sunucu başlatılamadı:\n{e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
    
    def stop_server(self):
        """Web sunucusunu durdur"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            
        self.status_label.config(text="⏹ Durduruldu", fg="#666666")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Pencere kapatıldığında"""
        if self.server_process:
            if messagebox.askokcancel("Çıkış", "Sunucu çalışıyor. Kapatmak istediğinizden emin misiniz?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = WhisperAppLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

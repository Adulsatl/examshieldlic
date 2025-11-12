#!/usr/bin/env python3
"""
ExamShield v2.6 — Secure Exam Monitoring System
Developed by Adul Sureshkumar
------------------------------------------------------------
Features:
✅ Multi-user Telegram broadcast
✅ USB detection + block in exam mode
✅ Browser blocking + restoration
✅ Professional alert formatting (Markdown)
✅ /exam, /normal, /logs, /start commands
------------------------------------------------------------
"""

import os, sys, json, time, threading, socket, logging, signal, psutil
from datetime import datetime

# License verification - Cross-platform support
LICENSE_ENABLED = False
try:
    # Try Linux path first
    sys.path.insert(0, '/opt/examshield')
    import license
    LICENSE_ENABLED = True
except ImportError:
    try:
        # Try Windows/current directory
        import sys
        import os
        license_path = os.path.join(os.path.dirname(__file__), 'license.py')
        if os.path.exists(license_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("license", license_path)
            license = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(license)
            LICENSE_ENABLED = True
        else:
            # Try client directory
            client_license = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', 'license.py')
            if os.path.exists(client_license):
                import importlib.util
                spec = importlib.util.spec_from_file_location("license", client_license)
                license = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(license)
                LICENSE_ENABLED = True
    except Exception as e:
        LICENSE_ENABLED = False
        logging.warning(f"License module not found. Running without license verification. ({e})")

try:
    import pyudev
    from telegram import Bot, Update
    from telegram.ext import Updater, CommandHandler, CallbackContext
except ImportError:
    print("Missing dependencies. Run: sudo pip3 install pyudev python-telegram-bot==13.15 psutil")
    sys.exit(1)

# ----------------------------------------------------------------
# Configuration paths
# ----------------------------------------------------------------
CONFIG_FILE = '/etc/examshield/config.json'
CHAT_LIST_FILE = '/etc/examshield/chatlist.json'
LOG_DIR = '/var/log/examshield'
USB_LOG = os.path.join(LOG_DIR, 'usb.log')
STATE_FILE = '/var/lib/examshield/state.json'
HOSTNAME = socket.gethostname()

# ----------------------------------------------------------------
# System settings
# ----------------------------------------------------------------
BROWSERS = [
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/usr/bin/firefox', '/usr/bin/brave-browser', '/usr/bin/microsoft-edge'
]
DESKTOP_FILES = [
    '/usr/share/applications/google-chrome.desktop',
    '/usr/share/applications/chromium.desktop',
    '/usr/share/applications/firefox.desktop',
    '/usr/share/applications/brave-browser.desktop',
    '/usr/share/applications/microsoft-edge.desktop'
]

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOG_DIR, 'examshield.log'),
    format='%(asctime)s %(levelname)s: %(message)s'
)
logging.getLogger('').addHandler(logging.StreamHandler())

# ----------------------------------------------------------------
def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ----------------------------------------------------------------
class Config:
    def __init__(self, path=CONFIG_FILE):
        self.path = path
        self.data = {}
        if os.path.exists(path):
            try:
                with open(path) as f:
                    self.data = json.load(f)
            except Exception:
                logging.exception('Failed to read config')

    @property
    def token(self):
        return self.data.get('bot_token')

    @property
    def chat_id(self):
        return self.data.get('chat_id')


cfg = Config()

# ----------------------------------------------------------------
# Chat list management
# ----------------------------------------------------------------
def load_chatlist():
    if os.path.exists(CHAT_LIST_FILE):
        try:
            with open(CHAT_LIST_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_chatlist(chats):
    os.makedirs(os.path.dirname(CHAT_LIST_FILE), exist_ok=True)
    with open(CHAT_LIST_FILE, "w") as f:
        json.dump(list(set(chats)), f, indent=2)

# ----------------------------------------------------------------
# Telegram broadcast
# ----------------------------------------------------------------
def send_telegram(event, details):
    if not cfg.token:
        logging.warning("Telegram not configured.")
        return

    bot = Bot(token=cfg.token)
    chats = load_chatlist()
    if not chats:
        # fallback to single chat_id if no list yet
        if cfg.chat_id:
            chats = [cfg.chat_id]
        else:
            logging.warning("No chatlist or default chat id found.")
            return

    msg = (
        f"🧠 *ExamShield Alert*\n"
        f"🖥 *Host:* {HOSTNAME}\n"
        f"🕒 *Time:* {now_str()}\n"
        f"🚨 *Event:* {event}\n"
        f"📝 *Details:* {details}"
    )

    for chat in chats:
        try:
            bot.send_message(chat_id=chat, text=msg, parse_mode="Markdown")
        except Exception as e:
            logging.warning(f"Failed to send alert to {chat}: {e}")

# ----------------------------------------------------------------
def log_usb_event(text):
    line = f"[{now_str()}] {text}\n"
    with open(USB_LOG, 'a') as f:
        f.write(line)
    logging.info(text)

# ----------------------------------------------------------------
class USBMonitor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by('usb')

    def run(self):
        logging.info("USB monitor active.")
        for device in iter(self.monitor.poll, None):
            try:
                action = device.action
                if action not in ('add', 'remove'):
                    continue
                vendor = device.get('ID_VENDOR') or 'unknown'
                model = device.get('ID_MODEL') or 'unknown'
                serial = device.get('ID_SERIAL_SHORT') or 'unknown'
                msg = f"USB {action.upper()} — {vendor} {model} ({serial})"
                log_usb_event(msg)
                send_telegram(f"USB {action.upper()}", f"{vendor} {model} ({serial})")

                # Block USBs during exam mode
                if exam_ctrl.in_exam and action == 'add':
                    os.system("for d in /sys/bus/usb/devices/*; do echo 0 > $d/authorized 2>/dev/null; done")
                    os.system("sudo beep -f 900 -l 250 || echo -e '\\a'")
                    send_telegram("USB Blocked", "A USB device was blocked during exam mode.")
            except Exception:
                logging.exception("USB monitor error")

# ----------------------------------------------------------------
class ExamModeController:
    def __init__(self):
        self.in_exam = False
        self._saved_execs = {}

    def _kill_browsers(self):
        count = 0
        for p in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                exe = (p.info['exe'] or '').lower()
                if any(b in exe for b in ('chrome', 'firefox', 'brave', 'edge', 'chromium')):
                    p.kill()
                    count += 1
            except Exception:
                pass
        return count

    def _disable_browsers(self):
        for path in BROWSERS:
            if os.path.exists(path):
                st = os.stat(path)
                self._saved_execs[path] = st.st_mode
                os.chmod(path, st.st_mode & ~0o111)
        for d in DESKTOP_FILES:
            if os.path.exists(d):
                os.rename(d, d + '.disabled')

    def _restore_browsers(self):
        for path, mode in self._saved_execs.items():
            os.chmod(path, mode)
        for d in DESKTOP_FILES:
            if os.path.exists(d + '.disabled'):
                os.rename(d + '.disabled', d)

    def enter_exam(self):
        if self.in_exam:
            return False
        killed = self._kill_browsers()
        self._disable_browsers()
        self.in_exam = True
        send_telegram("Exam Mode ENABLED", f"Browsers closed ({killed} processes). USB access restricted.")
        logging.info("Exam mode ON")
        return True

    def exit_exam(self):
        if not self.in_exam:
            return False
        self._restore_browsers()
        self.in_exam = False
        os.system("for d in /sys/bus/usb/devices/*; do echo 1 > $d/authorized 2>/dev/null; done")
        send_telegram("Exam Mode DISABLED", "System restored to normal state.")
        logging.info("Exam mode OFF")
        return True

exam_ctrl = ExamModeController()

# ----------------------------------------------------------------
class TelegramCommandThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.updater = None

    def run(self):
        if not cfg.token:
            logging.warning("Telegram not configured.")
            return

        self.updater = Updater(cfg.token, use_context=True)
        dp = self.updater.dispatcher
        chats = load_chatlist()

        # Register new users
        def start(update: Update, context: CallbackContext):
            cid = update.effective_chat.id
            if cid not in chats:
                chats.append(cid)
                save_chatlist(chats)
                logging.info(f"Added new chat ID: {cid}")
            update.message.reply_text(
                f"✅ Registered for ExamShield alerts.\nHost: {HOSTNAME}\nYou will now receive alerts."
            )

        def exam(update: Update, context: CallbackContext):
            ok = exam_ctrl.enter_exam()
            update.message.reply_text(f'Exam mode enabled: {ok}')

        def normal(update: Update, context: CallbackContext):
            ok = exam_ctrl.exit_exam()
            update.message.reply_text(f'Exam mode disabled: {ok}')

        def logs(update: Update, context: CallbackContext):
            try:
                with open(USB_LOG, 'r') as f:
                    lines = f.readlines()[-10:]
                text = f"🧾 Last 10 USB logs ({HOSTNAME}):\n" + ''.join(lines)
            except Exception:
                text = "No logs available."
            update.message.reply_text(text)

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("exam", exam))
        dp.add_handler(CommandHandler("normal", normal))
        dp.add_handler(CommandHandler("logs", logs))

        send_telegram("System Online", "ExamShield daemon is now active.")
        logging.info("Telegram listener active.")
        self.updater.start_polling()
        self.updater.idle()

# ----------------------------------------------------------------
def signal_handler(sig, frame):
    logging.info(f"Received signal {sig}, exiting gracefully.")
    sys.exit(0)

# ----------------------------------------------------------------
def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # License verification
    if LICENSE_ENABLED:
        logging.info("Checking license status...")
        if not license.check_and_exit_if_invalid():
            logging.error("License check failed. Exiting.")
            sys.exit(1)
        license_status = license.status()
        logging.info(f"License status: {license_status.get('status', 'unknown')} - {license_status.get('message', '')}")

    usbmon = USBMonitor(); usbmon.start()
    tg = TelegramCommandThread(); tg.start()

    while True:
        time.sleep(10)

# ----------------------------------------------------------------
if __name__ == "__main__":
    main()


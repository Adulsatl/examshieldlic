#!/usr/bin/env bash
set -e

PKG_NAME="examshield-installer"
VERSION="2.4"
ARCH="all"
BUILD_DIR="$(pwd)/build"
APP_DIR="$BUILD_DIR/opt/examshield"
DEBIAN_DIR="$BUILD_DIR/DEBIAN"

rm -rf "$BUILD_DIR"
mkdir -p "$APP_DIR" "$DEBIAN_DIR"

echo "📦 Preparing ExamShield v${VERSION}-auto-update build..."

# Copy logo
if [ -f "logo.png" ]; then
    cp logo.png "$APP_DIR/logo.png"
else
    echo "⚠️ logo.png not found — please add your logo in this folder."
fi

# Copy daemon
cp examshield.py "$APP_DIR/examshield.py"
chmod +x "$APP_DIR/examshield.py"

# Copy license module
if [ -f "client/license.py" ]; then
    cp client/license.py "$APP_DIR/license.py"
    chmod +x "$APP_DIR/license.py"
    echo "✅ License module included"
else
    echo "⚠️ client/license.py not found"
fi

# Create auto-updater
cat > "$APP_DIR/updater.sh" <<'EOF'
#!/usr/bin/env bash
set -e
PKG_PATH="/opt/examshield/ExamShield_Installer_v2.4-stable.deb"
VERSION_FILE="/etc/examshield/version"
SERVICE="examshield.service"

if [ ! -f "$PKG_PATH" ]; then
  echo "❌ Update package not found at $PKG_PATH"
  exit 1
fi

CURRENT_VER=$(cat "$VERSION_FILE" 2>/dev/null || echo "none")
NEW_VER="2.4"

if [ "$CURRENT_VER" == "$NEW_VER" ]; then
  echo "✅ ExamShield is already up to date (v$NEW_VER)"
  exit 0
fi

echo "🚀 Updating ExamShield from $CURRENT_VER → $NEW_VER..."
sudo dpkg -i "$PKG_PATH" >/dev/null 2>&1 || true
echo "$NEW_VER" | sudo tee "$VERSION_FILE" >/dev/null

sudo systemctl daemon-reload
sudo systemctl restart "$SERVICE"

echo "✅ ExamShield updated successfully to v$NEW_VER"
if [ -f "/etc/examshield/config.json" ]; then
  TOKEN=$(grep -oP '(?<="bot_token": ")[^"]*' /etc/examshield/config.json)
  CHAT=$(grep -oP '(?<="chat_id": ")[^"]*' /etc/examshield/config.json)
  if [ -n "$TOKEN" ] && [ -n "$CHAT" ]; then
    curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
      -d chat_id="$CHAT" -d text="✅ ExamShield auto-updated to v$NEW_VER on $(hostname)" >/dev/null
  fi
fi
EOF
chmod +x "$APP_DIR/updater.sh"

# Create installer GUI with license support
cat > "$APP_DIR/installer.py" <<'PY'
#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import json, os, subprocess, time, requests
from PIL import Image, ImageTk
CFG="/etc/examshield/config.json"; LOGO="/opt/examshield/logo.png"
VER_FILE="/etc/examshield/version"
VERIFY_URL=os.getenv("ES_VERIFY_URL","https://examshield-license-erver.onrender.com/verify")

def verify_key_online(key):
    """Verify license key online"""
    if not key or not key.strip():
        return True, "Trial mode"  # Blank key = trial mode
    try:
        import hashlib, socket, uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        hostname = socket.gethostname()
        fingerprint = hashlib.sha256(f"{mac}:{hostname}".encode()).hexdigest()
        r = requests.post(VERIFY_URL, json={"key": key.strip(), "device_fingerprint": fingerprint}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("valid"):
                return True, "License verified"
            else:
                return False, data.get("error", "License verification failed")
        else:
            err = r.json() if r.content else {}
            return False, err.get("error", f"Server error: {r.status_code}")
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to license server"
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def splash():
    s=tk.Tk(); s.overrideredirect(True); s.configure(bg="#0b3d91")
    w,h=520,300; sw,sh=s.winfo_screenwidth(),s.winfo_screenheight()
    s.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    if os.path.exists(LOGO):
        try: img=Image.open(LOGO).resize((150,150)); ph=ImageTk.PhotoImage(img)
        except: ph=None
        if ph: tk.Label(s,image=ph,bg="#0b3d91").pack(pady=(30,10)); s.photo=ph
    tk.Label(s,text="ExamShield",font=("Helvetica",22,"bold"),fg="white",bg="#0b3d91").pack()
    tk.Label(s,text="Secure Exam Environment",fg="white",bg="#0b3d91").pack()
    s.after(2500,s.destroy); s.mainloop()

def main_gui():
    root=tk.Tk(); root.title("ExamShield Setup Wizard")
    if os.path.exists(LOGO):
        try: ic=tk.PhotoImage(file=LOGO); root.iconphoto(False,ic)
        except: pass
    root.geometry("760x450"); root.configure(bg="#f5f6fa")
    main=ttk.Frame(root,padding=12); main.pack(fill="both",expand=True)
    left=ttk.Frame(main,width=240); left.pack(side="left",fill="y")
    right=ttk.Frame(main); right.pack(side="left",fill="both",expand=True,padx=(20,0))
    if os.path.exists(LOGO):
        try: img=Image.open(LOGO).resize((190,190)); ph=ImageTk.PhotoImage(img); tk.Label(left,image=ph).pack(pady=10); left.photo=ph
        except: pass
    tk.Label(left,text="ExamShield",font=("Helvetica",16,"bold")).pack()
    tk.Label(left,text="Developed by Adul Sureshkumar",font=("Helvetica",9)).pack()
    tk.Label(right,text="License Key (optional - leave blank for 7-day trial):",font=("Helvetica",10)).pack(anchor="w")
    e_license=ttk.Entry(right,width=50); e_license.pack(pady=(0,8))
    tk.Label(right,text="Telegram BOT TOKEN:",font=("Helvetica",10)).pack(anchor="w")
    e1=ttk.Entry(right,width=50); e1.pack(pady=(0,8))
    tk.Label(right,text="Telegram CHAT ID:",font=("Helvetica",10)).pack(anchor="w")
    e2=ttk.Entry(right,width=50); e2.pack(pady=(0,12))
    status=tk.Label(right,text="",fg="#333"); status.pack(anchor="w")
    bar=ttk.Progressbar(right,mode="indeterminate",length=380); bar.pack(pady=(8,4),anchor="w")

    def upd(t): status.config(text=t); status.update_idletasks()
    def run(cmd): return subprocess.run(cmd,shell=True)
    def test_bot(tk,chat):
        try:
            r=requests.post(f"https://api.telegram.org/bot{tk}/sendMessage",data={"chat_id":chat,"text":"✅ ExamShield connectivity OK"},timeout=10)
            return r.status_code==200
        except Exception: return False

    def install():
        license_key=e_license.get().strip()
        t=e1.get().strip(); c=e2.get().strip()
        if not t or not c: messagebox.showerror("Missing","Enter BOT TOKEN and CHAT ID"); return
        
        # Verify license key if provided
        if license_key:
            upd("Verifying license key...")
            valid, msg = verify_key_online(license_key)
            if not valid:
                messagebox.showerror("License Error", f"License verification failed:\n{msg}\n\nPlease check your license key or leave blank for trial mode.")
                return
            upd("License verified successfully")
        else:
            upd("No license key provided - trial mode will be activated")
        
        os.system("sudo mkdir -p /etc/examshield")
        json.dump({"bot_token":t,"chat_id":c},open(CFG,"w"))
        open(VER_FILE,"w").write("2.4")
        
        # Save license key if provided
        if license_key:
            license_data = {"key": license_key, "verified": True}
            json.dump(license_data, open("/etc/examshield/license.json", "w"), indent=2)
        
        bar.start(10); upd("Installing dependencies...")
        run("sudo apt update -y && sudo apt install -y python3 python3-pip python3-tk python3-psutil")
        run("sudo apt remove -y python3-pil || true")
        run("sudo -H pip3 install --upgrade pip")
        run("sudo -H pip3 install --no-cache-dir pyudev python-telegram-bot==13.15 psutil pillow requests")
        upd("Testing Telegram connectivity...")
        if test_bot(t,c):
            upd("Telegram OK — test message sent.")
        else:
            upd("⚠️ Telegram test failed.")
        service=f"""[Unit]
Description=ExamShield USB monitor
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
User=root
Environment=ES_VERIFY_URL={VERIFY_URL}
ExecStart=/usr/bin/python3 /opt/examshield/examshield.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
"""
        os.system(f"echo '{service}' | sudo tee /etc/systemd/system/examshield.service > /dev/null")
        upd("Enabling service..."); run("sudo systemctl daemon-reload && sudo systemctl enable --now examshield.service")
        bar.stop()
        if license_key:
            messagebox.showinfo("Done","✅ ExamShield installed & started.\nLicense activated.")
        else:
            messagebox.showinfo("Done","✅ ExamShield installed & started.\n7-day trial activated.")
        root.destroy()
    ttk.Button(right,text="Install & Activate",command=install).pack(anchor="w",pady=10)
    root.mainloop()

if __name__=="__main__": splash(); main_gui()
PY
chmod +x "$APP_DIR/installer.py"

# Debian package metadata and postinst
cat > "$DEBIAN_DIR/control" <<EOF
Package: $PKG_NAME
Version: $VERSION
Section: education
Priority: optional
Architecture: $ARCH
Maintainer: Adul S <aduls.career@gmail.com>
Description: ExamShield v$VERSION - Secure Exam Environment with Telegram Alerts
EOF

cat > "$DEBIAN_DIR/postinst" <<'EOF'
#!/bin/bash
echo "🚀 Launching ExamShield Setup Wizard..."
/usr/bin/python3 /opt/examshield/installer.py
EOF
chmod 755 "$DEBIAN_DIR/postinst"

# Build .deb
echo "🏗️ Building ExamShield Installer..."
dpkg-deb --build "$BUILD_DIR" ./ExamShield_Installer_v2.4-stable.deb
echo "✅ Build complete: $(pwd)/ExamShield_Installer_v2.4-stable.deb"


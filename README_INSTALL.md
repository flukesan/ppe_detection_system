# 🚀 Quick Installation Guide

เริ่มใช้งาน PPE Detection System ภายใน 5 นาที!

---

## 🐧 Ubuntu/Debian (Recommended)

### วิธีที่ 1: Auto Install Script ⭐ (แนะนำ)

```bash
# 1. Download โปรเจค
git clone <repository-url>
cd ppe_detection_system

# 2. รัน installation script
chmod +x install_ubuntu.sh
./install_ubuntu.sh

# รอ 5-15 นาที (ขึ้นอยู่กับความเร็วอินเทอร์เน็ต)

# 3. รันโปรแกรม
./run_ubuntu.sh
```

### วิธีที่ 2: Manual Install

```bash
# ติดตั้ง system packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip ffmpeg libxcb-xinerama0

# ติดตั้ง Python dependencies
pip3 install -r requirements.txt

# รัน
python3 main.py
```

---

## 🪟 Windows

### ขั้นตอนการติดตั้ง

**1. ติดตั้ง Python**
- ดาวน์โหลด: https://www.python.org/downloads/
- ✅ เช็ค "Add Python to PATH"

**2. เปิด Command Prompt และรันคำสั่ง:**

```cmd
cd ppe_detection_system
pip install -r requirements.txt
```

**3. รันโปรแกรม:**

```cmd
run_windows.bat
```

---

## 🍎 macOS

```bash
# ติดตั้ง Homebrew (ถ้ายังไม่มี)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# ติดตั้ง dependencies
brew install python@3.10 ffmpeg
pip3 install -r requirements.txt

# รัน
python3 main.py
```

---

## ✅ ตรวจสอบการติดตั้ง

```bash
python3 -c "import PyQt6; import cv2; import torch; print('✓ All OK!')"
```

---

## 🐛 แก้ปัญหา

### ❌ ModuleNotFoundError: No module named 'PyQt6'

**Ubuntu:**
```bash
./install_ubuntu.sh  # รัน auto install
```

**Windows:**
```cmd
pip install PyQt6
```

### ❌ Qt Wayland Error (Ubuntu)

```bash
./run_ubuntu.sh  # ใช้ script นี้แทน python3 main.py
```

---

## 📚 เอกสารเพิ่มเติม

- [Installation Guide ฉบับเต็ม](docs/INSTALLATION.md)
- [Quick Start Guide](docs/QUICKSTART.md)
- [Multi-Camera Setup](docs/MULTI_CAMERA_FUSION.md)

---

**Need Help?** อ่าน [Troubleshooting Guide](docs/UBUNTU_RTSP_TROUBLESHOOTING.md)

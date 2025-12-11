# Ubuntu Python 3.12+ Installation Fix

แก้ปัญหา "externally-managed-environment" บน Ubuntu 23.04+ และ Debian 12+

---

## 🐛 ปัญหา

เมื่อรัน `./install_ubuntu.sh` เจอ error:

```
error: externally-managed-environment

× This environment is externally managed
```

**สาเหตุ:** Python 3.12+ บน Ubuntu 23.04+/Debian 12+ ป้องกันไม่ให้ติดตั้ง packages ด้วย `pip` โดยตรง

---

## ✅ วิธีแก้ไข

### วิธีที่ 1: ใช้ Virtual Environment ⭐ (แนะนำ)

```bash
# รัน script ที่รองรับ venv
./install_ubuntu_venv.sh

# รันโปรแกรม (จะ activate venv อัตโนมัติ)
./run_ubuntu.sh
```

**ข้อดี:**
- ✅ ไม่ทำลาย system packages
- ✅ แยก dependencies ของโปรเจคออกจาก system
- ✅ ติดตั้งปลอดภัย
- ✅ แนะนำโดย Python/Ubuntu official

---

### วิธีที่ 2: ใช้ --break-system-packages ⚠️ (ไม่แนะนำ)

```bash
# แก้ไข install_ubuntu.sh เพิ่ม flag
pip3 install --break-system-packages -r requirements.txt
```

**ข้อเสีย:**
- ❌ อาจทำให้ system packages เสียได้
- ❌ อาจทำให้ระบบ unstable
- ⚠️ ใช้เฉพาะเมื่อรู้ว่าทำอะไรอยู่

---

### วิธีที่ 3: ติดตั้งผ่าน apt (สำหรับบาง packages)

```bash
# ติดตั้ง system packages ผ่าน apt
sudo apt install python3-opencv python3-numpy python3-yaml

# ส่วนที่เหลือติดตั้งใน venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Quick Start (Ubuntu 23.04+)

```bash
# 1. Clone repo
git clone <repo-url>
cd ppe_detection_system

# 2. ให้สิทธิ์ scripts
chmod +x install_ubuntu_venv.sh run_ubuntu.sh

# 3. ติดตั้งด้วย venv script
./install_ubuntu_venv.sh

# 4. รันโปรแกรม
./run_ubuntu.sh
```

---

## 📝 Manual Installation (ถ้า script ไม่ทำงาน)

```bash
# 1. ติดตั้ง system packages
sudo apt-get update
sudo apt-get install -y \
    python3-venv \
    python3-dev \
    python3-pip \
    ffmpeg \
    libavcodec-extra

# 2. สร้าง virtual environment
python3 -m venv venv

# 3. Activate venv
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. ติดตั้ง packages
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 6. รันโปรแกรม (ต้อง activate venv ก่อนทุกครั้ง)
source venv/bin/activate
python3 main.py
```

---

## 🔍 ตรวจสอบว่าติดตั้งสำเร็จ

```bash
# เปิด terminal ใหม่ในโฟลเดอร์โปรเจค

# ตรวจสอบ venv
ls -la venv/  # ควรเห็นโฟลเดอร์ bin/, lib/, etc.

# Activate venv
source venv/bin/activate

# ควรเห็น (venv) ที่หน้า prompt:
# (venv) user@host:~/ppe_detection_system$

# ตรวจสอบ packages
python3 -c "import PyQt6; import cv2; import torch; print('✓ OK')"
```

---

## 🆘 Troubleshooting

### Error: python3-venv not found

```bash
sudo apt-get install python3.12-venv
```

### Error: venv activation ไม่ทำงาน

```bash
# ตรวจสอบว่า venv ถูกสร้าง
ls -la venv/bin/activate

# ถ้าไม่มี ให้สร้างใหม่
rm -rf venv
python3 -m venv venv
```

### Error: pip ใน venv ใช้งานไม่ได้

```bash
# Activate venv ก่อน
source venv/bin/activate

# Upgrade pip ใน venv
python -m pip install --upgrade pip
```

---

## 📚 เอกสารเพิ่มเติม

- [PEP 668 - Externally Managed Environments](https://peps.python.org/pep-0668/)
- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [Ubuntu Python Policy](https://wiki.ubuntu.com/Python)

---

## 💡 คำแนะนำ

### ควรใช้ venv เสมอเมื่อ:
- ✅ พัฒนา Python projects
- ✅ ติดตั้ง dependencies ที่เฉพาะเจาะจง
- ✅ ทดสอบ packages เวอร์ชันต่างๆ
- ✅ แยก environments ของแต่ละโปรเจค

### ไม่ควรใช้ --break-system-packages เมื่อ:
- ❌ ไม่แน่ใจว่ามันทำอะไร
- ❌ ใช้งานระบบจริง (production)
- ❌ แชร์เครื่องกับคนอื่น
- ❌ ใช้ระบบสำคัญ (servers, workstations)

---

**Updated:** 2025-12-10
**Applies to:** Ubuntu 23.04+, Debian 12+, Python 3.12+

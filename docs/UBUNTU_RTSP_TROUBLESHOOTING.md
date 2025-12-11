# Ubuntu RTSP Troubleshooting Guide

คู่มือแก้ปัญหาสำหรับการรัน PPE Detection System บน Ubuntu พร้อม RTSP camera

## 🐛 ปัญหาที่พบบ่อย

### 1. H.264 Decoding Errors

```
[h264 @ 0x3c59d140] cabac decode of qscale diff failed at 74 1
[h264 @ 0x3c59d140] error while decoding MB 74 1, bytestream 13100
```

**สาเหตุ:**
- Network packet loss จาก RTSP stream
- RTSP stream quality ไม่เสถียร
- Bandwidth ไม่เพียงพอ

**วิธีแก้:**

1. **ใช้ TCP แทน UDP** (แก้ไขแล้วในโค้ด)
   ```python
   os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
   ```

2. **ลด FPS ของ RTSP camera** (ในไฟล์ `config.yaml`)
   ```yaml
   camera_configs:
     - fps: 15  # ลดจาก 30 เป็น 15
   ```

3. **ลด Resolution**
   ```yaml
   camera_configs:
     - width: 960   # ลดจาก 1280
       height: 540  # ลดจาก 720
   ```

4. **ตรวจสอบ Network**
   ```bash
   # Test RTSP stream
   ffplay rtsp://admin:wip50313@192.168.1.181:8554

   # Check latency
   ping 192.168.1.181
   ```

5. **ปรับ Bitrate บนกล้อง IP** (ถ้าเข้าถึงได้)
   - เข้า web interface ของกล้อง
   - ลด bitrate เป็น 2-4 Mbps
   - เปลี่ยน encoding เป็น H.264 baseline profile

### 2. Qt Wayland Display Error

```
qt.qpa.wayland: There are no outputs - creating placeholder screen
```

**สาเหตุ:** Qt พยายามใช้ Wayland compositor แต่ไม่สำเร็จ

**วิธีแก้ (เลือก 1 วิธี):**

#### วิธีที่ 1: ใช้ Launcher Script (แนะนำ) ✅

```bash
./run_ubuntu.sh
```

Script นี้จะ:
- ตั้งค่า `QT_QPA_PLATFORM=xcb` (บังคับใช้ X11)
- ปิด FFmpeg warnings
- รันโปรแกรม

#### วิธีที่ 2: Export Environment Variable

```bash
export QT_QPA_PLATFORM=xcb
python3 main.py
```

#### วิธีที่ 3: เพิ่มใน `.bashrc`

```bash
echo 'export QT_QPA_PLATFORM=xcb' >> ~/.bashrc
source ~/.bashrc
python3 main.py
```

## 🚀 วิธีการรันที่แนะนำ

### สำหรับ Ubuntu (ทั้งหมด)

```bash
# 1. ให้สิทธิ์ execute script (ครั้งแรกเท่านั้น)
chmod +x run_ubuntu.sh

# 2. รันผ่าน script
./run_ubuntu.sh

# หรือรัน multi-camera mode
./run_ubuntu.sh --config config.yaml
```

### ตรวจสอบ Dependencies

```bash
# ติดตั้ง required packages
sudo apt-get update
sudo apt-get install -y \
    python3-pyqt6 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    ffmpeg \
    libavcodec-extra
```

## 📊 ตั้งค่า RTSP ที่แนะนำ

### สำหรับ Network ไม่เสถียร

```yaml
multi_camera:
  camera_configs:
    - # USB Camera
      width: 1280
      height: 720
      fps: 30

    - # RTSP Camera (ลด quality)
      width: 960
      height: 540
      fps: 10
```

### สำหรับ Network ดี

```yaml
multi_camera:
  camera_configs:
    - # USB Camera
      width: 1280
      height: 720
      fps: 30

    - # RTSP Camera
      width: 1280
      height: 720
      fps: 15
```

## 🔧 Advanced Troubleshooting

### ตรวจสอบ RTSP Stream Details

```bash
# ดู stream information
ffprobe rtsp://admin:wip50313@192.168.1.181:8554

# ทดสอบ playback
ffplay -rtsp_transport tcp rtsp://admin:wip50313@192.168.1.181:8554
```

### ตรวจสอบ OpenCV RTSP Support

```python
import cv2
print(cv2.getBuildInformation())
# ตรวจสอบว่ามี FFMPEG support
```

### เปิด Debug Logs

```bash
# เปิด FFmpeg debug
export OPENCV_FFMPEG_LOGLEVEL=debug
export OPENCV_VIDEOIO_DEBUG=1
python3 main.py
```

### Monitor Network Usage

```bash
# ติดตั้ง iftop
sudo apt-get install iftop

# Monitor bandwidth
sudo iftop -i eth0  # หรือ wlan0
```

## ⚡ Performance Tips

### 1. ลดการใช้ CPU/GPU

```yaml
# config.yaml
multi_camera:
  num_cameras: 2
  camera_configs:
    - fps: 30  # USB
    - fps: 10  # RTSP (ลด FPS ลงมาก)

detection:
  frame_skip: 1  # Skip every other frame
```

### 2. ใช้ Hardware Acceleration

```bash
# ติดตั้ง VA-API (Intel GPU)
sudo apt-get install i965-va-driver

# ตั้งค่า environment
export LIBVA_DRIVER_NAME=i965
```

### 3. Network Optimization

```bash
# เพิ่ม network buffer size
sudo sysctl -w net.core.rmem_max=26214400
sudo sysctl -w net.core.rmem_default=26214400
```

## 📝 Error Messages และความหมาย

| Error | ความหมาย | วิธีแก้ |
|-------|---------|---------|
| `cabac decode failed` | H.264 corruption | ใช้ TCP transport |
| `error while decoding MB` | Macroblock error | ลด bitrate/FPS |
| `no outputs` | Wayland issue | ใช้ `QT_QPA_PLATFORM=xcb` |
| `Connection refused` | RTSP ไม่ได้เปิด | ตรวจสอบ IP camera |
| `Timeout` | Network slow | เพิ่ม timeout, ใช้ TCP |

## ✅ Checklist สำหรับ Production

- [ ] ใช้ `run_ubuntu.sh` สำหรับรัน
- [ ] ตั้ง RTSP FPS <= 15
- [ ] ใช้ TCP transport (ตั้งค่าแล้วในโค้ด)
- [ ] ทดสอบ RTSP stream ด้วย ffplay ก่อน
- [ ] ตรวจสอบ network latency < 50ms
- [ ] Monitor CPU/GPU usage
- [ ] ตั้งค่า timeout values
- [ ] เปิด error handling (ตั้งค่าแล้วในโค้ด)

## 🆘 ยังมีปัญหา?

1. **Check Logs**
   ```bash
   tail -f data/logs/app.log
   ```

2. **Test Cameras แยกกัน**
   ```bash
   # USB Camera
   python3 -c "import cv2; cap=cv2.VideoCapture(0); print(cap.isOpened())"

   # RTSP Camera
   ffplay -rtsp_transport tcp rtsp://admin:wip50313@192.168.1.181:8554
   ```

3. **Reduce Complexity**
   - ลองรัน single camera mode ก่อน
   - ทดสอบ USB camera เพียงอย่างเดียว
   - ทดสอบ RTSP camera เพียงอย่างเดียว
   - แล้วค่อยเปิด fusion mode

## 📞 การรายงานปัญหา

เมื่อรายงานปัญหา กรุณาแนบข้อมูล:

```bash
# System info
uname -a
python3 --version
pip3 list | grep -i opencv
pip3 list | grep -i pyqt

# Network test
ping 192.168.1.181
ffprobe rtsp://admin:wip50313@192.168.1.181:8554

# Run with debug
export OPENCV_FFMPEG_LOGLEVEL=debug
./run_ubuntu.sh 2>&1 | tee error_log.txt
```

---

**อัพเดท:** 2025-12-10
**Version:** 1.0.0

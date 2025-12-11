# Performance Optimization Guide

คู่มือแก้ปัญหา FPS ต่ำและเพิ่มประสิทธิภาพการตรวจจับ

---

## 🐛 ปัญหาที่พบบ่อย: FPS ต่ำ (9-15 FPS)

### สาเหตุหลัก

1. **ใช้ CPU แทน GPU** ⚠️ (สาเหตุที่พบบ่อยที่สุด!)
2. Resolution สูงเกินไป
3. RTSP network latency
4. Multi-camera mode ใช้ทรัพยากรมาก

---

## 🔍 วินิจฉัยปัญหา

### ขั้นตอนที่ 1: ตรวจสอบว่าใช้ GPU หรือไม่

```bash
# รัน diagnostic script
python3 check_gpu.py
```

**ผลลัพธ์ที่ควรเห็น (ถ้าใช้ GPU):**
```
✅ CUDA Available: True
✅ GPU 0: NVIDIA GeForce RTX 3060 (12.0 GB)
✅ Configured to use GPU
```

**ผลลัพธ์ที่บ่งบอกปัญหา:**
```
❌ CUDA Available: False  ← ใช้ CPU (ช้ามาก!)
❌ Configured to use CPU  ← Config ตั้งค่าผิด
```

---

## ✅ วิธีแก้ไข

### 1. เปิดใช้งาน GPU (แนะนำ!)

#### Ubuntu

**ตรวจสอบว่ามี NVIDIA GPU:**
```bash
lspci | grep -i nvidia
```

**ติดตั้ง NVIDIA Driver:**
```bash
# ติดตั้งอัตโนมัติ
sudo ubuntu-drivers autoinstall

# รีบูต
sudo reboot

# ตรวจสอบว่าติดตั้งสำเร็จ
nvidia-smi
```

**ติดตั้ง PyTorch with CUDA:**
```bash
# ถอน CPU version
pip3 uninstall torch torchvision

# ติดตั้ง GPU version
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**ตรวจสอบ:**
```bash
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"
# ควรได้: CUDA: True
```

#### Windows

1. ติดตั้ง [NVIDIA Driver](https://www.nvidia.com/download/index.aspx)
2. ติดตั้ง [CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive)
3. ติดตั้ง PyTorch with CUDA:
   ```cmd
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

---

### 2. ปรับแต่งประสิทธิภาพ (ถ้าไม่มี GPU)

#### วิธีที่ 1: ใช้ Optimization Script

```bash
./optimize_performance.sh

# เลือก:
# 2) Optimize for low-end hardware (CPU mode)
```

#### วิธีที่ 2: แก้ไข config.yaml เอง

```yaml
camera:
  width: 960   # ลดจาก 1280
  height: 540  # ลดจาก 720
  fps: 15      # ลดจาก 30

detection:
  use_gpu: false  # ถ้าไม่มี GPU
  frame_skip: 1   # Skip every other frame

multi_camera:
  camera_configs:
    - width: 960
      height: 540
      fps: 15
    - width: 640  # RTSP ใช้ resolution ต่ำกว่า
      height: 360
      fps: 10
```

---

### 3. ปรับแต่ง RTSP Camera

```yaml
multi_camera:
  camera_configs:
    - # USB Camera (ความละเอียดสูง)
      width: 1280
      height: 720
      fps: 20
      
    - # RTSP Camera (ความละเอียดต่ำ)
      width: 960
      height: 540
      fps: 10  # FPS ต่ำลด bandwidth
```

**เพิ่มเติมใน RTSP URL:**
```yaml
camera_sources:
  - "rtsp://admin:pass@192.168.1.100:554/stream?tcp"  # บังคับ TCP
```

---

### 4. ปิด Multi-Camera Mode ชั่วคราว

```yaml
multi_camera:
  enabled: false  # ทดสอบด้วย single camera ก่อน
```

---

## 📊 ตารางเปรียบเทียบ FPS

| Configuration | FPS (CPU) | FPS (GPU) | แนะนำ |
|---------------|-----------|-----------|-------|
| **1280x720 @ 30fps** | 8-12 | 30-40 | ❌ ช้าบน CPU |
| **960x540 @ 20fps** | 15-20 | 40-60 | ✅ สมดุลดี |
| **640x360 @ 15fps** | 20-25 | 50-80 | ⚠️ ความละเอียดต่ำ |
| **Multi-Camera (2)** | 5-10 | 15-25 | ⚠️ ต้องใช้ GPU |

---

## 🚀 Expected Performance

### Single Camera Mode

| Hardware | Resolution | Expected FPS |
|----------|------------|--------------|
| **CPU Only** (i5) | 960x540 | 15-20 FPS |
| **CPU Only** (i7) | 1280x720 | 12-18 FPS |
| **GPU** (GTX 1060) | 1280x720 | 30-40 FPS |
| **GPU** (RTX 3060) | 1280x720 | 50-70 FPS |

### Multi-Camera Mode (2 Cameras)

| Hardware | Resolution | Expected FPS |
|----------|------------|--------------|
| **CPU Only** | ❌ Not recommended | <10 FPS |
| **GPU** (GTX 1060) | 960x540 | 15-20 FPS |
| **GPU** (RTX 3060) | 1280x720 | 20-30 FPS |
| **GPU** (RTX 4070) | 1280x720 | 40-50 FPS |

---

## 🔧 Advanced Optimizations

### 1. TensorRT Optimization (Advanced)

```python
# Export model to TensorRT for faster inference
from ultralytics import YOLO
model = YOLO('yolov8m-pose.pt')
model.export(format='engine')  # Creates .engine file

# Use in config:
# path: "yolov8m-pose.engine"
```

### 2. Mixed Precision (FP16)

```yaml
detection:
  use_fp16: true  # Use half precision (faster, slight accuracy loss)
```

### 3. Batch Processing

```yaml
detection:
  batch_size: 2  # Process 2 frames at once (GPU only)
```

### 4. Model Size Selection

| Model | Speed | Accuracy | RAM | VRAM |
|-------|-------|----------|-----|------|
| **yolov8n-pose** | ⚡⚡⚡ | ⭐⭐ | 1GB | 2GB |
| **yolov8s-pose** | ⚡⚡ | ⭐⭐⭐ | 2GB | 3GB |
| **yolov8m-pose** | ⚡ | ⭐⭐⭐⭐ | 4GB | 5GB |

แก้ไขใน `config.yaml`:
```yaml
models:
  yolov8_pose:
    path: "yolov8n-pose.pt"  # เปลี่ยนเป็น n (nano) สำหรับความเร็ว
```

---

## 💡 Quick Fixes สำหรับปัญหาที่พบบ่อย

### ❌ FPS = 9-15 (ช้ามาก)

**สาเหตุ:** ใช้ CPU แทน GPU

**แก้ไข:**
```bash
python3 check_gpu.py
# ถ้า CUDA: False → ติดตั้ง NVIDIA driver + CUDA PyTorch
```

### ❌ FPS = 20-25 (ปานกลาง แต่อยากได้เร็วกว่า)

**สาเหตุ:** Resolution/FPS สูงเกินไป

**แก้ไข:**
```yaml
camera:
  width: 960
  height: 540
  fps: 20
```

### ❌ Multi-Camera FPS < 10

**สาเหตุ:** CPU ไม่พอ

**แก้ไข:**
1. ใช้ GPU
2. หรือปิด multi-camera mode
3. หรือลด resolution ทั้ง 2 กล้อง

### ❌ RTSP Camera หน่วงมาก

**สาเหตุ:** Network latency

**แก้ไข:**
```yaml
camera_configs:
  - fps: 10     # ลด FPS
    width: 640  # ลด resolution
```

---

## 📝 Troubleshooting Checklist

- [ ] รัน `python3 check_gpu.py`
- [ ] ตรวจสอบ `nvidia-smi` (ถ้ามี NVIDIA GPU)
- [ ] ตรวจสอบ `config.yaml` → `use_gpu: true`
- [ ] ตรวจสอบ `config.yaml` → `device: "cuda:0"`
- [ ] ลด resolution ถ้า FPS ยังต่ำ
- [ ] ลด FPS ของ RTSP camera
- [ ] ปิด multi-camera mode สำหรับทดสอบ
- [ ] ใช้ model ขนาดเล็ก (yolov8n แทน yolov8m)

---

## 🆘 ยังแก้ไม่ได้?

1. **รัน diagnostic:**
   ```bash
   python3 check_gpu.py > gpu_report.txt
   ```

2. **Check logs:**
   ```bash
   tail -f data/logs/app.log
   ```

3. **Monitor GPU usage:**
   ```bash
   watch -n 1 nvidia-smi
   ```

4. **Test with video file (not RTSP):**
   - ถ้า video file เร็ว = ปัญหาที่ RTSP
   - ถ้า video file ช้า = ปัญหาที่ GPU/CPU

---

**Updated:** 2025-12-10
**Version:** 1.0.0

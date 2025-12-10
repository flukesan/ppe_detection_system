# GPU vs CPU Configuration Guide

## Quick Check

Run this command to check GPU availability:

```bash
python check_gpu.py
```

## GPU Configuration (Recommended)

### Requirements
- NVIDIA GPU with CUDA support
- CUDA Toolkit 11.8+ installed
- PyTorch with CUDA support

### Configuration

**config.yaml:**
```yaml
detection:
  use_gpu: true
  gpu_device: 0

models:
  yolov8_pose:
    path: "yolov8m-pose.pt"  # Medium model
    device: "cuda:0"

  ppe_detection:
    path: "models/ppe_detection_best.pt"
    device: "cuda:0"
```

**Or via .env:**
```bash
USE_GPU=True
GPU_DEVICE=0
```

### Performance

| Resolution | Model Size | Expected FPS | GPU |
|------------|-----------|--------------|-----|
| 1280x720   | yolov8n   | 60-100       | RTX 3060+ |
| 1280x720   | yolov8m   | 40-60        | RTX 3060+ |
| 1280x720   | yolov8l   | 25-40        | RTX 3060+ |
| 1920x1080  | yolov8m   | 25-35        | RTX 3060+ |

## CPU Configuration (No GPU)

### Configuration

**config.yaml:**
```yaml
detection:
  use_gpu: false
  frame_skip: 1  # Skip every other frame

camera:
  width: 640     # Lower resolution
  height: 480
  fps: 15        # Lower FPS target

models:
  yolov8_pose:
    path: "yolov8n-pose.pt"  # Use Nano model (smallest)
    device: "cpu"

  ppe_detection:
    path: "models/ppe_detection_best.pt"
    device: "cpu"
```

**Or via .env:**
```bash
USE_GPU=False
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=15
```

### Performance

| Resolution | Model Size | Expected FPS | CPU |
|------------|-----------|--------------|-----|
| 640x480    | yolov8n   | 8-12         | i5/Ryzen 5 |
| 640x480    | yolov8s   | 5-8          | i5/Ryzen 5 |
| 1280x720   | yolov8n   | 3-5          | i5/Ryzen 5 |

### CPU Optimization Tips

1. **Use smallest model:**
   ```yaml
   path: "yolov8n-pose.pt"  # Nano - fastest
   ```

2. **Enable frame skipping:**
   ```yaml
   detection:
     frame_skip: 2  # Process every 3rd frame
   ```

3. **Lower resolution:**
   ```yaml
   camera:
     width: 640
     height: 480
   ```

4. **Reduce tracking complexity:**
   ```yaml
   tracking:
     max_age: 15      # Lower from 30
     min_hits: 2      # Lower from 3
   ```

5. **Reduce temporal buffer:**
   ```yaml
   temporal_filter:
     buffer_size: 15  # Lower from 30
   ```

## Auto-Detection

The system automatically detects GPU availability:

```python
# In pose_detector.py and ppe_detector.py
self.device = device if torch.cuda.is_available() else "cpu"
```

**Result:**
- ✅ If GPU available → Uses GPU
- ✅ If GPU not available → Falls back to CPU automatically

## Installing PyTorch with GPU Support

### For CUDA 11.8:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### For CUDA 12.1:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### For CPU only:
```bash
pip install torch torchvision
```

## Troubleshooting

### GPU not detected

**Check CUDA availability:**
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

**Solutions:**
1. Install NVIDIA drivers: https://www.nvidia.com/download/index.aspx
2. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
3. Reinstall PyTorch with CUDA support (see above)

### Out of Memory Error

**Reduce memory usage:**
```yaml
models:
  yolov8_pose:
    path: "yolov8s-pose.pt"  # Use smaller model

camera:
  width: 640
  height: 480  # Lower resolution
```

### Slow Performance on CPU

**Optimize settings:**
```yaml
detection:
  frame_skip: 2         # Skip frames

camera:
  width: 640
  height: 480
  fps: 15

models:
  yolov8_pose:
    path: "yolov8n-pose.pt"  # Smallest model
```

## Recommended Configurations

### High-End GPU (RTX 3060+)
```yaml
models:
  yolov8_pose:
    path: "yolov8l-pose.pt"  # Large model
    device: "cuda:0"

camera:
  width: 1920
  height: 1080
  fps: 30

detection:
  frame_skip: 0
```

### Mid-Range GPU (GTX 1660, RTX 2060)
```yaml
models:
  yolov8_pose:
    path: "yolov8m-pose.pt"  # Medium model
    device: "cuda:0"

camera:
  width: 1280
  height: 720
  fps: 30

detection:
  frame_skip: 0
```

### Low-End GPU or Integrated Graphics
```yaml
models:
  yolov8_pose:
    path: "yolov8s-pose.pt"  # Small model
    device: "cuda:0"

camera:
  width: 1280
  height: 720
  fps: 30

detection:
  frame_skip: 1
```

### CPU Only
```yaml
models:
  yolov8_pose:
    path: "yolov8n-pose.pt"  # Nano model
    device: "cpu"

camera:
  width: 640
  height: 480
  fps: 15

detection:
  frame_skip: 2
```

## Model Size Comparison

| Model | Parameters | Size | Speed | Accuracy |
|-------|-----------|------|-------|----------|
| yolov8n-pose | 3.3M | 6MB | ⚡⚡⚡⚡⚡ | ⭐⭐ |
| yolov8s-pose | 11.6M | 22MB | ⚡⚡⚡⚡ | ⭐⭐⭐ |
| yolov8m-pose | 25.9M | 52MB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| yolov8l-pose | 43.7M | 83MB | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| yolov8x-pose | 68.9M | 130MB | ⚡ | ⭐⭐⭐⭐⭐ |

## Monitoring Performance

Check FPS in the GUI:
```yaml
ui:
  display:
    show_fps: true
```

Or check logs:
```bash
tail -f data/logs/app.log
```

## Switching Between GPU and CPU

### Option 1: Edit config.yaml
```yaml
detection:
  use_gpu: false  # Change to false for CPU
```

### Option 2: Edit .env
```bash
USE_GPU=False
```

### Option 3: Environment variable at runtime
```bash
USE_GPU=False python main.py
```

The system will automatically use the correct device!

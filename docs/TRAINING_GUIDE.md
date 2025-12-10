# PPE Detection Model Training Guide

คู่มือการฝึกโมเดล PPE Detection ให้ได้ความแม่นยำสูงสุด

## 📋 Table of Contents

1. [Dataset Preparation](#dataset-preparation)
2. [Data Annotation](#data-annotation)
3. [Dataset Organization](#dataset-organization)
4. [Training Configuration](#training-configuration)
5. [Training Process](#training-process)
6. [Model Evaluation](#model-evaluation)
7. [Optimization Techniques](#optimization-techniques)
8. [Best Practices](#best-practices)

---

## 1. Dataset Preparation

### 📸 Image Collection Guidelines

#### Quantity Requirements:
- **Minimum:** 500-1000 images per class
- **Recommended:** 2000-5000 images per class
- **Optimal:** 10,000+ images per class

#### Image Quality:
- **Resolution:** Minimum 640x640, Recommended 1280x1280
- **Format:** JPG, PNG
- **Quality:** High quality, minimal blur
- **Diversity:** Various lighting, angles, distances

#### Diversity Checklist:
```
✅ Different lighting conditions:
   - Indoor (fluorescent, LED)
   - Outdoor (sunny, cloudy, shadow)
   - Night/Low light

✅ Various angles:
   - Front view
   - Side view (left/right)
   - Back view
   - Top view (bird's eye)
   - 45-degree angles

✅ Different distances:
   - Close-up (2-5 meters)
   - Medium (5-15 meters)
   - Far (15-30 meters)

✅ Multiple scenarios:
   - Single person
   - Multiple persons (2-10+)
   - Crowded scenes
   - Partial occlusion
   - Different backgrounds

✅ PPE variations:
   - Different colors (yellow, orange, red, white helmets)
   - Different types (full-brim, cap style)
   - Worn correctly
   - Worn incorrectly (for negative examples)
   - Different vest types (Class 2, Class 3)

✅ Environmental conditions:
   - Clean/dirty PPE
   - Wet/dry conditions
   - Different weather
```

---

## 2. Data Annotation

### 🏷️ Annotation Tools

#### Recommended Tools:

**1. Label Studio (Best for teams)**
```bash
pip install label-studio
label-studio start
```
- Web-based interface
- Multi-user support
- Export to YOLO format

**2. Roboflow (Cloud-based)**
- https://roboflow.com
- Automatic augmentation
- Version control
- Direct YOLO export

**3. LabelImg (Simple, local)**
```bash
pip install labelImg
labelImg
```
- Desktop application
- YOLO format support
- Fast annotation

**4. CVAT (Advanced)**
- https://cvat.org
- Team collaboration
- Video annotation support

### 📦 PPE Classes Definition

```yaml
classes:
  0: helmet          # Safety helmet/hard hat
  1: vest            # High-visibility vest
  2: gloves          # Safety gloves
  3: boots           # Safety boots
  4: goggles         # Safety goggles/glasses
  5: mask            # Face mask/respirator
  6: no-helmet       # Person without helmet (optional)
  7: no-vest         # Person without vest (optional)
```

### ✏️ Annotation Best Practices

#### Bounding Box Guidelines:

**Helmet:**
```
✅ DO:
- Include entire helmet (top to bottom edge)
- Include visor if present
- Tight fit around helmet shape

❌ DON'T:
- Include excessive background
- Cut off any part of helmet
- Include person's face
```

**Vest:**
```
✅ DO:
- Include all visible vest area
- Include reflective strips
- Both front and back if visible

❌ DON'T:
- Include arms/legs
- Miss reflective parts
- Too tight (cut stripes)
```

**Quality Control:**
- Review 10% of annotations
- Check for consistency
- Fix mislabeled images
- Remove poor quality images

---

## 3. Dataset Organization

### 📁 Directory Structure

```
ppe_dataset/
├── images/
│   ├── train/
│   │   ├── img_0001.jpg
│   │   ├── img_0002.jpg
│   │   └── ...
│   ├── val/
│   │   ├── img_1001.jpg
│   │   └── ...
│   └── test/
│       ├── img_2001.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── img_0001.txt
│   │   ├── img_0002.txt
│   │   └── ...
│   ├── val/
│   │   ├── img_1001.txt
│   │   └── ...
│   └── test/
│       ├── img_2001.txt
│       └── ...
└── data.yaml
```

### 📝 YOLO Label Format

Each `.txt` file contains:
```
<class_id> <x_center> <y_center> <width> <height>
```

Example (`img_0001.txt`):
```
0 0.5120 0.2450 0.0850 0.1200    # helmet
1 0.5200 0.4800 0.1500 0.2500    # vest
```

All values normalized to [0, 1]:
- `x_center`: Center X / Image Width
- `y_center`: Center Y / Image Height
- `width`: Box Width / Image Width
- `height`: Box Height / Image Height

### 📊 Dataset Split

**Recommended split:**
```yaml
Train: 70-80%    # 7000-8000 images
Val:   10-15%    # 1000-1500 images
Test:  10-15%    # 1000-1500 images
```

**For small datasets (<1000 images):**
```yaml
Train: 80%
Val:   15%
Test:  5%
```

---

## 4. Training Configuration

### 📄 Create data.yaml

```yaml
# PPE Detection Dataset Configuration
path: /path/to/ppe_dataset  # Dataset root directory
train: images/train         # Train images (relative to 'path')
val: images/val            # Val images (relative to 'path')
test: images/test          # Test images (relative to 'path')

# Classes
names:
  0: helmet
  1: vest
  2: gloves
  3: boots
  4: goggles
  5: mask

# Number of classes
nc: 6
```

Save as: `ppe_dataset/data.yaml`

---

## 5. Training Process

### 🚀 Basic Training

```bash
# Install Ultralytics
pip install ultralytics

# Train YOLOv8 model
yolo detect train \
    data=ppe_dataset/data.yaml \
    model=yolov8m.pt \
    epochs=100 \
    imgsz=640 \
    batch=16 \
    name=ppe_detection
```

### ⚙️ Advanced Training Parameters

```bash
yolo detect train \
    data=ppe_dataset/data.yaml \
    model=yolov8m.pt \
    epochs=300 \
    imgsz=640 \
    batch=16 \
    patience=50 \
    save=True \
    device=0 \
    workers=8 \
    project=ppe_models \
    name=ppe_v1 \
    exist_ok=True \
    pretrained=True \
    optimizer=AdamW \
    lr0=0.001 \
    lrf=0.01 \
    momentum=0.937 \
    weight_decay=0.0005 \
    warmup_epochs=3.0 \
    warmup_momentum=0.8 \
    warmup_bias_lr=0.1 \
    box=7.5 \
    cls=0.5 \
    dfl=1.5 \
    hsv_h=0.015 \
    hsv_s=0.7 \
    hsv_v=0.4 \
    degrees=0.0 \
    translate=0.1 \
    scale=0.5 \
    shear=0.0 \
    perspective=0.0 \
    flipud=0.0 \
    fliplr=0.5 \
    mosaic=1.0 \
    mixup=0.0 \
    copy_paste=0.0
```

### 📊 Model Size Selection

| Model | Size | Speed | mAP | Best For |
|-------|------|-------|-----|----------|
| yolov8n | ~6MB | ⚡⚡⚡⚡⚡ | ~35% | Edge devices, CPU |
| yolov8s | ~22MB | ⚡⚡⚡⚡ | ~42% | Mobile, fast inference |
| yolov8m | ~52MB | ⚡⚡⚡ | ~50% | **Balanced (Recommended)** ✅ |
| yolov8l | ~83MB | ⚡⚡ | ~53% | High accuracy |
| yolov8x | ~130MB | ⚡ | ~54% | Best accuracy |

**For PPE Detection:**
- **Start with:** `yolov8m.pt` (best balance)
- **Large dataset (>10k):** `yolov8l.pt` or `yolov8x.pt`
- **Small dataset (<1k):** `yolov8s.pt` (avoid overfitting)
- **Real-time critical:** `yolov8n.pt` or `yolov8s.pt`

---

## 6. Model Evaluation

### 📈 Metrics to Monitor

**During Training (TensorBoard):**
```bash
tensorboard --logdir runs/detect/ppe_v1
```

**Key Metrics:**
- **mAP50:** Mean Average Precision @ IoU 0.5
- **mAP50-95:** mAP @ IoU 0.5:0.95 (COCO metric)
- **Precision:** True Positives / (TP + False Positives)
- **Recall:** True Positives / (TP + False Negatives)
- **Box Loss:** Bounding box regression loss
- **Class Loss:** Classification loss

**Target Values:**
```
✅ Good Model:
   mAP50: > 0.85
   mAP50-95: > 0.60
   Precision: > 0.85
   Recall: > 0.80

⭐ Excellent Model:
   mAP50: > 0.95
   mAP50-95: > 0.75
   Precision: > 0.95
   Recall: > 0.90
```

### 🧪 Validation

```bash
# Validate trained model
yolo detect val \
    model=runs/detect/ppe_v1/weights/best.pt \
    data=ppe_dataset/data.yaml \
    imgsz=640 \
    batch=16 \
    save_json=True \
    save_hybrid=True
```

### 🎯 Testing on Real Images

```python
from ultralytics import YOLO

# Load model
model = YOLO('runs/detect/ppe_v1/weights/best.pt')

# Predict
results = model.predict(
    source='test_images/',
    conf=0.5,
    iou=0.4,
    save=True,
    save_txt=True,
    save_conf=True
)

# Print results
for r in results:
    print(f"Detected {len(r.boxes)} objects")
    for box in r.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        print(f"Class: {model.names[cls]}, Confidence: {conf:.2f}")
```

---

## 7. Optimization Techniques

### 🎯 Improve Accuracy

#### 1. **Data Augmentation**

```yaml
# Augmentation parameters in training
hsv_h: 0.015      # Hue variation
hsv_s: 0.7        # Saturation variation
hsv_v: 0.4        # Value/brightness variation
degrees: 10.0     # Rotation (+/- degrees)
translate: 0.1    # Translation (+/- fraction)
scale: 0.5        # Scaling (+/- gain)
shear: 5.0        # Shearing (+/- degrees)
perspective: 0.0  # Perspective distortion
flipud: 0.0       # Vertical flip probability
fliplr: 0.5       # Horizontal flip probability
mosaic: 1.0       # Mosaic augmentation
mixup: 0.15       # Mixup augmentation
copy_paste: 0.1   # Copy-paste augmentation
```

**Recommended for PPE:**
```yaml
hsv_h: 0.015
hsv_s: 0.7
hsv_v: 0.4
degrees: 15.0      # More rotation for various angles
translate: 0.1
scale: 0.5
fliplr: 0.5        # Horizontal flip only
mosaic: 1.0        # Very effective
mixup: 0.1
```

#### 2. **Class Balancing**

If some classes are rare:
```python
# Calculate class weights
from collections import Counter
import numpy as np

# Count instances per class
class_counts = Counter()
for label_file in label_files:
    with open(label_file) as f:
        for line in f:
            cls = int(line.split()[0])
            class_counts[cls] += 1

# Calculate weights (inverse frequency)
total = sum(class_counts.values())
weights = {cls: total / (len(class_counts) * count)
           for cls, count in class_counts.items()}

print("Class weights:", weights)
```

Use weighted loss or oversample rare classes.

#### 3. **Multi-Scale Training**

```bash
# Train with multiple image sizes
yolo detect train \
    data=data.yaml \
    model=yolov8m.pt \
    epochs=300 \
    imgsz=640 \
    batch=16 \
    # Multi-scale will automatically vary size during training
```

#### 4. **Transfer Learning from Custom Dataset**

```bash
# Step 1: Train on general safety dataset
yolo detect train \
    data=safety_general/data.yaml \
    model=yolov8m.pt \
    epochs=100

# Step 2: Fine-tune on your specific PPE dataset
yolo detect train \
    data=ppe_specific/data.yaml \
    model=runs/detect/safety_general/weights/best.pt \
    epochs=200 \
    lr0=0.0001  # Lower learning rate for fine-tuning
```

#### 5. **Ensemble Methods**

Train multiple models and combine predictions:
```python
from ultralytics import YOLO

# Load multiple models
models = [
    YOLO('model_v1.pt'),
    YOLO('model_v2.pt'),
    YOLO('model_v3.pt'),
]

# Ensemble prediction (weighted voting)
def ensemble_predict(image, models, weights=[0.4, 0.3, 0.3]):
    all_boxes = []
    for model, weight in zip(models, weights):
        results = model.predict(image, conf=0.3)
        # Weight the confidence scores
        for r in results:
            for box in r.boxes:
                box.conf *= weight
                all_boxes.append(box)

    # Apply NMS on combined boxes
    # Return final detections
    return nms(all_boxes, iou_threshold=0.5)
```

### ⚡ Improve Speed

#### 1. **Model Pruning**

```python
from ultralytics import YOLO

model = YOLO('best.pt')

# Export to optimized formats
model.export(format='onnx')      # ONNX for cross-platform
model.export(format='engine')    # TensorRT for NVIDIA GPU
model.export(format='openvino')  # OpenVINO for Intel
```

#### 2. **Quantization**

```python
# INT8 quantization (faster, smaller)
model.export(format='engine', int8=True)

# FP16 (balanced)
model.export(format='engine', half=True)
```

#### 3. **Reduce Input Size**

```bash
# Train with smaller input for faster inference
yolo detect train \
    data=data.yaml \
    model=yolov8s.pt \
    imgsz=416  # Smaller size (faster but less accurate)
```

---

## 8. Best Practices

### ✅ Do's

1. **Start with pre-trained weights**
   ```bash
   model=yolov8m.pt  # Always use pretrained
   ```

2. **Use sufficient epochs**
   ```bash
   epochs=300  # Don't stop too early
   patience=50 # Early stopping patience
   ```

3. **Monitor validation metrics**
   - Check validation loss doesn't increase
   - Monitor mAP50 improvement

4. **Save best model automatically**
   ```bash
   save=True  # Saves best.pt and last.pt
   ```

5. **Use appropriate batch size**
   ```
   RTX 3090 (24GB): batch=32-64
   RTX 3060 (12GB): batch=16-32
   GTX 1660 (6GB): batch=8-16
   CPU: batch=4-8
   ```

6. **Clean your dataset**
   - Remove duplicates
   - Fix wrong labels
   - Remove poor quality images

7. **Augment strategically**
   - More augmentation for small datasets
   - Less for large datasets

8. **Test on real scenarios**
   - Test in actual deployment conditions
   - Collect failure cases and retrain

### ❌ Don'ts

1. **Don't use tiny datasets**
   - Minimum 500 images per class
   - Augmentation can't fix insufficient data

2. **Don't train from scratch**
   - Always use pretrained weights
   - Transfer learning is much better

3. **Don't ignore data quality**
   - Poor labels = poor model
   - Spend time on quality annotation

4. **Don't overtrain**
   - Use early stopping
   - Monitor validation loss

5. **Don't use wrong metrics**
   - Focus on mAP for detection
   - Not just accuracy

6. **Don't skip validation**
   - Always validate on unseen data
   - Test set should be truly separate

7. **Don't use single metric**
   - Look at precision AND recall
   - Consider speed and size too

---

## 🎯 Complete Training Workflow

```bash
# 1. Prepare dataset
python prepare_dataset.py --input raw_images/ --output ppe_dataset/

# 2. Check dataset
python check_dataset.py --data ppe_dataset/data.yaml

# 3. Train model
yolo detect train \
    data=ppe_dataset/data.yaml \
    model=yolov8m.pt \
    epochs=300 \
    imgsz=640 \
    batch=16 \
    patience=50 \
    device=0 \
    project=ppe_models \
    name=ppe_v1

# 4. Validate
yolo detect val \
    model=ppe_models/ppe_v1/weights/best.pt \
    data=ppe_dataset/data.yaml

# 5. Test on sample
yolo detect predict \
    model=ppe_models/ppe_v1/weights/best.pt \
    source=test_images/ \
    save=True

# 6. Export for deployment
python -c "
from ultralytics import YOLO
model = YOLO('ppe_models/ppe_v1/weights/best.pt')
model.export(format='onnx')
"

# 7. Copy to project
cp ppe_models/ppe_v1/weights/best.pt \
   ../../models/ppe_detection_best.pt
```

---

## 📊 Expected Results Timeline

| Epochs | mAP50 | Status |
|--------|-------|--------|
| 0-50   | 0.3-0.5 | Initial learning |
| 50-100 | 0.5-0.7 | Improving |
| 100-200 | 0.7-0.85 | Good |
| 200-300 | 0.85-0.95 | Excellent |

If mAP50 plateaus before 0.85:
- Check data quality
- Add more diverse data
- Adjust augmentation
- Try different model size

---

## 🆘 Troubleshooting

### Low mAP (<0.6)

**Possible causes:**
1. Insufficient data
2. Poor annotation quality
3. Imbalanced classes
4. Too aggressive augmentation
5. Wrong learning rate

**Solutions:**
- Collect more data
- Review and fix annotations
- Balance dataset or use class weights
- Reduce augmentation
- Try learning rate: 0.001 or 0.0001

### Overfitting (Train mAP >> Val mAP)

**Solutions:**
- Add more data
- Increase augmentation
- Use smaller model (yolov8s instead of yolov8m)
- Add dropout/regularization
- Reduce epochs

### Slow Training

**Solutions:**
- Reduce batch size
- Use smaller model
- Reduce image size
- Use mixed precision: `amp=True`
- Use more workers: `workers=8`

### Out of Memory

**Solutions:**
- Reduce batch size
- Reduce image size
- Use smaller model
- Close other applications
- Use gradient accumulation

---

## 📚 Additional Resources

- **YOLOv8 Docs:** https://docs.ultralytics.com
- **Roboflow Blog:** https://blog.roboflow.com
- **Papers with Code:** https://paperswithcode.com/task/object-detection
- **COCO Dataset:** https://cocodataset.org

---

**Next Steps:** See `scripts/train_ppe_model.py` for automated training script!

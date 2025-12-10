# Training Scripts for PPE Detection

Quick start scripts for training PPE detection models.

## 📁 Files

- `train_ppe_model.py` - Main training script
- `prepare_dataset.py` - Dataset preparation and validation
- `example_data.yaml` - Template configuration file

## 🚀 Quick Start

### 1. Prepare Your Dataset

```bash
# Organize your dataset
python scripts/prepare_dataset.py \
    --images /path/to/images \
    --labels /path/to/labels \
    --output ppe_dataset \
    --classes helmet vest gloves boots goggles mask
```

This will:
- ✅ Validate label files
- ✅ Analyze class distribution
- ✅ Split into train/val/test (70/15/15)
- ✅ Create data.yaml configuration

### 2. Train Model

**Basic training (recommended for beginners):**
```bash
python scripts/train_ppe_model.py \
    --data ppe_dataset/data.yaml \
    --model yolov8m.pt \
    --epochs 100
```

**Advanced training (for best accuracy):**
```bash
python scripts/train_ppe_model.py \
    --data ppe_dataset/data.yaml \
    --model yolov8m.pt \
    --epochs 300 \
    --advanced
```

**For CPU or small GPU:**
```bash
python scripts/train_ppe_model.py \
    --data ppe_dataset/data.yaml \
    --model yolov8s.pt \
    --epochs 200 \
    --batch 8 \
    --device cpu
```

### 3. Monitor Training

```bash
# View training metrics with TensorBoard
tensorboard --logdir ppe_models/ppe_v1
```

Open browser: http://localhost:6006

### 4. Validate Model

```bash
yolo detect val \
    model=ppe_models/ppe_v1/weights/best.pt \
    data=ppe_dataset/data.yaml
```

### 5. Test Predictions

```bash
yolo detect predict \
    model=ppe_models/ppe_v1/weights/best.pt \
    source=test_images/ \
    save=True \
    conf=0.5
```

### 6. Deploy Model

```bash
# Copy trained model to project
cp ppe_models/ppe_v1/weights/best.pt ../models/ppe_detection_best.pt

# Test with main application
python ../main.py
```

## 📊 Training Parameters

### Model Selection

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| yolov8n | 6MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | CPU, Edge devices |
| yolov8s | 22MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Small datasets |
| yolov8m | 52MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **Recommended** ✅ |
| yolov8l | 83MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Large datasets |
| yolov8x | 130MB | ⚡ | ⭐⭐⭐⭐⭐ | Best accuracy |

### Recommended Settings

**Small dataset (<1000 images):**
```bash
--model yolov8s.pt --epochs 200 --batch 16
```

**Medium dataset (1000-5000 images):**
```bash
--model yolov8m.pt --epochs 300 --batch 16 --advanced
```

**Large dataset (>5000 images):**
```bash
--model yolov8l.pt --epochs 300 --batch 32 --advanced
```

## 🔧 Advanced Options

```bash
python scripts/train_ppe_model.py --help
```

Options:
- `--data`: Path to data.yaml (required)
- `--model`: Model size (yolov8n/s/m/l/x.pt)
- `--epochs`: Number of training epochs
- `--imgsz`: Image size (640, 1280)
- `--batch`: Batch size or 'auto'
- `--patience`: Early stopping patience
- `--device`: GPU device (0, 1, 2, cpu)
- `--workers`: Number of workers
- `--project`: Output folder name
- `--name`: Experiment name
- `--advanced`: Use advanced settings for better accuracy

## 📈 Expected Results

| Dataset Size | Model | Epochs | Expected mAP50 |
|--------------|-------|--------|----------------|
| 500-1000     | yolov8s | 200 | 0.70-0.80 |
| 1000-3000    | yolov8m | 300 | 0.80-0.90 |
| 3000-10000   | yolov8l | 300 | 0.85-0.95 |
| 10000+       | yolov8x | 300 | 0.90-0.98 |

## 🎯 Tips for Best Results

1. **Quality over quantity**
   - Better to have 1000 well-annotated images than 5000 poor ones

2. **Balance your classes**
   - Each class should have similar number of instances
   - Use `--classes` to see distribution

3. **Diverse data**
   - Different lighting, angles, distances
   - Various backgrounds and scenarios

4. **Correct annotations**
   - Tight bounding boxes
   - Consistent labeling
   - Review and fix errors

5. **Use augmentation wisely**
   - `--advanced` flag adds strong augmentation
   - Good for small datasets
   - May hurt large datasets

6. **Monitor metrics**
   - Watch mAP50 and mAP50-95
   - Check precision and recall
   - Use early stopping (patience)

7. **Test on real data**
   - Always test on actual deployment scenarios
   - Collect failure cases and retrain

## 🐛 Troubleshooting

### Out of Memory Error
```bash
# Reduce batch size
--batch 8  # or --batch 4
```

### Slow Training
```bash
# Use smaller model or reduce workers
--model yolov8s.pt --workers 4
```

### Low Accuracy
```bash
# Use advanced settings and train longer
--advanced --epochs 500 --patience 100
```

### Overfitting
```bash
# Use smaller model or more augmentation
--model yolov8s.pt --advanced
```

## 📚 See Also

- [Complete Training Guide](../docs/TRAINING_GUIDE.md)
- [GPU/CPU Configuration](../docs/GPU_CPU_GUIDE.md)
- [Main README](../README.md)

## 💡 Example Workflow

```bash
# 1. Prepare dataset
python scripts/prepare_dataset.py \
    --images raw_data/images \
    --labels raw_data/labels \
    --output ppe_dataset

# 2. Check dataset
python scripts/prepare_dataset.py \
    --images ppe_dataset/images/train \
    --labels ppe_dataset/labels/train \
    --no-split

# 3. Train model (basic)
python scripts/train_ppe_model.py \
    --data ppe_dataset/data.yaml \
    --model yolov8m.pt \
    --epochs 100 \
    --name ppe_basic

# 4. Train model (advanced)
python scripts/train_ppe_model.py \
    --data ppe_dataset/data.yaml \
    --model yolov8m.pt \
    --epochs 300 \
    --advanced \
    --name ppe_advanced

# 5. Compare results
tensorboard --logdir ppe_models/

# 6. Deploy best model
cp ppe_models/ppe_advanced/weights/best.pt \
   ../models/ppe_detection_best.pt

# 7. Test deployment
python ../main.py --check-models
python ../main.py
```

## 🎓 Learning Resources

- YOLOv8 Docs: https://docs.ultralytics.com
- Dataset Tips: https://blog.roboflow.com
- Annotation Guide: https://labelstud.io/guide
- Computer Vision: https://paperswithcode.com

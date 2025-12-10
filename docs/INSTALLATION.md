# Installation Guide

## System Requirements

### Hardware
- CPU: Intel Core i5 or AMD Ryzen 5 (minimum)
- RAM: 8GB minimum, 16GB recommended
- GPU: NVIDIA GPU with CUDA support (optional but recommended)
  - Minimum: GTX 1060 6GB
  - Recommended: RTX 3060 or better
- Storage: 5GB free space for models and data

### Software
- Operating System: Windows 10/11, Ubuntu 20.04+, or macOS 10.15+
- Python: 3.8 or higher
- CUDA Toolkit: 11.8+ (for GPU acceleration)
- Git

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ppe_detection_system.git
cd ppe_detection_system
```

### 2. Create Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install PyTorch (GPU version)

For CUDA 11.8:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

For CPU only:
```bash
pip install torch torchvision
```

### 5. Download Models

```bash
python main.py --download-models
```

Or manually download:
- YOLOv9-Pose: Place in `models/yolov9c-pose.pt`
- PPE Detection Model: Train your own or obtain pre-trained model

### 6. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` file:
```
USE_GPU=True
DEFAULT_CAMERA_ID=0
CONFIDENCE_THRESHOLD=0.5
```

### 7. Verify Installation

```bash
python main.py --check-models
```

## Running the Application

```bash
python main.py
```

With specific camera:
```bash
python main.py --camera 0
```

With video file:
```bash
python main.py --video path/to/video.mp4
```

## Troubleshooting

### CUDA Not Available
- Install NVIDIA drivers
- Install CUDA Toolkit
- Reinstall PyTorch with CUDA support

### Model Not Found
- Run `python main.py --download-models`
- Check model paths in `config.yaml`

### Camera Not Opening
- Check camera permissions
- Try different camera ID
- Verify camera is not used by another application

### Import Errors
- Activate virtual environment
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

## Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
- See [API.md](API.md) for API documentation
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for development guide

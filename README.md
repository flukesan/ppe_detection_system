# 🦺 PPE Detection System

AI-powered Personal Protective Equipment (PPE) Detection System using YOLOv9-Pose and Deep Learning.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

- ✅ **Real-time Detection**: Detect PPE compliance in real-time from camera feeds
- 🏃 **Person Tracking**: Track multiple persons with unique IDs using DeepSORT
- 🎭 **Pose Estimation**: Human pose detection with YOLOv9-Pose for accurate PPE localization
- ⏱️ **Temporal Filtering**: Reduce false positives with temporal analysis
- 📊 **Statistics Dashboard**: Real-time charts and metrics
- 🚨 **Alert System**: Instant notifications for violations (Sound, Email, Line Notify)
- 📹 **Video Recording**: Automatically record violation footage
- 💾 **Database Storage**: SQLite database for detection records
- 🎨 **Modern GUI**: User-friendly PyQt6 interface with dark theme
- 📈 **Export Reports**: Export statistics to Excel/CSV

## 🛡️ Detected PPE Items

- Safety Helmet
- High-Visibility Vest
- Safety Gloves
- Safety Boots
- Safety Goggles
- Face Mask

## 📋 Requirements

### Hardware
- CPU: Intel Core i5 or AMD Ryzen 5+
- RAM: 8GB minimum, 16GB recommended
- GPU: NVIDIA GPU with CUDA support (optional)

### Software
- Python 3.8+
- CUDA 11.8+ (for GPU acceleration)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ppe_detection_system.git
cd ppe_detection_system
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Download Models

```bash
python main.py --download-models
```

### 4. Configure Settings

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run Application

```bash
python main.py
```

## 📁 Project Structure

```
ppe_detection_system/
├── main.py                 # Entry point
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── core/                   # Core detection logic
│   ├── pose_detector.py    # YOLOv9-Pose wrapper
│   ├── ppe_detector.py     # PPE detection
│   ├── tracker.py          # Person tracking
│   ├── temporal_filter.py  # Temporal filtering
│   └── pose_based_detector.py  # Main detection algorithm
├── gui/                    # PyQt6 GUI
│   ├── main_window.py      # Main window
│   ├── camera_widget.py    # Camera display
│   ├── control_panel.py    # Controls
│   ├── stats_widget.py     # Statistics
│   └── alert_widget.py     # Alerts
├── utils/                  # Utilities
│   ├── config_loader.py    # Configuration loader
│   ├── logger.py           # Logging
│   ├── database.py         # Database
│   ├── notification.py     # Notifications
│   └── video_recorder.py   # Video recording
├── models/                 # Model files
├── data/                   # Data storage
│   ├── logs/               # Log files
│   ├── database/           # SQLite database
│   ├── screenshots/        # Screenshots
│   ├── videos/             # Recorded videos
│   └── exports/            # Exported reports
├── tests/                  # Unit tests
├── docs/                   # Documentation
└── monitoring/             # System monitoring
```

## 📖 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](docs/API.md) (TODO)
- [Development Guide](docs/DEVELOPMENT.md) (TODO)

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
detection:
  confidence_threshold: 0.5
  required_ppe:
    - helmet
    - vest

camera:
  width: 1280
  height: 720
  fps: 30

alerts:
  sound: true
  email: false
  line_notify: false
```

## 🎮 Usage

### GUI Mode (Default)

```bash
python main.py
```

### Command Line Options

```bash
# Use specific camera
python main.py --camera 0

# Process video file
python main.py --video path/to/video.mp4

# Check models
python main.py --check-models

# Download models
python main.py --download-models
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_detection.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

## 📊 Performance

| Hardware | FPS | Resolution |
|----------|-----|------------|
| RTX 3060 | ~45 | 1280x720   |
| GTX 1060 | ~25 | 1280x720   |
| CPU only | ~8  | 640x480    |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [YOLOv9](https://github.com/WongKinYiu/yolov9) - Object detection
- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLO implementation
- [DeepSORT](https://github.com/nwojke/deep_sort) - Object tracking
- PyQt6 - GUI framework

## 📧 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

Made with ❤️ for workplace safety

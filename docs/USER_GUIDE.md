# User Guide

## Getting Started

### Starting the Application

1. Activate virtual environment:
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. Run the application:
   ```bash
   python main.py
   ```

### Main Interface

The application consists of four main areas:

1. **Camera View** (Left): Real-time video feed with detection overlay
2. **Alerts Panel** (Bottom Left): Recent violation notifications
3. **Control Panel** (Top Right): System controls and settings
4. **Statistics** (Bottom Right): Detection metrics and charts

## Using the System

### Starting Detection

1. Click "▶ Start Detection" button
2. Select camera source from dropdown
3. Detections will appear in real-time

### Configuring Detection Settings

#### Confidence Threshold
- Adjusts minimum confidence for detections
- Higher = fewer false positives, may miss some detections
- Recommended: 50-70%

#### Violation Threshold
- Temporal filter threshold
- Higher = requires more consistent violations before alert
- Recommended: 70%

### Alert Settings

- **Enable Sound Alerts**: Play sound when violation detected
- **Record Violations**: Automatically record video clips of violations

### Viewing Statistics

The statistics panel shows:
- Current person count
- Number of compliant persons
- Number of violations
- Historical charts

### Exporting Data

1. **Export Statistics**:
   - Click "📊 Export Statistics"
   - Choose format (Excel or CSV)
   - Save to desired location

2. **Export Alerts**:
   - Click "Export Log" in alerts panel
   - Save alert history as text file

## PPE Detection

### Supported PPE Items

The system can detect:
- ✅ Safety Helmet
- ✅ High-Visibility Vest
- ✅ Safety Gloves
- ✅ Safety Boots
- ✅ Safety Goggles
- ✅ Face Mask

### Required PPE

By default, the following PPE items are required:
- Safety Helmet
- High-Visibility Vest

Configure required PPE in `config.yaml`:
```yaml
detection:
  required_ppe:
    - helmet
    - vest
```

## Video Processing

### Processing Video Files

1. Go to File → Open Video File
2. Select video file (MP4, AVI, MOV, MKV)
3. Detection will process automatically

### Recording Violations

When enabled:
- System automatically records 5 seconds before violation
- Continues recording for 5 seconds after
- Videos saved to `data/videos/`
- Filename format: `violation_person{ID}_{timestamp}.mp4`

## Understanding Detection Results

### Person Tracking

- Each person gets a unique ID
- Green box = Compliant
- Red box = Violation
- ID persists as person moves

### Pose Keypoints

When enabled:
- Shows skeletal structure
- Helps verify person detection
- 17 keypoint locations

### Confidence Scores

- Shown on each detection
- Higher = more certain
- Range: 0-100%

## Tips for Best Results

### Camera Placement

- Mount camera at 2-3 meters height
- Angle slightly downward (15-30°)
- Ensure good lighting
- Avoid backlighting

### Lighting Conditions

- Minimum 300 lux illumination
- Avoid direct sunlight on camera
- Use supplementary lighting if needed

### Camera Settings

- Resolution: 1280x720 or higher
- Frame rate: 30 FPS minimum
- Focus: Clear view of detection area

### Performance Optimization

- Use GPU if available (5-10x faster)
- Lower resolution for slower hardware
- Enable frame skipping for real-time performance

## Keyboard Shortcuts

- `Ctrl+O`: Open video file
- `Ctrl+Q`: Quit application
- `Space`: Start/Stop detection (when implemented)

## Common Issues

### False Positives

**Solution:**
1. Increase confidence threshold
2. Increase violation threshold
3. Improve lighting conditions
4. Retrain model with better data

### Missed Detections

**Solution:**
1. Decrease confidence threshold
2. Improve camera angle
3. Ensure adequate lighting
4. Check PPE visibility

### Slow Performance

**Solution:**
1. Enable GPU acceleration
2. Lower camera resolution
3. Enable frame skipping
4. Close other applications

## Data Management

### Database

- All detections stored in SQLite database
- Location: `data/database/ppe_detections.db`
- Can be queried for reports

### Logs

- Application logs: `data/logs/app.log`
- Rotated automatically (10MB max)
- 5 backup files kept

### Screenshots

- Saved to: `data/screenshots/`
- JPEG format, 90% quality
- Filename includes timestamp

## Advanced Configuration

Edit `config.yaml` for advanced settings:

```yaml
detection:
  confidence_threshold: 0.5
  frame_skip: 0  # Skip frames for performance

tracking:
  max_age: 30  # Frames before track deletion
  min_hits: 3  # Minimum detections before confirmed

temporal_filter:
  buffer_size: 30  # Frames to analyze
  violation_threshold: 0.7  # 70% violation rate
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/ppe_detection_system/issues
- Email: support@example.com
- Documentation: See other files in `docs/`

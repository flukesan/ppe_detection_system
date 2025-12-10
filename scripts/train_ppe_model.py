"""
PPE Detection Model Training Script

Automated training script for PPE detection model with optimal settings.
"""

import argparse
import os
import sys
from pathlib import Path
from ultralytics import YOLO
import yaml


def check_dataset(data_yaml):
    """Check if dataset is properly configured."""
    print("\n📋 Checking dataset configuration...")

    if not os.path.exists(data_yaml):
        print(f"❌ Error: {data_yaml} not found!")
        return False

    with open(data_yaml, 'r') as f:
        data = yaml.safe_load(f)

    # Check required fields
    required_fields = ['path', 'train', 'val', 'names', 'nc']
    for field in required_fields:
        if field not in data:
            print(f"❌ Error: Missing '{field}' in {data_yaml}")
            return False

    # Check paths exist
    dataset_path = Path(data['path'])
    train_path = dataset_path / data['train']
    val_path = dataset_path / data['val']

    if not train_path.exists():
        print(f"❌ Error: Training path not found: {train_path}")
        return False

    if not val_path.exists():
        print(f"❌ Error: Validation path not found: {val_path}")
        return False

    # Count images
    train_images = list(train_path.glob('*.jpg')) + list(train_path.glob('*.png'))
    val_images = list(val_path.glob('*.jpg')) + list(val_path.glob('*.png'))

    print(f"✅ Training images: {len(train_images)}")
    print(f"✅ Validation images: {len(val_images)}")
    print(f"✅ Number of classes: {data['nc']}")
    print(f"✅ Classes: {data['names']}")

    if len(train_images) < 100:
        print("⚠️  Warning: Less than 100 training images. Consider collecting more data.")

    return True


def get_training_config(args):
    """Get optimal training configuration based on dataset size and hardware."""
    print("\n⚙️  Determining optimal training configuration...")

    # Determine batch size based on GPU
    if args.batch == 'auto':
        try:
            import torch
            if torch.cuda.is_available():
                gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
                if gpu_mem >= 20:
                    batch_size = 32
                elif gpu_mem >= 10:
                    batch_size = 16
                elif gpu_mem >= 6:
                    batch_size = 8
                else:
                    batch_size = 4
            else:
                batch_size = 4
        except:
            batch_size = 16
    else:
        batch_size = int(args.batch)

    print(f"   Batch size: {batch_size}")
    print(f"   Image size: {args.imgsz}")
    print(f"   Epochs: {args.epochs}")
    print(f"   Model: {args.model}")

    return batch_size


def train_model(args):
    """Train PPE detection model."""
    print("\n" + "=" * 70)
    print("🚀 PPE Detection Model Training")
    print("=" * 70)

    # Check dataset
    if not check_dataset(args.data):
        return False

    # Get configuration
    batch_size = get_training_config(args)

    # Initialize model
    print(f"\n📦 Loading model: {args.model}")
    model = YOLO(args.model)

    # Training arguments
    train_args = {
        'data': args.data,
        'epochs': args.epochs,
        'imgsz': args.imgsz,
        'batch': batch_size,
        'patience': args.patience,
        'save': True,
        'device': args.device,
        'workers': args.workers,
        'project': args.project,
        'name': args.name,
        'exist_ok': True,
        'pretrained': True,
        'verbose': True,
    }

    # Advanced settings for better accuracy
    if args.advanced:
        print("\n🎯 Using advanced training settings for better accuracy...")
        train_args.update({
            'optimizer': 'AdamW',
            'lr0': 0.001,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3.0,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 15.0,
            'translate': 0.1,
            'scale': 0.5,
            'shear': 5.0,
            'perspective': 0.0,
            'flipud': 0.0,
            'fliplr': 0.5,
            'mosaic': 1.0,
            'mixup': 0.1,
            'copy_paste': 0.0,
        })

    # Train
    print("\n🏋️  Starting training...")
    print("-" * 70)

    try:
        results = model.train(**train_args)

        print("\n" + "=" * 70)
        print("✅ Training completed!")
        print("=" * 70)

        # Print results
        best_model_path = Path(args.project) / args.name / 'weights' / 'best.pt'
        print(f"\n📊 Results:")
        print(f"   Best model: {best_model_path}")

        if results:
            print(f"\n   Final metrics:")
            if hasattr(results, 'results_dict'):
                metrics = results.results_dict
                print(f"   - mAP50: {metrics.get('metrics/mAP50(B)', 'N/A'):.4f}")
                print(f"   - mAP50-95: {metrics.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
                print(f"   - Precision: {metrics.get('metrics/precision(B)', 'N/A'):.4f}")
                print(f"   - Recall: {metrics.get('metrics/recall(B)', 'N/A'):.4f}")

        # Suggest next steps
        print(f"\n📝 Next steps:")
        print(f"   1. Validate: yolo detect val model={best_model_path} data={args.data}")
        print(f"   2. Test: yolo detect predict model={best_model_path} source=test_images/")
        print(f"   3. Export: python -c \"from ultralytics import YOLO; YOLO('{best_model_path}').export(format='onnx')\"")
        print(f"   4. Deploy: cp {best_model_path} models/ppe_detection_best.pt")

        return True

    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Train PPE Detection Model')

    # Required arguments
    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to data.yaml file'
    )

    # Optional arguments
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8m.pt',
        help='Model to use (yolov8n/s/m/l/x.pt)'
    )

    parser.add_argument(
        '--epochs',
        type=int,
        default=300,
        help='Number of epochs (default: 300)'
    )

    parser.add_argument(
        '--imgsz',
        type=int,
        default=640,
        help='Image size (default: 640)'
    )

    parser.add_argument(
        '--batch',
        default='auto',
        help='Batch size (default: auto)'
    )

    parser.add_argument(
        '--patience',
        type=int,
        default=50,
        help='Early stopping patience (default: 50)'
    )

    parser.add_argument(
        '--device',
        default='0',
        help='Device to use (0, 1, 2, cpu)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=8,
        help='Number of workers (default: 8)'
    )

    parser.add_argument(
        '--project',
        type=str,
        default='ppe_models',
        help='Project folder name (default: ppe_models)'
    )

    parser.add_argument(
        '--name',
        type=str,
        default='ppe_v1',
        help='Experiment name (default: ppe_v1)'
    )

    parser.add_argument(
        '--advanced',
        action='store_true',
        help='Use advanced training settings for better accuracy'
    )

    args = parser.parse_args()

    # Train
    success = train_model(args)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

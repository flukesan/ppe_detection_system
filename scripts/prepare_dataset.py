"""
Dataset Preparation Script for PPE Detection

Helps organize and validate dataset for training.
"""

import argparse
import os
import shutil
from pathlib import Path
import random
from collections import Counter
import yaml


def split_dataset(images_dir, labels_dir, output_dir, split_ratio=(0.7, 0.15, 0.15)):
    """
    Split dataset into train/val/test sets.

    Args:
        images_dir: Directory containing images
        labels_dir: Directory containing labels
        output_dir: Output directory for split dataset
        split_ratio: (train, val, test) ratio
    """
    print("\n📂 Splitting dataset...")

    # Create output directories
    output_path = Path(output_dir)
    for split in ['train', 'val', 'test']:
        (output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)

    # Get all image files
    images_path = Path(images_dir)
    image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))

    print(f"   Found {len(image_files)} images")

    # Shuffle
    random.shuffle(image_files)

    # Calculate splits
    train_ratio, val_ratio, test_ratio = split_ratio
    n_total = len(image_files)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        'train': image_files[:n_train],
        'val': image_files[n_train:n_train + n_val],
        'test': image_files[n_train + n_val:],
    }

    # Copy files
    labels_path = Path(labels_dir)
    copied_counts = {'train': 0, 'val': 0, 'test': 0}

    for split_name, files in splits.items():
        for img_file in files:
            # Find corresponding label
            label_file = labels_path / (img_file.stem + '.txt')

            if not label_file.exists():
                print(f"⚠️  Warning: Label not found for {img_file.name}")
                continue

            # Copy image
            shutil.copy2(
                img_file,
                output_path / 'images' / split_name / img_file.name
            )

            # Copy label
            shutil.copy2(
                label_file,
                output_path / 'labels' / split_name / label_file.name
            )

            copied_counts[split_name] += 1

    print(f"\n✅ Dataset split completed:")
    print(f"   Train: {copied_counts['train']} images ({train_ratio * 100:.0f}%)")
    print(f"   Val: {copied_counts['val']} images ({val_ratio * 100:.0f}%)")
    print(f"   Test: {copied_counts['test']} images ({test_ratio * 100:.0f}%)")

    return output_path


def analyze_dataset(labels_dir, class_names):
    """Analyze dataset statistics."""
    print("\n📊 Analyzing dataset...")

    labels_path = Path(labels_dir)
    label_files = list(labels_path.glob('*.txt'))

    if not label_files:
        print("❌ No label files found!")
        return None

    # Count classes
    class_counter = Counter()
    total_objects = 0
    images_with_objects = 0
    objects_per_image = []

    for label_file in label_files:
        with open(label_file, 'r') as f:
            lines = f.readlines()

        if lines:
            images_with_objects += 1
            objects_per_image.append(len(lines))

        for line in lines:
            parts = line.strip().split()
            if parts:
                class_id = int(parts[0])
                class_counter[class_id] += 1
                total_objects += 1

    print(f"\n   Total images: {len(label_files)}")
    print(f"   Images with objects: {images_with_objects}")
    print(f"   Total objects: {total_objects}")
    print(f"   Avg objects/image: {total_objects / len(label_files):.2f}")

    print(f"\n   Class distribution:")
    for class_id, count in sorted(class_counter.items()):
        class_name = class_names.get(class_id, f"Class {class_id}")
        percentage = (count / total_objects) * 100
        print(f"      {class_id}: {class_name:15} - {count:5} ({percentage:5.1f}%)")

    # Check for imbalanced classes
    if class_counter:
        max_count = max(class_counter.values())
        min_count = min(class_counter.values())
        ratio = max_count / min_count if min_count > 0 else float('inf')

        if ratio > 10:
            print(f"\n   ⚠️  Warning: Class imbalance detected (ratio: {ratio:.1f}:1)")
            print(f"      Consider balancing your dataset or using class weights")

    return class_counter


def validate_labels(labels_dir):
    """Validate label files for errors."""
    print("\n🔍 Validating labels...")

    labels_path = Path(labels_dir)
    label_files = list(labels_path.glob('*.txt'))

    errors = []
    warnings = []

    for label_file in label_files:
        with open(label_file, 'r') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            parts = line.strip().split()

            if not parts:
                continue

            if len(parts) < 5:
                errors.append(f"{label_file.name}:{line_num} - Invalid format (expected 5 values)")
                continue

            try:
                class_id = int(parts[0])
                x, y, w, h = map(float, parts[1:5])

                # Validate ranges
                if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                    errors.append(f"{label_file.name}:{line_num} - Values out of range [0, 1]")

                if w <= 0 or h <= 0:
                    errors.append(f"{label_file.name}:{line_num} - Invalid width/height")

                if x - w/2 < 0 or x + w/2 > 1 or y - h/2 < 0 or y + h/2 > 1:
                    warnings.append(f"{label_file.name}:{line_num} - Box extends beyond image")

            except ValueError:
                errors.append(f"{label_file.name}:{line_num} - Invalid number format")

    if errors:
        print(f"\n   ❌ Found {len(errors)} errors:")
        for error in errors[:10]:  # Show first 10
            print(f"      {error}")
        if len(errors) > 10:
            print(f"      ... and {len(errors) - 10} more")
    else:
        print(f"   ✅ No errors found")

    if warnings:
        print(f"\n   ⚠️  Found {len(warnings)} warnings:")
        for warning in warnings[:5]:  # Show first 5
            print(f"      {warning}")
        if len(warnings) > 5:
            print(f"      ... and {len(warnings) - 5} more")

    return len(errors) == 0


def create_data_yaml(output_dir, class_names):
    """Create data.yaml configuration file."""
    print("\n📝 Creating data.yaml...")

    data_yaml = {
        'path': str(Path(output_dir).absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names,
    }

    yaml_path = Path(output_dir) / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False, sort_keys=False)

    print(f"   ✅ Created: {yaml_path}")
    return yaml_path


def main():
    parser = argparse.ArgumentParser(description='Prepare PPE Detection Dataset')

    parser.add_argument(
        '--images',
        type=str,
        required=True,
        help='Directory containing images'
    )

    parser.add_argument(
        '--labels',
        type=str,
        required=True,
        help='Directory containing labels'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='ppe_dataset',
        help='Output directory (default: ppe_dataset)'
    )

    parser.add_argument(
        '--split',
        type=float,
        nargs=3,
        default=[0.7, 0.15, 0.15],
        help='Train/Val/Test split ratio (default: 0.7 0.15 0.15)'
    )

    parser.add_argument(
        '--classes',
        type=str,
        nargs='+',
        default=['helmet', 'vest', 'gloves', 'boots', 'goggles', 'mask'],
        help='Class names in order'
    )

    parser.add_argument(
        '--no-split',
        action='store_true',
        help='Skip dataset splitting (use if already split)'
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("📦 PPE Dataset Preparation")
    print("=" * 70)

    # Validate input
    if not os.path.exists(args.images):
        print(f"❌ Error: Images directory not found: {args.images}")
        return

    if not os.path.exists(args.labels):
        print(f"❌ Error: Labels directory not found: {args.labels}")
        return

    # Create class names dict
    class_names = {i: name for i, name in enumerate(args.classes)}

    # Validate labels
    if not validate_labels(args.labels):
        print("\n⚠️  Errors found in labels. Please fix before continuing.")
        return

    # Analyze dataset
    analyze_dataset(args.labels, class_names)

    # Split dataset
    if not args.no_split:
        output_path = split_dataset(
            args.images,
            args.labels,
            args.output,
            tuple(args.split)
        )
    else:
        output_path = Path(args.output)
        print(f"\n   Skipping split (using existing: {output_path})")

    # Create data.yaml
    yaml_path = create_data_yaml(output_path, class_names)

    print("\n" + "=" * 70)
    print("✅ Dataset preparation completed!")
    print("=" * 70)
    print(f"\n📁 Dataset location: {output_path}")
    print(f"📄 Configuration: {yaml_path}")
    print(f"\n🚀 Next step:")
    print(f"   python scripts/train_ppe_model.py --data {yaml_path}")
    print()


if __name__ == '__main__':
    main()

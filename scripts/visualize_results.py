"""
Visualize Training Results

Show training metrics, predictions, and confusion matrix.
"""

import argparse
import os
from pathlib import Path
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO


def plot_training_curves(results_dir):
    """Plot training curves from results.csv."""
    results_csv = Path(results_dir) / 'results.csv'

    if not results_csv.exists():
        print(f"❌ Results file not found: {results_csv}")
        return

    import pandas as pd

    # Read results
    df = pd.read_csv(results_csv)
    df.columns = df.columns.str.strip()  # Remove whitespace

    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Training Metrics', fontsize=16, fontweight='bold')

    # Plot metrics
    plots = [
        ('train/box_loss', 'Box Loss'),
        ('train/cls_loss', 'Classification Loss'),
        ('train/dfl_loss', 'DFL Loss'),
        ('metrics/mAP50(B)', 'mAP@0.5'),
        ('metrics/mAP50-95(B)', 'mAP@0.5:0.95'),
        ('metrics/precision(B)', 'Precision & Recall'),
    ]

    for idx, (metric, title) in enumerate(plots):
        ax = axes[idx // 3, idx % 3]

        if metric in df.columns:
            ax.plot(df['epoch'], df[metric], linewidth=2, label=metric.split('/')[-1])

            # Add recall for precision plot
            if 'precision' in metric and 'metrics/recall(B)' in df.columns:
                ax.plot(df['epoch'], df['metrics/recall(B)'], linewidth=2, label='Recall')
                ax.legend()

            ax.set_xlabel('Epoch')
            ax.set_ylabel(title)
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, f'{metric}\nnot found', ha='center', va='center')
            ax.set_title(title)

    plt.tight_layout()
    output_path = Path(results_dir) / 'training_curves.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved training curves: {output_path}")
    plt.close()


def visualize_predictions(model_path, image_dir, output_dir, conf=0.5, max_images=10):
    """Visualize model predictions on test images."""
    print(f"\n🔍 Running predictions...")

    model = YOLO(model_path)

    # Get image files
    image_path = Path(image_dir)
    image_files = list(image_path.glob('*.jpg')) + list(image_path.glob('*.png'))

    if not image_files:
        print(f"❌ No images found in {image_dir}")
        return

    # Limit number of images
    image_files = image_files[:max_images]

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Run predictions
    for img_file in image_files:
        # Predict
        results = model.predict(
            source=str(img_file),
            conf=conf,
            save=False,
            verbose=False
        )

        # Draw results
        for r in results:
            img = r.plot()  # Get annotated image

            # Save
            output_file = output_path / img_file.name
            cv2.imwrite(str(output_file), img)

        print(f"   ✅ {img_file.name}")

    print(f"\n✅ Saved predictions to: {output_path}")


def show_confusion_matrix(results_dir):
    """Show confusion matrix if available."""
    cm_path = Path(results_dir) / 'confusion_matrix.png'

    if cm_path.exists():
        print(f"✅ Confusion matrix: {cm_path}")
        img = cv2.imread(str(cm_path))
        if img is not None:
            cv2.imshow('Confusion Matrix', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print(f"⚠️  Confusion matrix not found")


def show_summary(results_dir):
    """Show training summary."""
    results_csv = Path(results_dir) / 'results.csv'

    if not results_csv.exists():
        return

    import pandas as pd
    df = pd.read_csv(results_csv)
    df.columns = df.columns.str.strip()

    print("\n" + "=" * 70)
    print("📊 Training Summary")
    print("=" * 70)

    # Get final epoch metrics
    final_row = df.iloc[-1]

    metrics = {
        'Final Epoch': int(final_row['epoch']),
        'mAP@0.5': final_row.get('metrics/mAP50(B)', 'N/A'),
        'mAP@0.5:0.95': final_row.get('metrics/mAP50-95(B)', 'N/A'),
        'Precision': final_row.get('metrics/precision(B)', 'N/A'),
        'Recall': final_row.get('metrics/recall(B)', 'N/A'),
    }

    for name, value in metrics.items():
        if isinstance(value, float):
            print(f"   {name:20} : {value:.4f}")
        else:
            print(f"   {name:20} : {value}")

    # Best epoch
    if 'metrics/mAP50(B)' in df.columns:
        best_idx = df['metrics/mAP50(B)'].idxmax()
        best_row = df.iloc[best_idx]
        best_map = best_row['metrics/mAP50(B)']
        best_epoch = int(best_row['epoch'])

        print(f"\n   {'Best mAP@0.5':20} : {best_map:.4f} (epoch {best_epoch})")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Visualize Training Results')

    parser.add_argument(
        '--results',
        type=str,
        required=True,
        help='Path to training results directory (e.g., ppe_models/ppe_v1)'
    )

    parser.add_argument(
        '--images',
        type=str,
        help='Directory with test images for predictions'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='predictions',
        help='Output directory for predictions'
    )

    parser.add_argument(
        '--conf',
        type=float,
        default=0.5,
        help='Confidence threshold for predictions'
    )

    parser.add_argument(
        '--max-images',
        type=int,
        default=10,
        help='Maximum number of images to process'
    )

    args = parser.parse_args()

    results_dir = Path(args.results)

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return

    # Show summary
    show_summary(results_dir)

    # Plot training curves
    plot_training_curves(results_dir)

    # Visualize predictions if images provided
    if args.images:
        model_path = results_dir / 'weights' / 'best.pt'

        if model_path.exists():
            visualize_predictions(
                model_path,
                args.images,
                args.output,
                args.conf,
                args.max_images
            )
        else:
            print(f"❌ Model not found: {model_path}")

    # Show confusion matrix
    show_confusion_matrix(results_dir)

    print("\n✅ Visualization complete!")


if __name__ == '__main__':
    main()

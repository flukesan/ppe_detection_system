"""
Model downloader utility for downloading pre-trained models.
"""

import os
import requests
from tqdm import tqdm
from typing import Optional


class ModelDownloader:
    """
    Utility for downloading model weights.
    """

    # Model URLs (example - replace with actual URLs)
    MODEL_URLS = {
        "yolov9c-pose": "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-c-pose-converted.pt",
        "ppe_detection": "https://example.com/ppe_detection_best.pt",  # Replace with actual URL
    }

    def __init__(self, models_dir: str = "models"):
        """
        Initialize model downloader.

        Args:
            models_dir: Directory to save models
        """
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)

    def download_model(
        self,
        model_name: str,
        url: Optional[str] = None,
        force: bool = False,
    ) -> Optional[str]:
        """
        Download a model.

        Args:
            model_name: Model name (key in MODEL_URLS or custom name)
            url: Custom URL (if not in MODEL_URLS)
            force: Force re-download even if file exists

        Returns:
            Path to downloaded model or None
        """
        # Get URL
        download_url = url or self.MODEL_URLS.get(model_name)

        if not download_url:
            print(f"❌ Unknown model: {model_name}")
            print(f"Available models: {list(self.MODEL_URLS.keys())}")
            return None

        # Determine filename
        if model_name in self.MODEL_URLS:
            filename = f"{model_name}.pt"
        else:
            filename = os.path.basename(download_url)

        output_path = os.path.join(self.models_dir, filename)

        # Check if already exists
        if os.path.exists(output_path) and not force:
            print(f"✅ Model already exists: {output_path}")
            return output_path

        print(f"📥 Downloading {model_name} from {download_url}...")

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))

            print(f"✅ Downloaded: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Download failed: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    def download_all(self, force: bool = False):
        """
        Download all available models.

        Args:
            force: Force re-download
        """
        print("📥 Downloading all models...")

        for model_name in self.MODEL_URLS.keys():
            self.download_model(model_name, force=force)

        print("✅ All models downloaded!")

    def list_models(self) -> list:
        """
        List available models for download.

        Returns:
            List of model names
        """
        return list(self.MODEL_URLS.keys())

    def check_models(self) -> dict:
        """
        Check which models are downloaded.

        Returns:
            Dictionary of model status
        """
        status = {}

        for model_name in self.MODEL_URLS.keys():
            filename = f"{model_name}.pt"
            path = os.path.join(self.models_dir, filename)
            status[model_name] = os.path.exists(path)

        return status

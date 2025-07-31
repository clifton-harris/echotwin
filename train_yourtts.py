import os
import json
import subprocess
import sys
from pathlib import Path

def ensure_dependencies() -> None:
    """Install required Python packages if they are missing."""
    for pkg in ("numpy", "pandas", "gdown", "torch"):
        try:
            __import__(pkg)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)


def clone_and_install_tts(repo_dir="/content/TTS"):
    """Clone the Coqui TTS repo and install in editable mode."""
    if not os.path.isdir(repo_dir):
        subprocess.run(["git", "clone", "https://github.com/coqui-ai/TTS.git", repo_dir], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", repo_dir], check=True)


def download_dataset(file_id: str = "1t8FoVzZWQ5nPJglvatoHZLUjD2i3UlCi",
                     data_dir: str = "/content/gma_audio_files") -> None:
    """Download and extract dataset using gdown.

    The dataset is provided as a Google Drive zip archive. This function converts
    the file id into a direct download URL, downloads the zip, and extracts it to
    the target directory.
    """
    data_path = Path(data_dir)
    if data_path.is_dir() and any(data_path.iterdir()):
        return

    import gdown
    import zipfile

    data_path.mkdir(parents=True, exist_ok=True)
    gdrive_url = f"https://drive.google.com/uc?id={file_id}"
    zip_path = data_path / "dataset.zip"

    try:
        gdown.download(gdrive_url, str(zip_path), quiet=False)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(data_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Dataset download failed: {exc}")


def sanitize_metadata(data_dir="/content/gma_audio_files"):
    """Read metadata.csv and keep entries with valid audio and transcript."""
    import pandas as pd
    metadata_path = os.path.join(data_dir, "metadata.csv")
    df = pd.read_csv(metadata_path, sep="|", names=["file", "text"], header=None)
    valid_rows = []
    for _, row in df.iterrows():
        audio_path = os.path.join(data_dir, str(row["file"]).strip())
        transcript = str(row["text"]).strip()
        if os.path.isfile(audio_path) and transcript:
            valid_rows.append((os.path.basename(audio_path), transcript))
    clean_df = pd.DataFrame(valid_rows, columns=["file", "text"])
    clean_df.to_csv(metadata_path, sep="|", index=False, header=False)


def create_config(config_path="/content/yourtts_config.json", output_path="/content/yourtts_output"):
    os.makedirs(output_path, exist_ok=True)
    use_cuda = subprocess.run([
        "python",
        "-c",
        "import torch,sys;sys.exit(0) if torch.cuda.is_available() else sys.exit(1)"
    ], capture_output=True)
    config = {
        "output_path": output_path,
        "datasets": [{"name": "gma_dataset", "path": "/content/gma_audio_files"}],
        "model": "tts_models/multilingual/multi-dataset/your_tts",
        "trainer": {
            "epochs": 50,
            "batch_size": 16,
            "eval_batch_size": 8,
            "lr": 1e-4,
            "optimizer": "adam",
            "loss": "Tacotron2Loss",
            "run_eval": True,
            "test_delay_epochs": 5
        },
        "audio": {
            "sample_rate": 22050,
            "win_length": 1024,
            "hop_length": 256,
            "fft_size": 1024
        },
        "use_speaker_embedding": True,
        "use_cuda": use_cuda.returncode == 0,
        "multi_speaker": True,
        "multi_lingual": True
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def train_model(config_path="/content/yourtts_config.json"):
    subprocess.run([sys.executable, "TTS/train.py", "--config_path", config_path], check=True)


def main():
    ensure_dependencies()
    clone_and_install_tts()
    download_dataset()
    sanitize_metadata()
    create_config()
    train_model()


if __name__ == "__main__":
    main()

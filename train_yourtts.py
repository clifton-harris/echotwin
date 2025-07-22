import os
import json
import subprocess
import sys
import pandas as pd


def clone_and_install_tts(repo_dir="/content/TTS"):
    """Clone the Coqui TTS repo and install in editable mode."""
    if not os.path.isdir(repo_dir):
        subprocess.run(["git", "clone", "https://github.com/coqui-ai/TTS.git", repo_dir], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", repo_dir], check=True)


def sanitize_metadata(data_dir="/content/gma_audio_files"):
    """Read metadata.csv and keep entries with valid audio and transcript."""
    metadata_path = os.path.join(data_dir, "metadata.csv")
    df = pd.read_csv(metadata_path, sep="|", names=["file", "text"], header=None)
    valid_rows = []
    for _, row in df.iterrows():
        audio_path = os.path.join(data_dir, row["file"].strip())
        transcript = str(row["text"]).strip()
        if os.path.isfile(audio_path) and transcript:
            valid_rows.append((row["file"].strip(), transcript))
    clean_df = pd.DataFrame(valid_rows, columns=["file", "text"])
    clean_df.to_csv(metadata_path, sep="|", index=False, header=False)


def create_config(config_path="/content/yourtts_config.json", output_path="/content/yourtts_output"):
    os.makedirs(output_path, exist_ok=True)
    use_cuda = subprocess.run(["python", "-c", "import torch,sys;sys.exit(0) if torch.cuda.is_available() else sys.exit(1)"],
                              capture_output=True)
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
    clone_and_install_tts()
    sanitize_metadata()
    create_config()
    train_model()


if __name__ == "__main__":
    main()

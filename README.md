# EchoTwin

EchoTwin is an AI-powered platform that allows users to upload photos, videos, and text from a person and generate a lifelike digital twin that mirrors their appearance, tone, and communication style.

---

## 🧱 Tech Stack

| Component       | Technology             |
|----------------|------------------------|
| Frontend        | React + Tailwind       |
| Backend         | FastAPI (Python)       |
| Media Storage   | GCP Cloud Storage      |
| Database        | Firebase or PostgreSQL |
| Task Queue      | Celery + Redis         |
| Hosting         | GCP Cloud Run          |
| Billing         | Stripe                 |

---

## 🚀 Getting Started

### Frontend
```bash
cd frontend
npm install
npm start
```

### Voice Cloning Training
To fine-tune the [Coqui TTS](https://github.com/coqui-ai/TTS) YourTTS model on
your own dataset, run:

```bash
python train_yourtts.py
```
The script downloads the TTS repository, cleans the dataset in
`/content/gma_audio_files`, creates a configuration with multilingual and
multi-speaker support, installs missing Python dependencies, and launches
training with checkpoints saved to `/content/yourtts_output`.

# 🎙️ Empathy Engine

An AI-powered service that detects emotion in text and synthesizes expressive speech using pyttsx3 — matching vocal characteristics to the detected sentiment.

---

## How It Works

```
Text Input → Emotion Detection → Sentiment Mapping → Intensity Scaling → pyttsx3 TTS → Audio Output
```

1. Text is classified using `j-hartmann/emotion-english-distilroberta-base` 
2. Raw emotion is mapped to one of 3 sentiments: **positive, neutral, negative**
3. Confidence score scales the intensity of voice modulation
4. `pyttsx3` generates speech with sentiment-matched rate and volume
5. FastAPI serves the audio back via `/audio/{filename}`

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download the Transformer Model
On the **first run**, the app will automatically download the emotion classification model from HuggingFace:
- **Model:** `j-hartmann/emotion-english-distilroberta-base`
- **Size:** ~329MB
- **Location:** cached at `C:\Users\<you>\.cache\huggingface\hub\` (Windows) or `~/.cache/huggingface/hub/` (Mac/Linux)
- **One-time only** — subsequent runs will load from cache instantly

> You do not need to download it manually. Just run the server and it will download automatically on first startup.

### 3. Run the server
```bash
uvicorn main:app --reload
```

### 4. Open browser
```
http://localhost:8000
```
> **Note:** On first run, wait for the model to finish downloading (~329MB). On subsequent runs, wait for `Model loaded!` and `Application startup complete` in the terminal before opening the browser.

---

## FastAPI Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Web UI |
| POST | `/analyze` | Detect emotion + generate speech |
| GET | `/audio/{filename}` | Stream generated audio |
| GET | `/sentiments` | List all emotion mappings and voice settings |

### POST /analyze

**Request:**
```json
{ "text": "I just got promoted, this is amazing!" }
```

**Response:**
```json
{
  "text": "I just got promoted, this is amazing!",
  "emotion": "joy",
  "label": "happy",
  "sentiment": "positive",
  "result": "joy - happy",
  "confidence": 0.9823,
  "rate": 214,
  "volume": 1.0,
  "audio_file": "audio_output/positive_a3f2b1c4.wav"
}
```

---

## Emotion → Sentiment Mapping

### Positive
| Emotion | Label |
|---------|-------|
| joy | happy |
| surprise | surprised |
| optimism | optimistic |
| love | loving |
| excitement | excited |
| gratitude | grateful |
| admiration | admiring |
| amusement | amused |
| approval | approving |
| caring | caring |
| desire | desiring |
| pride | proud |
| relief | relieved |

### Neutral
| Emotion | Label |
|---------|-------|
| neutral | neutral |
| curiosity | curious |
| realization | realized |
| confusion | confused |

### Negative
| Emotion | Label |
|---------|-------|
| fear | fearful |
| sadness | sad |
| anger | angry |
| disgust | disgusted |
| disappointment | disappointed |
| disapproval | disapproving |
| embarrassment | embarrassed |
| grief | grieving |
| nervousness | nervous |
| remorse | remorseful |
| annoyance | annoyed |

---

## Sentiment → Voice Mapping

| Sentiment | Rate Delta | Volume | Effect |
|-----------|-----------|--------|--------|
| Positive | +40 wpm | 100% | Faster, louder, energetic |
| Neutral | 0 wpm | 90% | Normal, calm |
| Negative | -30 wpm | 70% | Slower, softer, subdued |

> **Intensity Scaling:** All deltas are multiplied by the model's confidence score, so a 95% confident "joy" modulates much more than a 52% confident "joy".


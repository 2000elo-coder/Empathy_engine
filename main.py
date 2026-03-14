from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import pyttsx3
import os
import uuid
from transformers import pipeline

app = FastAPI(title="Empathy Engine", version="1.0.0")
os.makedirs("audio_output", exist_ok=True)

print("Loading emotion model...")
emotion_classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=1
)
print("Model loaded!")


EMOTION_TO_SENTIMENT = {
    # Positive
    "joy":            {"sentiment": "positive", "label": "the user is happy"},
    "surprise":       {"sentiment": "positive", "label": "the user is surprised"},
    "optimism":       {"sentiment": "positive", "label": "the user is optimistic"},
    "love":           {"sentiment": "positive", "label": "the user is loving the product "},
    "excitement":     {"sentiment": "positive", "label": "the user is excited"},
    "gratitude":      {"sentiment": "positive", "label": "the user is grateful"},
    "admiration":     {"sentiment": "positive", "label": "the user admires"},
    "amusement":      {"sentiment": "positive", "label": "the user is amused"},
    "approval":       {"sentiment": "positive", "label": "the user is approving"},
    "caring":         {"sentiment": "positive", "label": "the user is caring"},
    "desire":         {"sentiment": "positive", "label": "the user is desiring"},
    "pride":          {"sentiment": "positive", "label": "the user is proud"},
    "relief":         {"sentiment": "positive", "label": "the user is relieved"},
    # Neutral
    "neutral":        {"sentiment": "neutral",  "label": "neutral"},
    "curiosity":      {"sentiment": "neutral",  "label": "the user is curious"},
    "realization":    {"sentiment": "neutral",  "label": "the user has realized"},
    "confusion":      {"sentiment": "neutral",  "label": "the user is confused"},
    # Negative
    "fear":           {"sentiment": "negative", "label": "the user is fearful"},
    "sadness":        {"sentiment": "negative", "label": "The user is sad"},
    "anger":          {"sentiment": "negative", "label": "the user is angry"},
    "disgust":        {"sentiment": "negative", "label": "the user is disgusted"},
    "disappointment": {"sentiment": "negative", "label": "the user is disappointed"},
    "disapproval":    {"sentiment": "negative", "label": "the user is disapproving"},
    "embarrassment":  {"sentiment": "negative", "label": "the user is embarrassed"},
    "grief":          {"sentiment": "negative", "label": "the user is grieving"},
    "nervousness":    {"sentiment": "negative", "label": "the user is nervous"},
    "remorse":        {"sentiment": "negative", "label": "the user is remorseful"},
    "annoyance":      {"sentiment": "negative", "label": "the user is annoyed"},
}


SENTIMENT_PARAMS = {
    "positive": {"rate_delta": +40,  "volume": 1.0},
    "negative": {"rate_delta": -30,  "volume": 0.7},
    "neutral":  {"rate_delta":   0,  "volume": 0.9},
}

BASE_RATE = 175  # words per minute 

class TextInput(BaseModel):
    text: str

class AnalysisResult(BaseModel):
    text: str
    emotion: str         
    label: str            
    sentiment: str        
    result: str           
    confidence: float
    rate: int
    volume: float
    audio_file: str


def detect_sentiment(text: str) -> tuple[str, str, str, float]:
    result = emotion_classifier(text)[0][0]
    emotion = result["label"].lower()
    confidence = round(result["score"], 4)
    mapping = EMOTION_TO_SENTIMENT.get(emotion, {"sentiment": "neutral", "label": "neutral"})
    sentiment = mapping["sentiment"]
    label = mapping["label"]
    return emotion, sentiment, label, confidence


def generate_speech(text: str, sentiment: str, confidence: float):
    params = SENTIMENT_PARAMS.get(sentiment, SENTIMENT_PARAMS["neutral"])

    scaled_rate_delta = int(params["rate_delta"] * confidence)
    final_rate = BASE_RATE + scaled_rate_delta
    final_volume = params["volume"]

    engine = pyttsx3.init()
    engine.setProperty("rate", final_rate)
    engine.setProperty("volume", final_volume)

    filename = f"audio_output/{sentiment}_{uuid.uuid4().hex[:8]}.wav"
    engine.save_to_file(text, filename)
    engine.runAndWait()

    return filename, final_rate, final_volume


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the web UI."""
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze", response_model=AnalysisResult)
def analyze(input: TextInput):
    """
    Accepts text, detects emotion via transformer, maps to sentiment,
    generates modulated speech.
    """
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    emotion, sentiment, label, confidence = detect_sentiment(input.text)
    audio_path, rate, volume = generate_speech(input.text, sentiment, confidence)

    return AnalysisResult(
        text=input.text,
        emotion=emotion,
        label=label,
        sentiment=sentiment,
        result=f"{emotion} - {label}",
        confidence=confidence,
        rate=rate,
        volume=volume,
        audio_file=audio_path,
    )


@app.get("/audio/{filename}")
def get_audio(filename: str):
    """Stream the generated audio file."""
    path = f"audio_output/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(path, media_type="audio/wav")


@app.get("/sentiments")
def list_sentiments():
    """Returns sentiment configs and emotion mapping."""
    return {
        "sentiment_params": SENTIMENT_PARAMS,
        "emotion_mapping": EMOTION_TO_SENTIMENT
    }
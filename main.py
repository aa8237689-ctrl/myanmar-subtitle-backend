from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from faster_whisper import WhisperModel
import os
import tempfile


app = FastAPI(
    title="မြန်မာစာတန်းထိုး Server",
    version="2.0.0"
)


# =========================================================
# Translation Model
# =========================================================

class TranslationRequest(BaseModel):
    text: str


MODEL_CACHE = r"D:\AI-Models\models--PyaeSoneK--nllb-600m-wikihow-en-my\snapshots"

snapshot = os.listdir(MODEL_CACHE)[0]
MODEL_PATH = os.path.join(MODEL_CACHE, snapshot)

print("Loading translation model from:", MODEL_PATH)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)

tokenizer.src_lang = "eng_Latn"

print("TRANSLATION MODEL LOADED OK")


# =========================================================
# Whisper Speech-to-Text
# =========================================================

print("Loading Whisper model...")

whisper_model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("WHISPER MODEL LOADED OK")


# =========================================================
# Home / Health
# =========================================================

@app.get("/")
def home():
    return {
        "message": "မြန်မာစာတန်းထိုး Server အလုပ်လုပ်နေပါသည်။"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =========================================================
# English -> Myanmar
# =========================================================

@app.post("/translate")
def translate_text(request: TranslationRequest):

    english_text = request.text.strip()

    if not english_text:
        return {
            "original_text": "",
            "translated_text": ""
        }

    try:

        print("TRANSLATING:", english_text)

        inputs = tokenizer(
            english_text,
            return_tensors="pt"
        )

        output = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                "mya_Mymr"
            ),
            max_length=128
        )

        translated_text = tokenizer.batch_decode(
            output,
            skip_special_tokens=True
        )[0]

        print(
            "TRANSLATION RESULT:",
            translated_text
        )

        return {
            "original_text": english_text,
            "translated_text": translated_text
        }

    except Exception as error:

        print(
            "TRANSLATION ERROR:",
            repr(error)
        )

        return {
            "original_text": english_text,
            "translated_text": "ဘာသာပြန်ရာတွင် အမှားတစ်ခု ဖြစ်ပွားခဲ့ပါသည်။",
            "error": repr(error)
        }


# =========================================================
# Audio -> English -> Myanmar
# =========================================================

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):

    temp_path = None

    try:

        audio_data = await file.read()

        if not audio_data:
            return {
                "original_text": "",
                "translated_text": ""
            }

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            temp_file.write(audio_data)
            temp_path = temp_file.name

        print(
            "WHISPER AUDIO:",
            len(audio_data),
            "bytes"
        )

        segments, info = whisper_model.transcribe(
            temp_path,
            language="en",
            beam_size=5,
            vad_filter=True
        )

        english_text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        print(
            "WHISPER RESULT:",
            english_text
        )

        if not english_text:
            return {
                "original_text": "",
                "translated_text": ""
            }

        inputs = tokenizer(
            english_text,
            return_tensors="pt"
        )

        output = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                "mya_Mymr"
            ),
            max_length=128
        )

        translated_text = tokenizer.batch_decode(
            output,
            skip_special_tokens=True
        )[0]

        print(
            "TRANSLATION RESULT:",
            translated_text
        )

        return {
            "original_text": english_text,
            "translated_text": translated_text
        }

    except Exception as error:

        print(
            "TRANSCRIBE ERROR:",
            repr(error)
        )

        return {
            "original_text": "",
            "translated_text": "",
            "error": repr(error)
        }

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except Exception:
                pass


# =========================================================
# Start Server
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000
    )
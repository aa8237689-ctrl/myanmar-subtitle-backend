from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from deep_translator import GoogleTranslator
import uvicorn

app = FastAPI(
    title="မြန်မာစာတန်းထိုး Server",
    description="English စာကို မြန်မာစာအဖြစ် ပြောင်းပေးသော Server",
    version="1.0.0"
)


class TranslationRequest(BaseModel):
    text: str


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


@app.post("/translate")
def translate_text(request: TranslationRequest):
    english_text = request.text.strip()

    if not english_text:
        return JSONResponse(
            content={
                "original_text": "",
                "translated_text": ""
            },
            media_type="application/json; charset=utf-8"
        )

    try:
        translated_text = GoogleTranslator(
            source="en",
            target="my"
        ).translate(english_text)

        return JSONResponse(
            content={
                "original_text": english_text,
                "translated_text": translated_text
            },
            media_type="application/json; charset=utf-8"
        )

    except Exception as error:
        print("Translation error:", error)

        return JSONResponse(
            content={
                "original_text": english_text,
                "translated_text": "ဘာသာပြန်ရာတွင် အမှားတစ်ခု ဖြစ်ပွားခဲ့ပါသည်။"
            },
            media_type="application/json; charset=utf-8"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000
    )
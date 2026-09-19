from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI(
    title="မြန်မာစာတန်းထိုး Server",
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
            }
        )

    try:
        print("TRANSLATING:", english_text)

        url = "https://translate.googleapis.com/translate_a/single"

        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "my",
            "dt": "t",
            "q": english_text,
        }

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        translated_text = ""

        for item in data[0]:
            if item[0]:
                translated_text += item[0]

        print("TRANSLATION RESULT:", translated_text)

        return JSONResponse(
            content={
                "original_text": english_text,
                "translated_text": translated_text
            }
        )

    except Exception as error:
        print("TRANSLATION ERROR:", repr(error))

        return JSONResponse(
            content={
                "original_text": english_text,
                "translated_text": "ဘာသာပြန်ရာတွင် အမှားတစ်ခု ဖြစ်ပွားခဲ့ပါသည်။",
                "error": repr(error)
            }
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000
    )
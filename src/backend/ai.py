import warnings
warnings.filterwarnings("ignore")
from google import genai
from dotenv import load_dotenv 
import os
import sys
import json

load_dotenv("/Users/master/Desktop/ExamensArbete/src/.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def classify_email(subject, body):
    prompt = f"""
    Analysera följande e-post och returnera ENDAST JSON (inget annat):
    {{
        "folder": "en av: Arbete, Privat, Kvitton, Nyhetsbrev, Skräp, Övrigt",
        "summary": "kort sammanfattning på max 2 meningar",
        "subject": "förbättrat ämne på max 10 ord"
    }}

    Ämne: {subject}
    Innehåll: {(body or '')[:2000]}
    """

    try:
        stderr_backup = sys.stderr
        sys.stderr = open(os.devnull, 'w')

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        sys.stderr = stderr_backup

        result = response.text.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1].rsplit("```", 1)[0]

        return json.loads(result)

    except Exception as e:
        print(f"AI-fel: {e}")
        return {
            "folder": "Övrigt",
            "summary": "",
            "subject": subject or "Inget ämne"
        }



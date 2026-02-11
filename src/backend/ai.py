import warnings
warnings.filterwarnings("ignore")
from openai import OpenAI
from dotenv import load_dotenv 
import os
import json

load_dotenv("/Users/master/Desktop/ExamensArbete/src/.env")
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

def classify_email(subject, body):
    prompt = f"""
Du ska klassificera ett mejl. Gå igenom kategorierna i ordning och välj den FÖRSTA som stämmer.

MEJL:
Ämne: {subject}
Innehåll: {(body or '')[:3000]}

GÅ IGENOM I DENNA ORDNING:

1. Kvitton - JA om mejlet bekräftar något du köpt, betalat, bokat eller beställt.
   Tänk: Fick jag detta för att jag spenderade pengar eller reserverade något?

2. Nyhetsbrev - JA om mejlet är massutskick med reklam/erbjudanden.
   Tänk: Skickades detta till tusentals personer för att sälja något?

3. Arbete - JA om mejlet rör jobb, kollegor eller arbetsuppgifter.
   Tänk: Handlar detta om mitt arbete?

4. Privat - JA om mejlet är personlig kommunikation.
   Tänk: Är detta från någon jag känner personligen?

5. Skräp - JA om mejlet är spam, bluff eller phishing.
   Tänk: Försöker detta lura mig?

6. Övrigt - ENDAST om ingen kategori ovan passar.

Svara med JSON:
{{"folder": "...", "summary": "kort sammanfattning på svenska", "subject": "kort ämne"}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        if "```" in result:
            result = result.split("```")[1].split("```")[0]
            if result.startswith("json"):
                result = result[4:]

        return json.loads(result.strip())

    except Exception as e:
        print(f"AI-fel: {e}")
        return {
            "folder": "Övrigt",
            "summary": "",
            "subject": subject or "Inget ämne"
        }

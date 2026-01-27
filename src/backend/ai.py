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
    prompt = f"""Du är en intelligent e-postassistent. Analysera mejlet och klassificera det.

MEJL ATT ANALYSERA:
Ämne: {subject}
Innehåll: {(body or '')[:2000]}

KLASSIFICERINGSREGLER FÖR FOLDER:
- "Kvitton" = Orderbekräftelser, bokningsbekräftelser, betalningskvitton, leveransbekräftelser, biljetter, fakturor
- "Nyhetsbrev" = Marknadsföring, erbjudanden, rabatter, kampanjer, nyhetsbrev, reklam, "unsubscribe"-länkar
- "Arbete" = Jobbmejl, kollegor, mötesinbjudningar, projekt, arbetsrelaterade ärenden
- "Privat" = Vänner, familj, personliga meddelanden, privata ärenden
- "Skräp" = Spam, phishing, bedrägeriförsök, oönskad reklam
- "Övrigt" = Passar inte in i någon annan kategori

INSTRUKTIONER:
1. folder: Välj den MEST passande kategorin baserat på reglerna ovan
2. summary: Skriv en informativ sammanfattning på svenska (1-2 meningar) som förklarar vad mejlet handlar om
3. subject: Skriv ett kort, tydligt ämne på svenska (max 10 ord)

Svara ENDAST med giltig JSON i detta exakta format:
{{"folder": "kategori", "summary": "sammanfattning", "subject": "ämne"}}"""

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

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
Du ska klassificera ett mejl genom att gå igenom en strukturerad serie ja/nej‑kontroller i en bestämd ordning.
Välj den första kategori där kriterierna stämmer.

MEJL:
Ämne: {subject}
Innehåll: {(body or '')[:2000]}

KATEGORIER OCH KONTROLLER (i denna ordning):

1. Kvitton
Ja om mejlet gäller något av följande:
- beställning, order, betalning, faktura, kvitto, leverans, bokning, biljett
- formuleringar som ”tack för din beställning”, ”din order är mottagen”, ”betalning genomförd”
- betalnings- eller transaktionsmeddelanden från t.ex. PayPal, Klarna, Stripe eller Swish

2. Nyhetsbrev
Ja om mejlet innehåller:
- erbjudanden, kampanjer, rabatter, reklam, produktnyheter
- massutskick, automatiska utskick, ”unsubscribe”, ”newsletter”

3. Arbete
Ja om mejlet gäller:
- kollegor, kunder, projekt, möten, arbetsuppgifter, rekrytering
- arbetsrelaterade system som Jira, GitHub, Teams eller Slack

4. Privat
Ja om mejlet är:
- från vänner, familj eller personliga kontakter
- privata ärenden, sociala planer eller hobbygrupper

5. Skräp
Ja om mejlet är:
- spam, bluff, phishing eller oseriösa utskick
- okänd avsändare med misstänkt innehåll

6. Övrigt
Används endast om inget ovan stämmer.

Instruktion:
- Gå igenom kontrollerna i ordning.
- Välj den första kategori som passar.
- Svara med JSON:
  {{"folder": "...", "summary": "...", "subject": "..."}}.
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

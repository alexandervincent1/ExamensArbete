"""
Kör detta script EN gång för att autentisera med Gmail.
Efter autentisering kan du använda web.py.
"""
import warnings
warnings.filterwarnings("ignore")

from backend.gmail import login

if __name__ == "__main__":
    print("🔐 Startar Gmail-autentisering...")
    print("� En webbläsare öppnas - logga in och godkänn.")
    login()
    print("✅ Klart! Token sparad. Du kan nu köra: python web.py")
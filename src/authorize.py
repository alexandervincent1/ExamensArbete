from flask import Flask, redirect, url_for, session, request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os

# Importera din DB-modul
from db import initialize_database

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CLIENT_SECRETS_FILE = "credentials.json"

# Initiera DB-anslutning
conn = initialize_database()
if conn:
    cursor = conn.cursor()
else:
    print("⚠️ Kunde inte ansluta till databasen.")

@app.route("/")
def index():
    return """
        <h1>Gmail AI Assistent</h1>
        <a href='/authorize'>Logga in / Registrera</a>
    """

@app.route("/authorize")
def authorize():
    # Starta OAuth2-flödet
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    session["flow"] = flow
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    # Slutför OAuth2-flödet
    flow = session["flow"]
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Spara token.json för framtida login
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    return "<h2>✅ Du är inloggad med Gmail!</h2><p>Här kan du visa mail, analysera och spara i DB.</p>"

if __name__ == "__main__":
    app.run(debug=True)
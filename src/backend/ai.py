import warnings
warnings.filterwarnings("ignore")
from google import genai
from dotenv import load_dotenv 
import os
import sys

load_dotenv("/Users/master/Desktop/ExamensArbete/src/.env")
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="generate 10 costumers with different ids and names and ages for a mysql database only json dont write ```json",
    config={
        "thinking_config":{
            "include_thoughts": False
        } 
    }
)



print(response.text)
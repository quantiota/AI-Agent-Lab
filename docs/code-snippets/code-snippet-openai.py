import os
from openai import OpenAI
import openai

API_KEY = os.environ.get('OPENAI_API_KEY')
if API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize OpenAI client with the API key
try:
    client = OpenAI(api_key=API_KEY)
    openai.api_key = API_KEY 
    print("OpenAI API connection is successful!")
except Exception as e:
    print(f"Error connecting to OpenAI: {e}")
    exit()

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = OpenAI(api_key=OPENAI_API_KEY)

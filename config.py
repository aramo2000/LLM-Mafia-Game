import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import anthropic

load_dotenv()

# === OpenAI ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
OPENAI_MODEL = "o4-mini"

# === Gemini ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"

# === DeepSeek ===
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
DEEPSEEK_MODEL = "deepseek-reasoner"

# === Claude ===
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_CLIENT = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"

# === Grok ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_CLIENT = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
GROK_MODEL = "grok-3-mini-beta"

# === HuggingFace ===
HUGGINGFACE_MODEL = 'lxyuan/distilbert-base-multilingual-cased-sentiments-student'

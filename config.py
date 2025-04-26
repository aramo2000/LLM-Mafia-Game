import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
import anthropic

load_dotenv()

# === OpenAI ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
OPENAI_MODEL = "gpt-4o-2024-08-06"
# OPENAI_MODEL = "o3-mini"

# === Gemini ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"
GEMINI_CONFIG = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=1024))
# GEMINI_MODEL = "gemini-2.5-pro-preview-03-25"

# === DeepSeek ===
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
# DEEPSEEK_MODEL = "deepseek-reasoner"
DEEPSEEK_MODEL = "deepseek-chat"

# === Claude ===
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_CLIENT = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"

# === Grok ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_CLIENT = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
GROK_MODEL = "grok-3-mini-beta"
# GROK_MODEL = "grok-3-beta"

# === HuggingFace ===
HUGGINGFACE_MODEL = 'lxyuan/distilbert-base-multilingual-cased-sentiments-student'
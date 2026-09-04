import os

from dotenv import load_dotenv
from google import genai
from backend.llm.prompts import build_sql_prompt, build_insight_prompt

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated text.
    """
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text

def generate_sql(question: str) -> str:
    """
    Convert a natural-language analytics question into a SQL query.
    """
    prompt = build_sql_prompt(question)

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return response.output_text.strip()

def generate_insight(question: str, sql: str, results: list) -> str:
    """
    Convert SQL results into a concise business insight.
    """

    prompt = build_insight_prompt(
        question=question,
        sql=sql,
        results=results
    )

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return response.output_text.strip()
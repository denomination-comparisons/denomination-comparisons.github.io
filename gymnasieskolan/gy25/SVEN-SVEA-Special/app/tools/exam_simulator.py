# app/tools/exam_simulator.py

import os
import json
import google.generativeai as genai
from flask import current_app

# It's good practice to configure the API key once when the app starts.
# Assuming you have this in your app factory or similar.
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def generate_reading_questions_async(text: str) -> dict:
    """
    Generates national exam-style reading comprehension questions from a text
    using the Gemini API and returns a structured JSON object.
    """
    # Configure the client within the function to access the app context
    # This is a robust way to handle API keys in Flask applications
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return {"error": "API-nyckel är inte konfigurerad på servern."}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    except Exception as e:
        print(f"Error configuring Generative AI: {e}")
        return {"error": "API configuration failed."}

    # This prompt is carefully engineered to demand a specific JSON structure.
    # Few-shot prompting (providing an example) greatly increases reliability.
    prompt = f"""
        Du är en expert på svensk pedagogik och provkonstruktion, specialiserad på att skapa övningsuppgifter för Nationella Proven i svenska för gymnasiet.

        Baserat på följande text, generera 3-5 läsförståelsefrågor i stil med Nationella Proven. Blanda frågor av typen "flerval" och "öppen fråga".

        Ditt svar MÅSTE vara ett enda, giltigt JSON-objekt. Inkludera ingen text, förklaringar eller markdown-formatering före eller efter JSON-objektet.

        JSON-strukturen måste följa detta exakta format:
        {{
          "questions": [
            {{
              "type": "multiple-choice",
              "question_text": "Frågetexten här...",
              "options": ["Svarsalternativ A", "Svarsalternativ B", "Svarsalternativ C"],
              "correct_answer": "Svarsalternativ B"
            }},
            {{
              "type": "open-ended",
              "question_text": "Frågetexten för den öppna frågan här...",
              "correct_answer": "En föreslagen modellsvar eller en detaljerad rättningsmall som förklarar vad ett bra svar bör innehålla."
            }}
          ]
        }}

        Här är texten du ska analysera:
        ---
        {text}
        ---
    """

    try:
        response = await model.generate_content_async(prompt)
        
        # Clean the response text to ensure it's valid JSON
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        
        # Parse the cleaned string into a Python dictionary
        exam_data = json.loads(cleaned_response_text)
        return exam_data
    except json.JSONDecodeError:
        return {"error": "Failed to decode the response from the AI. The format was invalid."}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred while generating questions."}

async def generate_writing_prompt_async() -> str:
    """
    Generates a realistic writing prompt in the style of the Swedish National Exams.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return "Ett fel uppstod: API-nyckel är inte konfigurerad på servern."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    except Exception as e:
        print(f"Error configuring Generative AI: {e}")
        return "Ett fel uppstod vid konfiguration av AI-tjänsten."

    prompt = """
        Du är en AI-assistent som skapar innehåll för en språkinlärningsplattform.

        Ditt uppdrag är att generera ett enda, realistiskt skrivuppgiftsförslag (en "prompt") i stil med Nationella Proven för kursen Svenska 3 på gymnasiet.

        En bra prompt ska bestå av:
        1.  En kort inledande text (ett citat, ett scenario, ett kort utdrag ur en artikel) som sätter en kontext.
        2.  En tydlig uppgift som specificerar texttyp (t.ex. debattartikel, krönika, novell, tal) och vad eleven ska göra.

        Svara ENDAST med den genererade prompten. Inkludera inga rubriker, förklaringar eller annan text.
    """

    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Ett fel uppstod när skrivuppgiften skulle genereras. Försök igen."


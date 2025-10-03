# app/tools/modifier.py
import os
import google.generativeai as genai
from google.api_core import exceptions

# --- This is the new, improved prompt. We define it here. ---
def get_llm_prompt(text, target_level):
    return f"""
Du är en expert på lingvistik och andraspråksinlärning med svenska som specialitet. Ditt uppdrag är att anpassa en given svensk text till en specifik CEFR-nivå. Följ dessa instruktioner noggrant:

**Målnivå: {target_level}**

**Instruktioner:**
- **Om målnivån är A1/A2 (Förenkling):**
  - Använd ett högfrekvent basordförråd.
  - Byt ut komplexa ord och idiom mot enklare synonymer eller förklaringar.
  - Använd korta, enkla meningar (t.ex. subjekt-verb-objekt). Undvik långa och komplexa meningar med många bisatser.
  - Använd aktiv form istället för passiv form.
- **Om målnivån är B1/B2 (Standardisering/Neutral):**
  - Behåll textens ursprungliga innebörd och komplexitet, men se till att språket är klart, korrekt och naturligt.
  - Ersätt eventuellt mycket informellt talspråk eller mycket formellt kanslispråk med ett neutralt standardspråk.
  - Förbättra textens flöde och sammanhang om det behövs.
- **Om målnivån är C1/C2 (Avancerad):**
  - Introducera ett mer nyanserat, precist och varierat ordförråd.
  - Använd mer komplexa meningsstrukturer, inklusive olika typer av bisatser och konjunktioner, för att skapa variation.
  - Använd en mer formell eller akademisk ton där det är lämpligt.
  - Inkorporera idiomatiska uttryck på ett naturligt sätt.

**Viktig regel:** Returnera ENDAST den anpassade texten. Inkludera inga förklaringar, kommentarer, rubriker eller annan extra text i ditt svar.

**Originaltext att anpassa:**
---
{text}
---
"""

async def modify_text_for_cefr_async(text, target_level):
    """
    Asynchronously modifies text using the Gemini LLM.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return None, "API-nyckel är inte konfigurerad på servern."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = get_llm_prompt(text, target_level)

        response = await model.generate_content_async(prompt)

        return response.text, None

    except exceptions.GoogleAPICallError as e:
        print(f"API Call Error: {e}")
        return None, f"Ett fel uppstod vid kommunikation med AI-tjänsten: {e.reason}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, "Ett oväntat fel inträffade. Försök igen senare."
import os
import google.generativeai as genai
from google.api_core import exceptions

def get_argument_mining_prompt(text: str) -> str:
    """
    Creates a detailed, structured prompt for the Gemini API to perform
    argumentation mining and return a Mermaid.js graph.
    """
    return f"""
Du är en expert på argumentationsteori och retorik. Ditt uppdrag är att analysera den bifogade texten och extrahera dess argumentstruktur. Du ska presentera denna struktur som en Mermaid.js-graf.

**Analyssteg:**
1.  **Identifiera huvudtesen (Thesis):** Vad är textens centrala budskap eller ståndpunkt? Det ska finnas EN huvudtes.
2.  **Identifiera huvudargument (Claims):** Vilka är de primära påståenden som direkt stödjer huvudtesen?
3.  **Identifiera stödjande bevis/underargument (Evidence):** För varje huvudargument, identifiera de specifika bevis, exempel, data eller underargument som används för att stödja det.

**Formatkrav (Mycket viktigt):**
-   Resultatet ska vara **endast** en sträng med giltig Mermaid.js-grafsyntax (en `graph TD`).
-   Inkludera **inga** förklaringar, kommentarer, kodblock-markörer (som ```mermaid) eller någon annan text före eller efter grafdefinitionen.
-   Använd korta, sammanfattade citat från texten som etiketter för noderna. Håll dem koncisa.
-   Strukturera grafen med huvudtesen överst.

**Exempel på förväntat format:**
graph TD
    A["Huvudtes: [Sammanfattning av tesen]"]
    B["Argument 1: [Sammanfattning av argument 1]"]
    C["Argument 2: [Sammanfattning av argument 2]"]
    D["Bevis 1.1: [Specifikt bevis för argument 1]"]
    E["Bevis 1.2: [Annat bevis för argument 1]"]
    F["Bevis 2.1: [Specifikt bevis för argument 2]"]

    A --> B
    A --> C
    B --> D
    B --> E
    C --> F

**Text att analysera:**
---
{text}
---
"""

async def extract_arguments_async(text: str) -> tuple[str | None, str | None]:
    """
    Asynchronously analyzes a text to extract its argument structure using the Gemini LLM,
    returning a Mermaid.js graph string.

    Args:
        text (str): The text to analyze.

    Returns:
        tuple[str | None, str | None]: A tuple containing (mermaid_graph_string, error_message).
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None, "Serverkonfigurationsfel: API-nyckel för Gemini saknas."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = get_argument_mining_prompt(text)

        # Use the asynchronous version of the generate_content method
        response = await model.generate_content_async(prompt)

        # Clean up potential markdown fences from the response
        cleaned_response = response.text.replace("```mermaid", "").replace("```", "").strip()

        return cleaned_response, None

    except exceptions.GoogleAPICallError as e:
        print(f"API Call Error: {e}")
        return None, f"Ett API-fel uppstod vid kommunikation med AI-tjänsten: {e.reason or 'Okänd orsak'}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, "Ett oväntat serverfel inträffade. Vänligen försök igen senare."

from flask import Flask, request, jsonify
import os

# This function will eventually use a powerful LLM to modify the text.
# For now, it simulates the behavior.
def modify_text_for_cefr(text, target_level):
    """
    Modifies a given text to better match a target CEFR level.

    Args:
        text (str): The original text.
        target_level (str): The desired CEFR level (e.g., "A2", "B1", "C1").

    Returns:
        str: The modified text.
    """
    # In a real implementation, this would be a call to a powerful LLM
    # with a prompt like:
    # "Rewrite the following text to be suitable for a CEFR {target_level} reader.
    # If simplifying, use more common vocabulary and shorter sentences.
    # If making it more advanced, introduce more complex sentence structures and richer vocabulary.
    # Original text: {text}"

    # Simulate the modification
    header = f"--- Text anpassad för nivå {target_level} ---

"
    footer = f"\n\n--- Slut på anpassad text ---"

    if target_level.upper() in ["A1", "A2"]:
        # Simulate simplification
        modified_content = text.replace("klimatförändringar är ett stort problem", "vädret ändras och det är ett problem")
        modified_content = modified_content.replace("Vi måste minska användningen av fossila bränslen.", "Vi måste använda mindre olja och kol.")
        modified_content = modified_content.replace("Trots att teknologin utvecklas snabbt", "Tekniken blir bättre snabbt")
        modified_content = modified_content.replace("finns det fortfarande utmaningar inom artificiell intelligens och etik", "men det finns svåra frågor om datorer som tänker och vad som är rätt.")
    elif target_level.upper() in ["C1", "C2"]:
        # Simulate complexification
        modified_content = text.replace("Jag tycker att klimatförändringar är ett stort problem.", "Ur mitt perspektiv utgör klimatförändringarna en av vår tids mest signifikanta utmaningar.")
        modified_content = modified_content.replace("Vi måste minska användningen av fossila bränslen.", "Det är imperativt att vi reducerar vår konsumtion av fossila bränslen.")
    else: # B1/B2 or other
        modified_content = text # No change for baseline

    return header + modified_content + footer

# Flask-integration for standalone testing
app = Flask(__name__)

@app.route('/modify', methods=['POST'])
def api_modify():
    data = request.get_json()
    if not data or 'text' not in data or 'target_level' not in data:
        return jsonify({"error": "Invalid input. 'text' and 'target_level' are required."}), 400

    text = data['text']
    target_level = data['target_level']

    modified_text = modify_text_for_cefr(text, target_level)

    return jsonify({"original_text": text, "modified_text": modified_text, "target_level": target_level})

def generate_gy25_version(text: str, book_title: str = "") -> str:
    """
    Generates a Gy25 curriculum-adapted version of the input text.
    Assumes text is from a teacher's guide or book content.
    """
    # Placeholder: In real implementation, use LLM to adapt
    adapted = f"# Läroplan för Gy25 - {book_title}\n\n## Syfte\nAtt förstå och analysera innehållet i texten.\n\n## Centralt innehåll\n{text}\n\n## Kunskapskrav\nEleven kan identifiera nyckelbegrepp och argument."
    return adapted

if __name__ == '__main__':
    # Running on port 5001 to avoid conflict with other apps
    app.run(port=5001, debug=True)

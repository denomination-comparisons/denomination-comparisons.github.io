#!/usr/bin/env python3
import sys
import logging
import argparse
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

# Download NLTK data if needed
nltk.download('vader_lexicon', quiet=True)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Configure logging
logging.basicConfig(filename='evaluation_logs.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def semantic_analysis(text):
    doc = nlp(text)
    # Extract entities and concepts related to God and human
    god_related = [token.lemma_ for token in doc if 'god' in token.lemma_.lower() or 'divine' in token.lemma_.lower()]
    human_related = [token.lemma_ for token in doc if 'human' in token.lemma_.lower() or 'man' in token.lemma_.lower()]
    return len(god_related), len(human_related)

def detect_divergence(judaism_text, christianity_text):
    # Simple divergence based on keyword differences
    jud_god, jud_human = semantic_analysis(judaism_text)
    chr_god, chr_human = semantic_analysis(christianity_text)
    divergence = abs((jud_god / max(jud_human, 1)) - (chr_god / max(chr_human, 1)))
    return divergence

def nuance_scoring(text):
    ambiguity_markers = ['paradoxically', 'debated', 'ambiguous', 'uncertain', 'complex']
    score = sum(1 for word in ambiguity_markers if word in text.lower())
    return score

def ethical_reflection_prompts():
    prompts = [
        "What experiential aspects of religion defy AI capture?",
        "How might AI bias influence theological interpretations?",
        "Consider the role of faith in human experience versus algorithmic analysis."
    ]
    return prompts

def arti2_bias_check(text):
    # Simple bias check: sentiment analysis for neutrality
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    bias_score = abs(sentiment['compound'])  # Closer to 0 is more neutral
    return bias_score

def calculate_scores(text, judaism_text, christianity_text):
    divergence = detect_divergence(judaism_text, christianity_text)
    nuance = nuance_scoring(text)
    bias = arti2_bias_check(text)
    
    # Theology score: based on divergence and nuance
    theology_score = min(100, (divergence * 50) + (nuance * 10))
    
    # AI critique: based on bias
    ai_critique_score = max(0, 100 - (bias * 100))
    
    # Synthesis: average of both
    synthesis_score = (theology_score + ai_critique_score) / 2
    
    return theology_score, ai_critique_score, synthesis_score

def generate_feedback(theology, ai_critique, synthesis):
    feedback = f"""
Rubric Feedback:
- Theology (40%): {theology:.2f}/100 - Depth in comparative analysis.
- AI Critique (40%): {ai_critique:.2f}/100 - Bias and ethical considerations.
- Synthesis (20%): {synthesis:.2f}/100 - Integration of theology and AI insights.

Ethical Reflection Prompts:
{chr(10).join(ethical_reflection_prompts())}
"""
    return feedback

def main():
    parser = argparse.ArgumentParser(description='Evaluate Gy25 Religion student responses.')
    parser.add_argument('response_file', help='Path to student response text file')
    parser.add_argument('--judaism', required=True, help='Judaism reference text')
    parser.add_argument('--christianity', required=True, help='Christianity reference text')
    
    args = parser.parse_args()
    
    with open(args.response_file, 'r') as f:
        response = f.read()
    
    judaism_text = args.judaism
    christianity_text = args.christianity
    
    theology, ai_critique, synthesis = calculate_scores(response, judaism_text, christianity_text)
    feedback = generate_feedback(theology, ai_critique, synthesis)
    
    print(feedback)
    
    # Log the evaluation
    logging.info(f"Evaluated response: Theology={theology:.2f}, AI Critique={ai_critique:.2f}, Synthesis={synthesis:.2f}")

if __name__ == '__main__':
    main()
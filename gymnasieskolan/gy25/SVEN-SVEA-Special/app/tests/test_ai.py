import pytest
from ai_module.regression_model import TextRecommender, explain_recommendation

# ARTI-koppling: Enhetstester för AI-logik för att säkerställa korrekthet

class TestTextRecommender:
    def test_recommend_next_level_basic(self):
        # Test grundläggande rekommendation
        recommender = TextRecommender()
        # Simulera data
        recommended = recommender.recommend_next_level(1, '1', 85, 300, None)
        assert recommended in ['A1', 'A2', 'B1', 'B2', 'C1']

    def test_explain_recommendation(self):
        # Test förklaring
        explanation = explain_recommendation(1, 'A2', {'score': 85, 'time_spent': 300})
        assert 'Rekommendation för elev 1' in explanation
        assert 'A2' in explanation

    def test_detect_bias(self):
        # Test bias-detektion
        from models.models import Text
        text = Text(text_id='1', source='Test', title='Test', cefr_level='A1', word_count=10, theme='Test', bias_flags='kön', full_text='Test')
        recommender = TextRecommender()
        warning = recommender.detect_bias(text)
        assert 'kön' in warning
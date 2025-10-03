import pytest
from app.tools.text_processor import TextProcessor

class TestTextProcessor:
    def test_parse_input_text(self):
        processor = TextProcessor()
        text = "Sample text"
        result = processor.parse_input(text, 'text')
        assert result == text

    def test_parse_input_pdf_placeholder(self):
        processor = TextProcessor()
        with pytest.raises(NotImplementedError):
            processor.parse_input(b"pdf data", 'pdf')

    def test_analyze_cefr(self):
        processor = TextProcessor()
        text = "Jag heter Anna."
        level = processor.analyze_cefr(text)
        assert isinstance(level, str)

    @pytest.mark.asyncio
    async def test_modify_text(self):
        processor = TextProcessor()
        text = "Sample text"
        modified = await processor.modify_text(text, 'B1')
        assert "[Modified to B1]" in modified

    def test_generate_source_criticism(self):
        processor = TextProcessor()
        text = "Sample text"
        result = processor.generate_source_criticism(text)
        assert 'questions' in result

    @pytest.mark.asyncio
    async def test_simulate_exam(self):
        processor = TextProcessor()
        text = "Sample text"
        result = await processor.simulate_exam(text)
        assert 'questions' in result

    @pytest.mark.asyncio
    async def test_process_book_guide(self):
        processor = TextProcessor()
        input_data = "Book content"
        options = {'cefr': 'B1', 'source_crit': True}
        result = await processor.process_book_guide(input_data, 'text', 'Test Book', options)
        assert result['book_title'] == 'Test Book'
        assert 'modified_text' in result
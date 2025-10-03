
from flask import Blueprint, render_template, request, jsonify, current_app
from app.tools.exam_simulator import generate_reading_questions_async, generate_writing_prompt_async
from app.tools import cefr, kallkritik, visualizer, modifier, argument_miner
from app.tools.text_processor import TextProcessor
import os

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

@tools_bp.route('/')
def index():
    """Main page for the tools suite."""
    return render_template('tools/index.html')

@tools_bp.route('/cefr_analyzer', methods=['GET', 'POST'])
def cefr_analyzer():
    """Provides an interface for the CEFR text analyzer."""
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            return render_template('tools/cefr_analyzer.html', error="Text field cannot be empty.")
        
        result = cefr.classify_text(text)
        return render_template('tools/cefr_analyzer.html', result=result, original_text=text)
        
    return render_template('tools/cefr_analyzer.html')

@tools_bp.route('/source_criticism', methods=['GET', 'POST'])
def source_criticism():
    """Provides an interface for the source criticism question generator."""
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            return render_template('tools/source_criticism.html', error="Text field cannot be empty.")
            
        result = kallkritik.generate_questions(text)
        return render_template('tools/source_criticism.html', result=result, original_text=text)

    return render_template('tools/source_criticism.html')

@tools_bp.route('/concept_mapper', methods=['GET', 'POST'])
def concept_mapper():
    """Provides an interface for the concept map generator."""
    if request.method == 'POST':
        text_input = request.form.get('text')
        if not text_input:
            return render_template('tools/concept_mapper.html', error="Input field cannot be empty.")
        
        static_folder = current_app.static_folder
        image_filename = visualizer.generate_concept_map(text_input, static_folder)
        
        if image_filename:
            return render_template('tools/concept_mapper.html', image_filename=image_filename, original_text=text_input)
        else:
            return render_template('tools/concept_mapper.html', error="Could not generate map. Ensure input format is correct (e.g., 'Concept A -> Concept B [Label]').", original_text=text_input)

    return render_template('tools/concept_mapper.html')


@tools_bp.route('/text-modifier', methods=['GET', 'POST'])
async def text_modifier(): # <--- Make the route function async
    """Provides an interface for the text modification tool."""
    if request.method == 'POST':
        data = request.get_json()
        text = data.get('text')
        target_level = data.get('target_level')

        if not text or not target_level:
            return jsonify({"error": "Indata saknas. 'text' och 'target_level' krävs."}), 400

        # Await the new async function
        modified_text, error = await modifier.modify_text_for_cefr_async(text, target_level)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"modified_text": modified_text})

    return render_template('tools/text_modifier.html')


@tools_bp.route('/argument-visualizer', methods=['GET', 'POST'])
async def argument_visualizer():
    """Provides an interface for the argumentation visualization tool."""
    if request.method == 'POST':
        data = request.get_json()
        text = data.get('text')

        if not text:
            return jsonify({"error": "'text' är obligatoriskt."}), 400

        # Call the new async function from the argument_miner module
        graph_data, error = await argument_miner.extract_arguments_async(text)

        if error:
            # If an error occurred, return it with a 500 server error status
            return jsonify({"error": error}), 500

        return jsonify({"argument_graph": graph_data})

    return render_template('tools/argument_visualizer.html')


@tools_bp.route('/reading-exam', methods=['GET', 'POST'])
async def reading_exam():
    if request.method == 'POST':
        data = await request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        result = await generate_reading_questions_async(text)
        return jsonify(result)

    return render_template('tools/reading_exam.html')


@tools_bp.route('/writing-exam', methods=['GET', 'POST'])
async def writing_exam():
    if request.method == 'POST':
        # This POST request is just a trigger to generate a new prompt
        prompt_text = await generate_writing_prompt_async()
        return prompt_text

    return render_template('tools/writing_exam.html')

@tools_bp.route('/process-book-guide', methods=['GET', 'POST'])
async def process_book_guide():
    """Page and handler for processing book guide."""
    if request.method == 'POST':
        file = request.files.get('file')
        book_title = request.form.get('book_title', 'Unknown Book')
        options = {
            'cefr': request.form.get('cefr'),
            'source_crit': request.form.get('source_crit') == 'on',
            'exam': request.form.get('exam') == 'on',
            'visualize': request.form.get('visualize') == 'on'
        }

        if not file:
            return render_template('tools/process_book_guide.html', error="No file uploaded")

        input_data = file.read()
        input_type = 'pdf' if file.filename.endswith('.pdf') else 'text'

        processor = TextProcessor()
        result = await processor.process_book_guide(input_data, input_type, book_title, options)

        return render_template('tools/process_book_guide.html', result=result)

    return render_template('tools/process_book_guide.html')

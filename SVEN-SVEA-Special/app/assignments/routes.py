from flask import Blueprint, render_template, request, jsonify, current_app
from app.tools.text_processor import TextProcessor
# from app.models.models import ReadingAssignment, StudentResponse, AIFeedback, db  # Placeholder

assignments = Blueprint('assignments', __name__)
tp = TextProcessor()

@assignments.route('/create', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        content = request.form.get('content') or request.files.get('file').read().decode('utf-8')
        parsed = tp.parse_assignment(content)
        # assignment = ReadingAssignment(title=request.form['title'], content=json.dumps(parsed))
        # db.session.add(assignment)
        # db.session.commit()
        return render_template('assignments/create.html', success="Assignment created")
    return render_template('assignments/create.html')

@assignments.route('/exercise/<int:assignment_id>')
def student_exercise(assignment_id):
    # assignment = ReadingAssignment.query.get(assignment_id)
    # Render interactive UI
    return render_template('assignments/student_exercise.html', assignment={'title': 'Sample', 'content': {'texts': ['Sample text'], 'questions': ['Sample question']}})

@assignments.route('/submit/<int:assignment_id>', methods=['POST'])
def submit_response(assignment_id):
    answers = request.json.get('answers', [])
    strategies = request.json.get('strategies', [])
    # response = StudentResponse(assignment_id=assignment_id, answers=json.dumps(answers), strategies=json.dumps(strategies))
    # db.session.add(response)
    # db.session.commit()
    # feedback = tp.analyze_comprehension(answers[0] if answers else '', 'correct')
    # ai_fb = AIFeedback(response_id=response.id, comprehension_score=feedback[0], cefr_level=feedback[1])
    # db.session.add(ai_fb)
    # db.session.commit()
    return jsonify({'feedback': 'Sample feedback'})
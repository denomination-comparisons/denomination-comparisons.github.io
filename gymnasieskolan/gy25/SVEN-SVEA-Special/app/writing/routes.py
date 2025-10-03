from flask import Blueprint, render_template, request, jsonify
from app.tools.text_processor import TextProcessor
# from app.models.models import WritingAssignment, StudentWriting, WritingFeedback, db

writing = Blueprint('writing', __name__)
tp = TextProcessor()

@writing.route('/create', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        elements = request.form.getlist('elements')  # checkboxes
        # assignment = WritingAssignment(title=title, description=description, elements=json.dumps(elements))
        # db.session.add(assignment)
        # db.session.commit()
        return render_template('writing/create.html', success="Assignment created")
    return render_template('writing/create.html')

@writing.route('/write/<int:assignment_id>', methods=['GET', 'POST'])
def write_novella(assignment_id):
    if request.method == 'POST':
        content = request.form['content']
        elements_used = request.form.getlist('elements_used')
        # writing = StudentWriting(assignment_id=assignment_id, content=content, elements_used=json.dumps(elements_used))
        # db.session.add(writing)
        # db.session.commit()
        # feedback = tp.provide_writing_feedback(content, {})
        # wf = WritingFeedback(writing_id=writing.id, element_scores=json.dumps(feedback['element_scores']), recommendations=json.dumps(feedback['recommendations']), cefr_level=feedback['cefr_level'])
        # db.session.add(wf)
        # db.session.commit()
        return jsonify({'feedback': 'Sample feedback'})
    return render_template('writing/write.html', assignment={'title': 'Sample Novella Assignment', 'description': 'Write a novella.', 'elements': ['undertext', 'dialog']})
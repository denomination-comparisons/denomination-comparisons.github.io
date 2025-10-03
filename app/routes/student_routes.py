# app/routes/student_routes.py

from flask import Blueprint, render_template, abort
import json

student_bp = Blueprint('student', __name__, url_prefix='/student')

ASSIGNMENTS_FILE = 'app/data/assignments.json'

def load_assignments():
    """Helper function to load assignments."""
    try:
        with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@student_bp.route('/')
def dashboard():
    """Displays the list of all available assignments."""
    assignments = load_assignments()
    return render_template('student_dashboard.html', assignments=assignments)

@student_bp.route('/assignment/<assignment_id>')
def assignment_view(assignment_id):
    """Displays a single assignment with its text and enabled tools."""
    assignments = load_assignments()
    assignment = next((a for a in assignments if a['id'] == assignment_id), None)
    if assignment is None:
        abort(404)
    return render_template('assignment_view.html', assignment=assignment)

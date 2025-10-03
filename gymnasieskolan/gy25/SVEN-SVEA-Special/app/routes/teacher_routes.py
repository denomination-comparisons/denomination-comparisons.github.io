# app/routes/teacher_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import json
import uuid
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

ASSIGNMENTS_FILE = 'app/data/assignments.json'

def load_assignments():
    """Helper function to load assignments from the JSON file."""
    try:
        with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_assignments(assignments):
    """Helper function to save assignments to the JSON file."""
    with open(ASSIGNMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(assignments, f, indent=2, ensure_ascii=False)

@teacher_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # Create a new assignment
        assignments = load_assignments()
        
        new_assignment = {
            "id": uuid.uuid4().hex,
            "teacher_id": "teacher01", # Hardcoded for now
            "title": request.form['title'],
            "text": request.form['text'],
            "date_created": datetime.utcnow().isoformat() + "Z",
            "enabled_tools": request.form.getlist('enabled_tools')
        }
        
        assignments.insert(0, new_assignment) # Add to the top of the list
        save_assignments(assignments)
        
        return redirect(url_for('teacher.dashboard'))

    # For GET request, load and display existing assignments
    assignments = load_assignments()
    return render_template('teacher_dashboard.html', assignments=assignments)

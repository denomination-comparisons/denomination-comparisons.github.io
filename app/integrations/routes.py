from flask import Blueprint, request, jsonify
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

integrations = Blueprint('integrations', __name__)

@integrations.route('/sync_classroom', methods=['POST'])
def sync_classroom():
    # Placeholder for OAuth credentials
    creds_data = request.json.get('credentials')  # Assume JSON with creds
    creds = Credentials.from_authorized_user_info(creds_data)
    service = build('classroom', 'v1', credentials=creds)
    course_id = request.json.get('course_id')
    title = request.json.get('title', 'Swedish Assignment')
    coursework = {'title': title, 'workType': 'ASSIGNMENT'}
    result = service.courses().courseWork().create(courseId=course_id, body=coursework).execute()
    return jsonify({'coursework_id': result['id'], 'message': 'Assignment synced'})
import json
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse

# Constants
TASKS_FILE = 'tasks.json'

def load_tasks(file_path):
    """Load tasks from JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in tasks file. Starting with empty tasks.")
            return []
    return []

def save_tasks(tasks, file_path):
    """Save tasks to JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(tasks, f, indent=4)
    except IOError as e:
        print(f"Error saving tasks: {e}")

def add_task(tasks, description, deadline_str):
    """Add a new task."""
    try:
        deadline = datetime.fromisoformat(deadline_str)
        task_id = max([t['id'] for t in tasks], default=0) + 1
        task = {
            'id': task_id,
            'description': description,
            'deadline': deadline_str,
            'completed': False
        }
        tasks.append(task)
        print(f"Task added with ID {task_id}")
    except ValueError:
        print("Error: Invalid deadline format. Use ISO format, e.g., 2023-10-01T12:00:00")

def list_tasks(tasks):
    """List all tasks."""
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        status = "Completed" if task['completed'] else "Pending"
        print(f"ID: {task['id']}, Description: {task['description']}, Deadline: {task['deadline']}, Status: {status}")

def complete_task(tasks, task_id):
    """Mark a task as completed."""
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = True
            print(f"Task {task_id} marked as completed.")
            return
    print(f"Task {task_id} not found.")

def delete_task(tasks, task_id):
    """Delete a task."""
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            del tasks[i]
            print(f"Task {task_id} deleted.")
            return
    print(f"Task {task_id} not found.")

def send_reminders(tasks, smtp_server, smtp_port, email_user, email_pass, recipient):
    """Send email reminders for tasks due within 24 hours."""
    now = datetime.now()
    upcoming = [t for t in tasks if not t['completed'] and datetime.fromisoformat(t['deadline']) - now <= timedelta(hours=24)]
    if not upcoming:
        print("No upcoming deadlines.")
        return
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_pass)
        for task in upcoming:
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = recipient
            msg['Subject'] = f"Reminder: Task '{task['description']}' due soon"
            body = f"Your task '{task['description']}' is due on {task['deadline']}."
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(email_user, recipient, msg.as_string())
        server.quit()
        print(f"Reminders sent for {len(upcoming)} tasks.")
    except Exception as e:
        print(f"Error sending reminders: {e}")

def main():
    parser = argparse.ArgumentParser(description="Command-line Task Manager")
    parser.add_argument('action', choices=['add', 'list', 'complete', 'delete', 'remind'], help="Action to perform")
    parser.add_argument('--description', help="Task description")
    parser.add_argument('--deadline', help="Task deadline in ISO format")
    parser.add_argument('--id', type=int, help="Task ID")
    parser.add_argument('--smtp-server', default='smtp.gmail.com', help="SMTP server")
    parser.add_argument('--smtp-port', type=int, default=587, help="SMTP port")
    parser.add_argument('--email-user', help="Email username")
    parser.add_argument('--email-pass', help="Email password")
    parser.add_argument('--recipient', help="Recipient email")

    args = parser.parse_args()

    tasks = load_tasks(TASKS_FILE)

    if args.action == 'add':
        if not args.description or not args.deadline:
            print("Error: Description and deadline required for add action.")
            return
        add_task(tasks, args.description, args.deadline)
    elif args.action == 'list':
        list_tasks(tasks)
    elif args.action == 'complete':
        if not args.id:
            print("Error: Task ID required for complete action.")
            return
        complete_task(tasks, args.id)
    elif args.action == 'delete':
        if not args.id:
            print("Error: Task ID required for delete action.")
            return
        delete_task(tasks, args.id)
    elif args.action == 'remind':
        if not all([args.email_user, args.email_pass, args.recipient]):
            print("Error: Email credentials and recipient required for remind action.")
            return
        send_reminders(tasks, args.smtp_server, args.smtp_port, args.email_user, args.email_pass, args.recipient)

    save_tasks(tasks, TASKS_FILE)

if __name__ == "__main__":
    main()
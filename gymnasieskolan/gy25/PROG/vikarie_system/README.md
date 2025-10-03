# Vikarie Management System

A web-based system for managing substitute teachers in Swedish schools.

## Features

- Digital substitute pool management
- SMS/email broadcast for vacancies
- Attendance reporting
- Integration placeholders for SchoolSoft

## Setup

### Backend

1. Navigate to `backend/` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Create database: `python create_db.py`
4. Run the server: `uvicorn main:app --reload`

### Frontend

1. Navigate to `frontend/` directory
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

## Project Structure

- `backend/`: Python FastAPI application
- `frontend/`: React TypeScript application
- `docs/`: Documentation

## Next Steps

- Implement SMS integration
- Add authentication
- Create more models (assignments, attendance)
- Build additional UI components

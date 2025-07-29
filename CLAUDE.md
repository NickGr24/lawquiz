# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This is a Django web application. Use these commands for development:

- **Run development server**: `python manage.py runserver`
- **Run migrations**: `python manage.py migrate`
- **Create migrations**: `python manage.py makemigrations`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic`
- **Django shell**: `python manage.py shell`

Install dependencies with: `pip install -r requirements.txt`

## Architecture Overview

This is a Django quiz application with the following structure:

### Core Models (home/models.py)
- **Discipline**: Subject categories for quizzes
- **Quiz**: Individual quizzes belonging to disciplines  
- **Question**: Questions within quizzes
- **Answer**: Multiple choice answers for questions (with correct flag)
- **Marks_Of_User**: User quiz scores and completion tracking

### Key Features
- Multi-discipline quiz system with hierarchical organization
- Session-based quiz taking (stores progress in Django sessions)
- Admin-only question creation interface with AJAX quiz loading
- Django Allauth integration for authentication including Google OAuth
- Romanian language interface (LANGUAGE_CODE = 'ro-RO')

### URL Structure
- `/` - Home page showing all disciplines
- `/discipline/<id>/` - Quiz list by discipline with completion status
- `/quiz/<id>/` - Take quiz (session-based progression)
- `/quiz/<id>/results/` - Quiz results page
- `/add-question/` - Admin interface for adding questions
- `/login/`, `/register/`, `/logout/` - Authentication

### Technical Details
- Uses SQLite database (db.sqlite3)
- Static files served from `/static/` directory
- Templates in `home/templates/` with base template structure
- CSRF protection enabled with trusted origins for ngrok
- Session-based quiz state management (question_number, user_answers, score)
- AJAX endpoints for dynamic quiz loading in admin interface

### Database Schema
Questions have multiple answers, only one marked as correct. User progress tracked in Marks_Of_User model with score percentages.
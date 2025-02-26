# Quiz Master - V1

## Overview
Quiz Master is a multi-user web application designed for exam preparation across multiple courses. The platform supports two roles: **Admin** (Quiz Master) and **Users**, allowing quiz management, subject-wise question categorization, and performance tracking.

## Tech Stack
- **Backend:** Flask
- **Templating Engine:** Jinja2
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite

## Features
### Admin (Quiz Master)
- **Superuser Access:** Preexsisting in database
- **Dashboard Management:**
  - [ ] Create, edit, and delete subjects.
  - [ ] Create, edit, and delete chapters under subjects.
  - [ ] Create quizzes under chapters.
  - [ ] Add multiple-choice questions (MCQs) with one correct option.
  - [ ] Define quiz date and duration.
  - [ ] View and manage registered users.
  - [ ] View quiz performance and generate summary charts.
- **Search Functionalities:**
  - [ ] Search users, subjects, and quizzes.

### User
- **Registration & Authentication:**
  - [ ] Users must sign up with an email and password.
  - [ ] Additional fields include full name, qualification, and date of birth.
- **Quiz Management:**
  - [ ] Select subject and chapter for quiz attempts.
  - [ ] Timed quizzes (optional timer feature).
  - [ ] View previous quiz attempts and scores.
  - [ ] Summary charts for performance tracking.

## Database Schema
### User Table
- `id` (Primary Key)
- `username` (Email)
- `password`
- `full_name`
- `qualification`
- `dob`

### Subject Table
- `id` (Primary Key)
- `name`
- `description`

### Chapter Table
- `id` (Primary Key)
- `subject_id` (Foreign Key)
- `name`
- `description`

### Quiz Table
- `id` (Primary Key)
- `chapter_id` (Foreign Key)
- `date_of_quiz`
- `time_duration`
- `remarks`

### Question Table
- `id` (Primary Key)
- `quiz_id` (Foreign Key)
- `question_statement`
- `option1`, `option2`, `option3`, `option4`
- `correct_option`

### Score Table
- `id` (Primary Key)
- `quiz_id` (Foreign Key)
- `user_id` (Foreign Key)
- `time_stamp_of_attempt`
- `total_scored`

## Core Functionalities
### Admin Panel
- CRUD operations for subjects, chapters, quizzes, and questions.
- View and manage user profiles.
- Track user quiz attempts and performance.
- Generate reports and summary charts.

### User Dashboard
- Browse available quizzes by subject and chapter.
- Take quizzes and receive instant scores.
- Track past quiz performances.
- View graphical summaries of performance trends.

## Additional Functionalities
### Recommended Enhancements
- RESTful APIs using Flask (`flask_restful` or JSON responses).
- Frontend form validation (HTML5/JavaScript).
- Backend validation (Flask controllers).
- Chart integration (e.g., Chart.js).

### Optional Features
- Enhanced UI/UX with Bootstrap.
- Secure authentication (`flask_login`, `flask_security`).
- Additional quiz modes or question types.



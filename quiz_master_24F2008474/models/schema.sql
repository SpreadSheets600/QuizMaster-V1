-- USERS TABLE: Stores Information About The Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT CHECK(role IN ('user', 'admin')) NOT NULL DEFAULT 'user'
);

-- SUBJECTS TABLE: Stores Information About Different Subjects
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- CHAPTERS TABLE: Stores Information About The Chapters In Each Subject
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- QUIZZES TABLE: Stores Information About The Quizzes Conducted For Each Chapter
CREATE TABLE quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    date_of_quiz DATE NOT NULL,
    time_duration TEXT CHECK(length(time_duration) = 5),  -- Format HH:MM
    remarks TEXT,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

-- QUESTIONS TABLE: Stores The Questions For Each Quiz
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    question_statement TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    option4 TEXT NOT NULL,
    correct_option INTEGER CHECK(correct_option BETWEEN 1 AND 4) NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

-- SCORES TABLE: Stores The Scores Of Each User In Each Quiz
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp_of_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_score INTEGER NOT NULL CHECK(total_score >= 0),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

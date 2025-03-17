CREATE TABLE
  users (
    id integer PRIMARY KEY AUTO_INCREMENT,
    username varchar(50) UNIQUE NOT NULL,
    password varchar(100) NOT NULL,
    full_name varchar(100) NOT NULL,
    email varchar(100) UNIQUE NOT NULL,
    role varchar(5) NOT NULL DEFAULT 'user'
  );

CREATE TABLE
  subjects (
    id integer PRIMARY KEY AUTO_INCREMENT,
    name varchar(100) UNIQUE NOT NULL,
    description text
  );

CREATE TABLE
  chapters (
    id integer PRIMARY KEY AUTO_INCREMENT,
    name varchar(100) NOT NULL,
    description text,
    subject_id integer NOT NULL
  );

CREATE TABLE
  quizzes (
    id integer PRIMARY KEY AUTO_INCREMENT,
    chapter_id integer NOT NULL,
    subject_id integer NOT NULL,
    date_of_quiz date NOT NULL,
    quiz_name varchar(100) NOT NULL,
    time_duration varchar(5) NOT NULL COMMENT 'Format HH:MM',
    remarks text
  );

CREATE TABLE
  questions (
    id integer PRIMARY KEY AUTO_INCREMENT,
    quiz_id integer NOT NULL,
    question_statement text NOT NULL,
    option1 text NOT NULL,
    option2 text NOT NULL,
    option3 text NOT NULL,
    option4 text NOT NULL,
    correct_options integer NOT NULL,
    marks integer NOT NULL DEFAULT 4,
    negative_marks integer NOT NULL DEFAULT 1,
    question_image varchar(200),
    option1_image varchar(200),
    option2_image varchar(200),
    option3_image varchar(200),
    option4_image varchar(200)
  );

CREATE TABLE
  quizzes_attempts (
    id integer PRIMARY KEY AUTO_INCREMENT,
    quiz_id integer NOT NULL,
    user_id integer NOT NULL,
    question_id integer NOT NULL,
    start_time datetime DEFAULT (now ()),
    end_time datetime,
    answers varchar(500) NOT NULL,
    attempt_date datetime NOT NULL DEFAULT (now ())
  );

CREATE TABLE
  scores (
    id integer PRIMARY KEY AUTO_INCREMENT,
    quiz_id integer NOT NULL,
    user_id integer NOT NULL,
    timestamp_of_attempt datetime DEFAULT (now ()),
    total_score integer NOT NULL,
    correct_answers integer NOT NULL,
    wrong_answers integer NOT NULL,
    skipped integer NOT NULL
  );

ALTER TABLE chapters ADD FOREIGN KEY (subject_id) REFERENCES subjects (id);

ALTER TABLE quizzes ADD FOREIGN KEY (chapter_id) REFERENCES chapters (id);

ALTER TABLE quizzes ADD FOREIGN KEY (subject_id) REFERENCES subjects (id);

ALTER TABLE questions ADD FOREIGN KEY (quiz_id) REFERENCES quizzes (id);

ALTER TABLE quizzes_attempts ADD FOREIGN KEY (quiz_id) REFERENCES quizzes (id);

ALTER TABLE quizzes_attempts ADD FOREIGN KEY (user_id) REFERENCES users (id);

ALTER TABLE quizzes_attempts ADD FOREIGN KEY (question_id) REFERENCES questions (id);

ALTER TABLE scores ADD FOREIGN KEY (quiz_id) REFERENCES quizzes (id);

ALTER TABLE scores ADD FOREIGN KEY (user_id) REFERENCES users (id);
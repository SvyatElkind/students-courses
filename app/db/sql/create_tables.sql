CREATE TABLE IF NOT EXISTS "groups" (
    id VARCHAR(5) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    group_id VARCHAR(5),
    FOREIGN KEY (group_id)
        REFERENCES "groups" (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS student_course (
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
);


GRANT USAGE ON SCHEMA public TO principal;
GRANT ALL ON ALL TABLES IN SCHEMA public TO principal;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO principal;


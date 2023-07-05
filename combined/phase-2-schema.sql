USE phase;

DROP TABLE IF EXISTS Alumni;

DROP TABLE IF EXISTS Form1;

DROP TABLE IF EXISTS Enrollments;

DROP TABLE IF EXISTS GraduationApplications;

DROP TABLE IF EXISTS DegreeRequirement;

DROP TABLE IF EXISTS Prerequisite;

DROP TABLE IF EXISTS Meeting;

DROP TABLE IF EXISTS Section;

DROP TABLE IF EXISTS courseFeedback;

DROP TABLE IF EXISTS Course;

DROP TABLE IF EXISTS User;

DROP TABLE IF EXISTS Application;

DROP TABLE IF EXISTS ApplicationReview;

DROP TABLE IF EXISTS RecommendationLetterReview;

DROP TABLE IF EXISTS RecommendationLetter;

DROP TABLE IF EXISTS Person;

DROP TABLE IF EXISTS Program;

CREATE TABLE Program (
    program_id INT(8) NOT NULL UNIQUE AUTO_INCREMENT,
    program_name enum('MS', 'PhD') DEFAULT ('MS'),
    program_major VARCHAR(255) NOT NULL,
    program_gpa FLOAT4 NOT NULL,
    program_credits INT4 NOT NULL,
    program_department VARCHAR(50),
    PRIMARY KEY (
        program_id,
        program_name,
        program_major
    )
);

INSERT INTO
    Program (
        program_id,
        program_major,
        program_gpa,
        program_credits,
        program_department
    )
VALUES
    (1, 'Computer Science', 3.0, 30, 'CS');

INSERT INTO
    Program (
        program_id,
        program_name,
        program_major,
        program_gpa,
        program_credits,
        program_department
    )
VALUES
    (7, 'PhD', 'Computer Science', 3.5, 36, 'CS');

CREATE TABLE Person (
    user_id INT(8) NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zip VARCHAR(100),
    country VARCHAR(100),
    phone INT(10),
    birthdate DATE,
    ssn INT(9),
    gender VARCHAR(100),
    pronouns VARCHAR(100),
    race VARCHAR(100),
    program_id INT(8),
    advisor_id INT(8),
    FOREIGN KEY (advisor_id) REFERENCES Person (user_id),
    FOREIGN KEY (program_id) REFERENCES Program (program_id)
);

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (83674927, 'Bhagi', 'Narahari');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (83674725, 'Hyeong-Ah', 'Choi');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (11111113, 'Test', 'Faculty');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (83927725, 'James', 'Taylor');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (86375082, 'John', 'Doe');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (98203756, 'Steve', 'Harvey');

INSERT INTO
    Person (user_id, first_name, last_name, advisor_id)
VALUES
    (55555555, 'Paul', 'McCartney', 83674927);

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (74958673, 'Tommy', 'Riffe');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (77347777, 'Tim', 'Wood');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (02937499, 'Seeam', 'Khan');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (88888888, 'Billie', 'Holiday');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (99999999, 'Diana', 'Krall');

INSERT INTO
    Person (user_id, first_name, last_name, ssn)
VALUES
    (12312312, 'John', 'Lennon', 111111111);

INSERT INTO
    Person (user_id, first_name, last_name, ssn)
VALUES
    (66666665, 'Ringo', 'Starr', 222111111);

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (27403756, 'Gabriel', 'Parmer');

INSERT INTO
    Person (user_id, first_name, last_name, advisor_id)
VALUES
    (66666666, 'George', 'Harrison', 27403756);

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (77777777, 'Eric', 'Clapton');

INSERT INTO
    Person (user_id, first_name, last_name)
VALUES
    (72085738, 'Chair', 'CAC');
    

CREATE TABLE RecommendationLetter (
    user_id INT(8) NOT NULL,
    sender VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    affiliation VARCHAR(255),
    sender_email VARCHAR(255),
    letter LONGTEXT,
    FOREIGN KEY (user_id) REFERENCES Person (user_id),
    PRIMARY KEY (user_id, sender)
);

CREATE TABLE RecommendationLetterReview (
    user_id INT(8) NOT NULL,
    sender VARCHAR(255) NOT NULL,
    worker_id INT(8) NOT NULL,
    rating INT(1),
    generic BOOLEAN,
    credible BOOLEAN,
    FOREIGN KEY (user_id, sender) REFERENCES RecommendationLetter (user_id, sender),
    FOREIGN KEY (worker_id) REFERENCES Person (user_id),
    PRIMARY KEY (
        worker_id,
        user_id,
        sender
    )
);

CREATE TABLE Application (
    user_id INT(8) NOT NULL UNIQUE,
    dateSubmitted DATE NOT NULL,
    advisor INT(8),
    decision enum ('Incomplete Application','Application Submitted', 'Application Materials Missing: T','Application Materials Missing: TR','Application Materials Missing: R', 'Admission Decision: Accepted', 'Admission Decision: Accepted with Aid', 'Admission Decision: Rejected') DEFAULT ('Incomplete Application'),
    semester enum ('SPRING', 'SUMMER', 'FALL') DEFAULT ('FALL'),
    appYear INT(4),
    degreeType enum ('MS', 'PhD') DEFAULT ('MS'),
    GREVerbal INT3,
    GREAdvanced INT3,
    GRESubject enum (
        'Chemistry',
        'Mathematics',
        'Physics',
        'Psychology'
    ) DEFAULT (NULL),
    GREQuantitative BIGINT,
    GREYear INT4,
    TOEFLscore INT2,
    TOEFLdate INT4,
    areas_of_interest LONGTEXT,
    experience LONGTEXT,
    transcripts BOOLEAN,
    prior_degrees enum ('BS', 'MS', 'PhD') DEFAULT (NULL),
    gpa DOUBLE,
    major VARCHAR(255),
    grad_year INT4,
    university VARCHAR(255),
    PRIMARY KEY (
        user_id,
        dateSubmitted,
        decision
    ),
    FOREIGN KEY (user_id) REFERENCES Person (user_id),
    FOREIGN KEY (advisor) REFERENCES Person (user_id)
);

INSERT INTO
    Application (user_id, dateSubmitted, advisor)
VALUES
    (86375082, NOW(), 77347777);

INSERT INTO
    Application (user_id, dateSubmitted, advisor)
VALUES
    (98203756, NOW(), 77347777);

INSERT INTO
    Application (user_id, dateSubmitted, advisor)
VALUES
    (12312312, NOW(), 77347777);

CREATE TABLE ApplicationReview (
    worker_id int(8) NOT NULL,
    user_id int(8) NOT NULL,
    rating int(1),
    deficiencycourses varchar(255),
    reject_reason varchar(255),
    comments varchar(40),
    FOREIGN KEY (user_id) REFERENCES Person (user_id),
    FOREIGN KEY (worker_id) REFERENCES Person (user_id)
);

CREATE TABLE User (
    role ENUM (
        'APPLICANT',
        'STUDENT',
        'FACULTY',
        'GS',
        'ADVISOR',
        'ADMIN',
        'ALUMNI'
    ) DEFAULT ('STUDENT'),
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_id INT(8) NOT NULL,
    cac int(8) DEFAULT(0),
    PRIMARY KEY (username, user_id),
    FOREIGN KEY (user_id) references Person (user_id)
);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('STUDENT', 'gharrison', 'password', 66666666);

INSERT INTO
    User (role, username, password, user_id, cac)
VALUES
    ('FACULTY', 'cac', 'password', 72085738, 1);
    

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('GS', 'skhan', 'password', 02937499);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('ADVISOR', 'gparmer', 'password', 27403756);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('STUDENT', 'pmccartney', 'password', 55555555);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('FACULTY', 'NarahariFaculty', 'password', 83674927);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('ADVISOR', 'NarahariAdvisor', 'password', 83674927);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('FACULTY', 'Choi', 'password', 83674725);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('ALUMNI', 'eclapton', 'password', 77777777);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('FACULTY', 'test', 'password', 11111113);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('ADMIN', 'admin', 'password', 83674927);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('STUDENT', 'james', 'password', 83927725);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('ALUMNI', 'jtaylor', 'password', 83927725);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('STUDENT', 'tommy', 'password', 74958673);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('ADVISOR', 'advisor', 'password', 77347777);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('STUDENT', 'bholiday', 'password', 88888888);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('STUDENT', 'dkrall', 'password', 99999999);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('APPLICANT', 'jlennon', 'password', 12312312);

INSERT INTO
    User (role, username, password, user_id)
VALUES
    ('APPLICANT', 'rstarr', 'password', 66666665);

CREATE TABLE Course (
    course_code VARCHAR(10) NOT NULL UNIQUE PRIMARY KEY,
    type VARCHAR(10),
    title VARCHAR(50),
    credit_hours INTEGER,
    department VARCHAR(50),
    description TEXT
);

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6221', 'SW Paradigms', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6461', 'Computer Architecture', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6212', 'Algorithms', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6220', 'Machine Learning', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6232', 'Networks 1', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6233', 'Networks 2', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6241', 'Database 1', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6242', 'Database 2', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6246', 'Compilers', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6260', 'Multimedia', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6251', 'Cloud Computing', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6254', 'SW Engineering', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6262', 'Graphics 1', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6283', 'Security 1', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6284', 'Cryptography', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6286', 'Network Security', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6325', 'Algorithms 2', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6339', 'Embedded Systems', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('CSCI 6384', 'Cryptography 2', 3, 'CS');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('ECE 6241', 'Communication Theory', 3, 'ECE');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('ECE 6242', 'Information Theory', 2, 'ECE');

INSERT INTO
    Course (course_code, title, credit_hours, department)
VALUES
    ('MATH 6210', 'Logic', 2, 'MATH');

CREATE TABLE Section (
    crn INTEGER UNIQUE NOT NULL,
    number INTEGER NOT NULL,
    course VARCHAR(10) NOT NULL,
    semester VARCHAR(15),
    professor INT(8),
    studentsEnrolled INTEGER,
    seatsAvailable INTEGER,
    waitlist INTEGER,
    waitlistmax INTEGER,
    PRIMARY KEY (course, number),
    FOREIGN KEY (course) REFERENCES Course (course_code),
    FOREIGN KEY (professor) REFERENCES Person (user_id)
);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1234, 1, 'CSCI 6221', 10, 25, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1235, 1, 'CSCI 6461', 15, 30, 83674927);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1236, 1, 'CSCI 6212', 20, 25, 83674725);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1237, 1, 'CSCI 6232', 7, 15, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1238, 1, 'CSCI 6233', 23, 30, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1239, 1, 'CSCI 6241', 4, 15, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1240, 1, 'CSCI 6242', 17, 20, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1241, 1, 'CSCI 6246', 4, 15, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1242, 1, 'CSCI 6251', 1, 10, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1243, 1, 'CSCI 6254', 24, 30, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1244, 1, 'CSCI 6260', 11, 20, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1245, 1, 'CSCI 6262', 10, 20, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1246, 1, 'CSCI 6283', 18, 25, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1247, 1, 'CSCI 6284', 21, 25, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1248, 1, 'CSCI 6286', 33, 35, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1249, 1, 'CSCI 6384', 12, 20, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1250, 1, 'ECE 6241', 41, 50, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1251, 1, 'ECE 6242', 6, 20, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1252, 1, 'MATH 6210', 12, 20, 11111113);

INSERT INTO
    Section (
        crn,
        number,
        course,
        studentsEnrolled,
        seatsAvailable,
        professor
    )
VALUES
    (1253, 1, 'CSCI 6339', 17, 20, 11111113);

CREATE TABLE Meeting (
    classCrn INTEGER NOT NULL,
    date ENUM (
        'M',
        'T',
        'W',
        'TR',
        'F') NOT NULL,
    startTime VARCHAR(4),
    endTime VARCHAR(4),
    building VARCHAR(50),
    campus VARCHAR(50),
    room VARCHAR(50),
    PRIMARY KEY (classCrn, date, startTime, endTime),
    FOREIGN KEY (classCrn) REFERENCES Section (crn)
);

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1234, 'M', '1500', '1730', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1235, 'T', '1500', '1730', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1236, 'W', '1500', '1730', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1237, 'M', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1238, 'T', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1239, 'W', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1240, 'TR', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1241, 'T', '1500', '1730', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1242, 'M', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1243, 'M', '1530', '1800', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1244, 'TR', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1245, 'W', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1246, 'T', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1247, 'M', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1248, 'W', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1249, 'W', '1500', '1730', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1250, 'M', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1251, 'T', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1252, 'W', '1800', '2030', 'Main');

INSERT INTO
    Meeting (classCrn, date, startTime, endTime, campus)
VALUES
    (1253, 'TR', '1600', '1830', 'Main');

CREATE TABLE Prerequisite (
    course_code VARCHAR(10) NOT NULL,
    course_prereq1 VARCHAR(10) NOT NULL,
    course_prereq2 VARCHAR(10),
    PRIMARY KEY (course_code),
    FOREIGN KEY (course_code) REFERENCES Course (course_code),
    FOREIGN KEY (course_prereq1) REFERENCES Course (course_code),
    FOREIGN KEY (course_prereq2) REFERENCES Course (course_code)
);
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6233', 'CSCI 6232');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6242', 'CSCI 6241');
INSERT INTO Prerequisite(course_code, course_prereq1, course_prereq2) VALUES ('CSCI 6246', 'CSCI 6461', 'CSCI 6212');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6251', 'CSCI 6461');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6254', 'CSCI 6221');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6283', 'CSCI 6212');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6284', 'CSCI 6212');
INSERT INTO Prerequisite(course_code, course_prereq1, course_prereq2) VALUES ('CSCI 6286', 'CSCI 6283', 'CSCI 6232');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6325', 'CSCI 6212');
INSERT INTO Prerequisite(course_code, course_prereq1, course_prereq2) VALUES ('CSCI 6339', 'CSCI 6461', 'CSCI 6212');
INSERT INTO Prerequisite(course_code, course_prereq1) VALUES ('CSCI 6384', 'CSCI 6284');



CREATE TABLE DegreeRequirement (
    program_id INT(8) Not NULL,
    course_code VARCHAR(10) NOT NULL,
    PRIMARY KEY (program_id, course_code),
    FOREIGN KEY (program_id) REFERENCES Program (program_id),
    FOREIGN KEY (course_code) REFERENCES Course (course_code)
);

INSERT INTO
    DegreeRequirement (program_id, course_code)
VALUES
    (1, 'CSCI 6212');

INSERT INTO
    DegreeRequirement (program_id, course_code)
VALUES
    (1, 'CSCI 6221');

INSERT INTO
    DegreeRequirement (program_id, course_code)
VALUES
    (1, 'CSCI 6461');

CREATE TABLE GraduationApplications (
    student_id INT(8) NOT NULL UNIQUE PRIMARY KEY,
    degree INT(8) NOT NULL,
    application_date DATE NOT NULL,
    status enum ('APPROVED', 'PENDING', 'REJECTED', 'GRADUATED') DEFAULT ('PENDING'),
    thesis VARCHAR(255) NULL,
    FOREIGN KEY (student_id) REFERENCES Person (user_id),
    FOREIGN KEY (degree) REFERENCES Program (program_id)
);

CREATE TABLE Enrollments (
    student_id INT(8) NOT NULL,
    section INTEGER,
    course_id VARCHAR(10) NOT NULL,
    semester enum ('SPRING', 'SUMMER', 'FALL', 'WINTER') DEFAULT ('SPRING'),
    year YEAR NOT NULL DEFAULT (YEAR(now())),
    status enum ('FINAL', 'IN PROGRESS', 'REGISTERED') DEFAULT ('IN PROGRESS'),
    grade enum('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP') DEFAULT ('IP'),
    FOREIGN KEY (student_id) REFERENCES Person (user_id),
    FOREIGN KEY (course_id) REFERENCES Course (course_code),
    FOREIGN KEY (section) REFERENCES Section (crn),
    PRIMARY KEY (
        student_id,
        course_id,
        semester,
        year
    )
);


INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6461', 1993, 'FINAL', 'A', 1235);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6221', 1990, 'FINAL', 'A', 1234);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6212', 1995, 'FINAL', 'A', 1236);

INSERT INTO
    Enrollments (student_id, course_id, year, status, grade)
VALUES
    (83927725, 'CSCI 6220', 1995, 'FINAL', 'B');

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6232', 1996, 'FINAL', 'B', 1237);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6233', 1995, 'FINAL', 'C', 1238);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6241', 1994, 'FINAL', 'B', 1239);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6242', 1995, 'FINAL', 'C', 1240);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6246', 1995, 'FINAL', 'A', 1241);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (83927725, 'CSCI 6260', 1994, 'FINAL', 'A', 1244);


INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6212', 2022, 'FINAL', 'A', 1236);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6221', 2022, 'FINAL', 'A', 1234);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6461', 2022, 'FINAL', 'A-', 1235);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade
    )
VALUES
    (74958673, 'CSCI 6339', 2022, 'FINAL', 'B+');

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6232', 2022, 'FINAL', 'B', 1237);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6233', 2022, 'FINAL', 'B', 1238);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6241', 2022, 'FINAL', 'C+', 1239);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6242', 2022, 'FINAL', 'A', 1240);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6283', 2022, 'FINAL', 'A-', 1246);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6284', 2022, 'FINAL', 'B+', 1247);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (74958673, 'CSCI 6286', 2022, 'FINAL', 'B', 1248);

INSERT INTO
    Enrollments (student_id, course_id, year, status, grade)
VALUES
    (74958673, 'CSCI 6325', 2022, 'FINAL', 'B');


INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (88888888, 'CSCI 6212', 2022, 'IN PROGRESS', 'B', 1236);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (88888888, 'CSCI 6461', 2022, 'IN PROGRESS', 'B', 1235);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6221', 2022, 'FINAL', 'A', 1234);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6212', 2022, 'FINAL', 'A', 1236);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6461', 2022, 'FINAL', 'A', 1235);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6232', 2022, 'FINAL', 'A', 1237);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6233', 2022, 'FINAL', 'A', 1238);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6241', 2022, 'FINAL', 'B', 1239);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6246', 2022, 'FINAL', 'B', 1241);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6262', 2022, 'FINAL', 'B', 1245);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6283', 2022, 'FINAL', 'B', 1246);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (55555555, 'CSCI 6242', 2022, 'FINAL', 'B', 1240);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'ECE 6242', 2022, 'FINAL', 'C', 1251);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6221', 2022, 'FINAL', 'B', 1234);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6461', 2022, 'FINAL', 'B', 1235);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6212', 2022, 'FINAL', 'B', 1236);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6232', 2022, 'FINAL', 'B', 1237);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6233', 2022, 'FINAL', 'B', 1238);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6241', 2022, 'FINAL', 'B', 1239);


INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6242', 2022, 'FINAL', 'B', 1240);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6283', 2022, 'FINAL', 'B', 1246);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (66666666, 'CSCI 6284', 2022, 'FINAL', 'B', 1247);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6221', 2022, 'FINAL', 'B', 1234);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6212', 2022, 'FINAL', 'B', 1236);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6461', 2022, 'FINAL', 'B', 1235);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6232', 2022, 'FINAL', 'B', 1237);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6233', 2022, 'FINAL', 'B', 1238);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6241', 2022, 'FINAL', 'B', 1239);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6242', 2022, 'FINAL', 'B', 1240);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6283', 2022, 'FINAL', 'A', 1246);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6284', 2022, 'FINAL', 'A', 1247);

INSERT INTO
    Enrollments (
        student_id,
        course_id,
        year,
        status,
        grade,
        section
    )
VALUES
    (77777777, 'CSCI 6286', 2022, 'FINAL', 'A', 1248);

CREATE TABLE Form1 (
    student_id INT(8) NOT NULL,
    course_id VARCHAR(10) NOT NULL,
    degree ENUM ('MS', 'PhD') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Person (user_id),
    FOREIGN KEY (course_id) REFERENCES Course (course_code),
    PRIMARY KEY (student_id, course_id)
);

CREATE TABLE Alumni (
    student_id INT(8),
    graduation_date DATE,
    degree INT(8),
    FOREIGN KEY (student_id) REFERENCES Person (user_id),
    FOREIGN KEY (degree) REFERENCES Program (program_id)
);

INSERT INTO
    Alumni (student_id, graduation_date, degree)
VALUES
    (83927725, NOW(), 1);

INSERT INTO
    Alumni (student_id, graduation_date, degree)
VALUES
    (77777777, 2014-05-05, 1);

CREATE TABLE courseFeedback (
    course VARCHAR(10),
    feedback  VARCHAR(1024),
    name VARCHAR(10),
    Foreign Key (course) REFERENCES Course (course_code)
)
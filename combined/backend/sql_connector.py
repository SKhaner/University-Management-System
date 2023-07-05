import json

import mysql.connector as connector

connection_file = open("combined/backend/connection.json")
connection_details = json.load(connection_file)


def fetch_all_students():
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    query = "SELECT user_id, first_name, last_name, status FROM Person JOIN Enrollments ON Person.user_id = " \
            "Enrollments.student_id;"

    cursor.execute(query)
    results = cursor.fetchall()

    students = []
    for result in results:
        students.append({
            "id": result[0],
            "first_name": result[1],
            "last_name": result[2],
            "status": result[3]
        })

    cursor.close()
    connection.close()
    return students


def get_connection():
    return connector.connect(host=connection_details["host"],
                             user=connection_details["user"],
                             password=connection_details["pass"],
                             port=connection_details["port"],
                             database=connection_details["database"])


def get_student_form1(student_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(
        "SELECT student_id, course_id, course_code, credit_hours FROM Form1 JOIN Course ON Form1.course_id = "
        "Course.course_code WHERE student_id = %s",
        (student_id,))
    forms = cursor.fetchall()
    cursor.close()
    connection.close()
    return forms


def verify_form1(program_id, array_of_dictionaries):
    ## Verify classes are included
    degree_classes = get_degree_classes(program_id)
    program = get_program(program_id)
    if degree_classes is not None:
        for x in degree_classes:
            if not class_in_array(x["course_code"], array_of_dictionaries):
                return False
    return True

    ##Verify Credits are met
    credit_count = 0
    credits_in_program = 0
    program_credits = program["program_credits"]
    for x in array_of_dictionaries:
        class_details = get_class(x["course_id"])
        credit_count += int(class_details["credit_hours"])
        if class_details["department"] == program["program_department"]:
            credits_in_program += int(class_details["credit_hours"])
    if credit_count < program_credits:
        return False

    if program["program_name"] == 'MS':
        if credit_count - credits_in_program > 6:
            return False
    else:
        if credits_in_program < 30:
            return False

    user_info = get_person_information(array_of_dictionaries[0]["user_id"])
    if user_info is None:
        return False
    if len(array_of_dictionaries) > 0:
        for x in array_of_dictionaries:
            if not course_exists(x["course_id"]):
                return False
        return True
    return False


def get_program(program_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM Program "
                   "WHERE program_id = %s", (program_id,))
    results = cursor.fetchone()
    cursor.close()
    connection.close()
    return results


def get_degree_classes(program_id):
    connection = get_connection()
    cursor =connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM Course JOIN DegreeRequirement ON Course.course_code = DegreeRequirement.course_code "
                   "WHERE program_id = %s", (program_id, ))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    print(results)
    return results


def get_class(class_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM Course WHERE course_code = %s", (class_id, ))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def class_in_array(class_code, array):
    for x in array:
        if x["course_code"] == class_code:
            return True
    return False


def class_in_transcript(class_code, array):
    for x in array:
        if x["course_id"] == class_code:
            return True
    return False


def verify_requirements_met(array_of_dictionaries, program_id):
    requirements = get_program_requirements(program_id)
    gpa = requirements["program_gpa"]
    level = requirements["program_name"]
    current_value = 0
    in_dept_credits = 0
    out_dept_credits = 0
    for x in array_of_dictionaries:
        course = get_course(x["course_id"])
        if requirements["program_department"] == course["department"]:
            in_dept_credits += course["credit_hours"]
        else:
            out_dept_credits += course["credit_hours"]
        value = 0
        match x["grade"]:
            case 'A':
                value = 4
            case 'A-':
                value = 3.7
            case 'B+':
                value = 3.2
            case 'B':
                value = 3
            case 'B-':
                value = 2.7
            case 'C+':
                value = 2.2
            case 'C':
                value = 2
            case 'F':
                value = 1
        current_value += (value * course["credit_hours"])
    current_gpa = current_value / len(array_of_dictionaries)
    if current_gpa < gpa:
        return False

    num_bad = 0
    for x in array_of_dictionaries:
        match x['grade']:
            case 'B-':
                num_bad += 1
            case 'C+':
                num_bad += 1
            case 'C':
                num_bad += 1
            case 'F':
                num_bad += 1
    if level == 'MS':
        if num_bad > 2:
            return False
    else:
        if num_bad > 1:
            return False
    if out_dept_credits + in_dept_credits < 30:
        return False
    print("\nDept Credits: " + str(in_dept_credits))
    print("\n Out Dept Credits: " + str(out_dept_credits))
    return True


def get_course(course_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_id, ))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def in_array(x, array):
    for index in array:
        if x["course_code"] == index["course_code"]:
            return True
    return False


def get_program_requirements(program_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(
        "SELECT * FROM Program WHERE program_id = %s",
        (program_id,))
    results = cursor.fetchone()
    cursor.close()
    connection.close()
    return results


def course_exists(course_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return False
    return True


def store_student_form1(array_of_dictionaries):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    for x in array_of_dictionaries:
        cursor.execute("INSERT INTO Form1 (student_id, course_id, degree) VALUES (%s, %s, %s)",
                       (x["user_id"], x["course_code"], x["degree"]))
    connection.commit()
    cursor.close()
    connection.close()
    return True


def get_graduation_application(student_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM GraduationApplications WHERE student_id = %s", (student_id,))
    application = cursor.fetchone()
    cursor.close()
    connection.close()

    if application is None:
        return None

    return application


def update_graduation_application_status(student_id, status):
    valid_statuses = ['APPROVED', 'PENDING', 'REJECTED', 'GRADUATED']
    if status not in valid_statuses:
        return False
    else:
        connection = get_connection()
        cursor = connection.cursor(buffered=True)
        cursor.execute("UPDATE GraduationApplications SET status = %s WHERE student_id = %s", (status, student_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True


def has_graduation_application(student_id):
    application = get_graduation_application(student_id)
    if application is None:
        return False
    else:
        return True


def set_user_advisor(user_id, advisor_id):
    if has_user_information(user_id):
        if has_user_information(advisor_id):
            connection = get_connection()
            cursor = connection.cursor(buffered=True)
            cursor.execute("UPDATE Person SET advisor_id = %s WHERE user_id = %s", (int(user_id), int(advisor_id)))
            connection.commit()
            connection.close()
            cursor.close()
            return True
    return False


def get_user_advisor(user_id):
    if has_advisor(user_id):
        student = get_user_information(user_id)
        advisor = get_user_information(student["advisor_id"])
        return advisor
    else:
        return None


def has_advisor(user_id):
    user = get_user_information(user_id)
    if user["advisor_id"] is None or len(str(user["advisor_id"])) == 0:
        return False
    else:
        return True


def get_user_information(username):
    if has_user_information(username):
        connection = get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        cursor.execute(
            "SELECT User.user_id, username, password, User.role, first_name, last_name, P.program_id, program_major, program_name, advisor_id FROM User JOIN Person P on User.user_id = P.user_id LEFT JOIN Program P2 on P.program_id = P2.program_id WHERE username = %s",
            (username,))
        user = cursor.fetchone()
        connection.close()
        cursor.close()
        return user
    else:
        return None


def get_person_information(user_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(
        "SELECT email, first_name, last_name, street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race FROM Person WHERE user_id = %s",
        (user_id,))
    user = cursor.fetchone()
    connection.close()
    cursor.close()
    return user


def update_personal_information(user_id, dictionary):
    if dictionary is None:
        return False
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute(
        "UPDATE Person SET first_name = %s, last_name = %s , email = %s, street_address = %s, city = %s, state = %s, "
        "zip = %s, country = %s, phone = %s, birthdate = %s, ssn = %s, gender = %s, pronouns = %s, race = %s WHERE "
        "user_id = %s",
        (dictionary["first_name"], dictionary["last_name"], dictionary["email"], dictionary["street_address"],
         dictionary["city"], dictionary["state"], dictionary["zip"], dictionary["country"], dictionary["phone"],
         dictionary["birthdate"], dictionary["ssn"], dictionary["gender"], dictionary["pronouns"], dictionary["race"],
         user_id))
    connection.commit()
    cursor.close()
    connection.close()
    return True


def get_graduation_date(user_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT graduation_date FROM Alumni WHERE student_id = %s", (user_id,))
    date = cursor.fetchone()
    cursor.close()
    connection.close()
    dictionary = {
        'date': date[0]
    }
    return dictionary


def get_graduation_applications():
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(
        "SELECT student_id, degree, application_date, status, first_name, last_name, program_id, advisor_id FROM "
        "GraduationApplications JOIN Person ON Person.user_id = GraduationApplications.student_id")
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return results


def get_student_list():
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("""
        SELECT P.*, U.role, GA.status, GA.thesis 
        FROM Person P
        JOIN User U on P.user_id = U.user_id
        LEFT JOIN GraduationApplications GA on P.user_id = GA.student_id
        WHERE U.role = 'STUDENT'
    """)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


def has_user_information(username):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM Person JOIN User U on Person.user_id = U.user_id WHERE username = %s", (username,))
    user = cursor.fetchone()
    connection.close()
    cursor.close()
    if user is None:
        return False
    else:
        return True


def is_alumni(student_id):
    result = get_alumni_information(student_id)
    if result is None:
        return False
    else:
        return True


def get_login_information(username):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result is None:
        return None

    user_dictionary = {
        "role": result[0],
        "username": result[1],
        "password": result[2]
    }
    return user_dictionary



def create_account(username, password, email, account_type):
    ##MODIFIED FOR APPS

    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    # Check if the username already exists
    cursor.execute("SELECT username FROM User WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        return "Error: Username already exists."
    id = get_next_user_id()
    #create the person first
    cursor.execute("INSERT INTO Person (user_id, email) VALUES (%s, %s)",(id, email))
    connection.commit()
    #cursor.execute("SELECT LAST_INSERT_ID()")
    user_id = cursor.lastrowid
    print(id)
    # Insert the new account information into the Users table
    cursor.execute("INSERT INTO User (user_id, role, username, password) VALUES (%s, %s, %s, %s)",
                   (id, account_type, username, password))
    # Insert the user's basic information into the Person table
    # cursor.execute(
        # "INSERT INTO Person (user_id, first_name, last_name, program_id, advisor_id) VALUES (%s, "
        # "%s, %s, %s, %s)",
        # (user_id, username, '', '', '', None, None))


    connection.commit()
    cursor.close()
    connection.close()
    return None


def approve_graduation_application(application, program_id):
    form1 = get_student_form1(application["user_id"])
    finished_courses = get_transcript(application["user_id"])
    for course in form1:
        if not class_in_transcript(course["course_code"], finished_courses):
            return False
    if len(form1) == 0 or form1 is None:
        return False
    if not verify_requirements_met(finished_courses, program_id):
        return False
    return True


def get_program_id(program_name, program_major):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT program_id FROM Program WHERE program_name = %s AND program_major = %s",
                   (program_name, program_major))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

#
# def get_program(name):
#     connection = get_connection()
#     cursor = connection.cursor(buffered=True)
#     cursor.execute("SELECT * FROM Program WHERE program_name = %s", (name,))
#     result = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return result


def add_graduation_application(application_dictionary, program_id):
    status = approve_graduation_application(application_dictionary, program_id)
    if status:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO GraduationApplications (student_id, degree, application_date, status, thesis) VALUES (%s, %s, "
            "now(), 'PENDING', %s) ",
            (application_dictionary["user_id"], program_id, application_dictionary["thesis"]))
        connection.commit()
        cursor.close()
        connection.close()
        return True

    return False


def get_transcript(student_id):
    transcript_array = []
    if is_alumni(student_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT student_id, course_id, year, status, grade, semester, credit_hours, department FROM Enrollments JOIN Course C on Enrollments.course_id = C.course_code WHERE status = 'FINAL' AND "
            "student_id = %s",
            (student_id,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        for x in results:
            transcript_array.append({
                "student_id": x[0],
                "course_id": x[1],
                "year": x[2],
                "status": x[3],
                "grade": x[4],
                "semester": x[5]
            })
    else:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT student_id, course_id, year, status, grade, semester FROM Enrollments WHERE student_id = %s",
            (student_id,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        for x in results:
            transcript_array.append({
                "student_id": x[0],
                "course_id": x[1],
                "year": x[2],
                "status": x[3],
                "grade": x[4],
                "semester": x[5]
            })

    return transcript_array


def get_alumni_information(user_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute(
        "SELECT student_id, first_name, last_name FROM Person JOIN Alumni ON Person.user_id = "
        "Alumni.student_id WHERE Person.user_id = %s",
        (user_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result is None:
        return None
    else:
        alumni_information = {
            "student_id": result[0],
            "first_name": result[1],
            "last_name": result[2]
        }
        return alumni_information


def update_personal_information(user_id, information):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    cursor.execute(
        "UPDATE Person SET first_name = %s, last_name = %s, street_address = %s, city = %s, state = %s, zip = %s, country = %s, phone = %s, birthdate = %s, ssn = %s, gender = %s, pronouns = %s, race = %s, email = %s WHERE user_id = %s",
        (information["first_name"], information["last_name"], information["street_address"], information["city"], information["state"], information["zip"], information["country"], information["phone"], information["birthdate"], information["ssn"], information["gender"], information["pronouns"], information["race"], information["email"] , user_id))

    connection.commit()
    cursor.close()
    connection.close()
    return True


def get_advisor_list():
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("""
        SELECT P.user_id, P.first_name, P.last_name
        FROM Person P
        JOIN User U ON P.user_id = U.user_id
        WHERE U.role = 'ADVISOR'
    """)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    dictionaries = []
    for x in result:
        dictionaries.append({
            "user_id": x["user_id"],
            'first_name': x["first_name"],
            'last_name': x["last_name"]
        })
    return dictionaries


def update_student_advisor(student_id, advisor_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("UPDATE Person SET advisor_id = %s WHERE user_id = %s", (advisor_id, student_id))
    connection.commit()
    cursor.close()
    connection.close()
    return


def get_program_major_list():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT program_major FROM Program")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    program_list = [{"program_major": x[0]} for x in results]

    return program_list

def update_alumni_status(user_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("UPDATE User SET role = 'ALUMNI' WHERE user_id = %s AND role = 'STUDENT'", (user_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return



def get_advisee_list(advisor_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM Person JOIN User ON User.user_id = Person.user_id WHERE advisor_id = %s AND role = 'STUDENT'", (advisor_id, ))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


def applied_to_graduate(user_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM GraduationApplications WHERE student_id = %s", (user_id, ))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return False
    return True

def get_enrollments(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT Meeting.classCrn, Meeting.date, Meeting.startTime, Meeting.endTime
    FROM Enrollments
    JOIN Section ON Enrollments.section = Section.crn
    JOIN Meeting ON Section.crn = Meeting.classCrn
    WHERE Enrollments.student_id = %s AND status != 'FINAL';
    """, (student_id,))

    return cursor.fetchall()

def get_section_meetings(section_crn):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT Meeting.date, Meeting.startTime, Meeting.endTime, Section.semester, Section.studentsEnrolled, Section.seatsAvailable, Section.course FROM Section \
		JOIN Meeting ON Section.crn = Meeting.classCrn \
		WHERE Section.crn = %s
    """, (section_crn,))

    return cursor.fetchall()

def check_time_conflict(student_id, section_crn):
    student_enrollments = get_enrollments(student_id)
    print("student_enrollments: ")
    print(student_enrollments)
    section_meetings = get_section_meetings(section_crn)
    print("section_meetings: " )
    print(section_meetings)

    for student_meeting in student_enrollments:
        for section_meeting in section_meetings:
            if student_meeting and section_meeting and \
                student_meeting[1] == section_meeting[0] and \
                (student_meeting[2] <= section_meeting[1] and student_meeting[3] >= section_meeting[2]):
                return True

    return False

def check_prerequisites(course_code):
    # Connect to the database
    connection = get_connection()
    cursor = connection.cursor()

    # Query the Prerequisite table to check if the course has prerequisites
    cursor.execute("SELECT course_prereq1, course_prereq2 FROM Prerequisite WHERE course_code=%s", (course_code,))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    # Check if the course has prerequisites
    if result:
        return True, result
    else:
        return False, None







##apps sql quereies
def application_status(user_id):
    #possible values:
    # 'Application not Started'
    # 'Incomplete Application', 
    # 'Application Submitted'
    # 'Application Materials Missing: T', - transcript
    # 'Application Materials Missing: TR', - transcript and recomendations missing
    # 'Application Materials Missing: R', - recomendation letters missing
    # 'Admission Decision: Accepted', 
    # 'Admission Decision: Accepted with Aid', 
    # 'Admission Decision: Rejected' 

    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT decision FROM Application WHERE user_id = %s", (user_id,))
    print('user id: ' + str(user_id))
    stat = cursor.fetchone()
    cursor.close()
    connection.close()
    print('stat ' + str(stat))
    if stat is None:
        return 'Application not Started'
    # if stat['decision'] == '':
    #     return 'Application not Started'
    match stat['decision']:
            case 'Incomplete Application':
                status = 'Incomplete Application'
            case 'Application Submitted':
                status = 'Application Submitted and Under Review'
            case 'Application Materials Missing: T':
                status = 'Application Materials Missing: Transcript'
            case 'Application Materials Missing: TR':
                status = 'Application Materials Missing: Transcript and Recomendation Letters'
            case 'Application Materials Missing: R':
                status = 'Application Materials Missing: Recomendation Letters'
            case 'Application Ready':
                status = 'Application Ready'
            case 'Admission Decision: Accepted':
                status = 'Admission Decision: Accepted'
            case 'Admission Decision: Accepted with Aid':
                status = 'Admission Decision: Accepted with Aid'
            case 'Admission Decision: Rejected':
                status = 'Admission Decision: Rejected'
    return status



def is_personal_info_complete(user_id):
    #TODO check if personal info is completed. 
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT user_id, email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race FROM Person WHERE user_id = %s", (user_id,))
    info = cursor.fetchone()
    cursor.close()
    connection.close()
    if info is None:
        return False
    
    for key in info:
        if info[key] is None:
            return False
    return True

def get_personal_info(user_id):
    #DONE
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT user_id, email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race FROM Person WHERE user_id = %s", (user_id,))
    info = cursor.fetchone()
    cursor.close()
    connection.close()
    return info

def update_personal_info(user_id, email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race):
    #update or set the personal information for the user. 
    #check if a record exists
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT user_id FROM Person WHERE user_id = %s", (user_id,))
    exists = cursor.fetchone()
    if exists is None:
        #insert
        cursor.execute("INSERT INTO Person (user_id, email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(user_id, email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race))
        connection.commit()
        cursor.close()
        connection.close()
        return
    else:
        #update

        cursor.execute("UPDATE Person SET email = %s, first_name = %s, last_name = %s, street_address = %s, city = %s, state = %s, zip = %s, country = %s, phone = %s, birthdate = %s, ssn = %s, gender = %s, pronouns = %s, race = %s WHERE user_id = %s", (email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        return
def get_applicant_advisor_id(user_id):
    #returns the user_id of the advisor for the applicant.
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT advisor_id FROM Person WHERE user_id = %s", (user_id,))
    advisor = cursor.fetchone()
    cursor.close()
    connection.close()
    return advisor['advisor_id']

def get_applicant_advisor_name(user_id):
    #returns the advisors name of the applicant
    advisor_id = get_applicant_advisor_id(user_id)
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT first_name, last_name FROM Person WHERE user_id = %s", (advisor_id,))
    advisor = cursor.fetchone()
    if advisor is None:
        return None
    cursor.close()
    connection.close()
    return advisor['first_name'] + ' ' + advisor['last_name']

def update_student_application(user_id, decision, semester, appYear, degreeType, GREVerbal, GREAdvanced, GRESubject, GREQuantitative, GREYear , TOEFLscore, TOEFLdate, areas_of_interest, experience, prior_degrees, gpa, major, grad_year, university):
    #check if it is being updated or inserted
    #datesubmitted
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT user_id FROM Application WHERE user_id = %s", (user_id,))
    exists = cursor.fetchone()
    if exists is None:
        #doesn't exist
        #insert
        cursor.execute("INSERT INTO Application (user_id, dateSubmitted, decision, semester, appYear, degreeType, GREVerbal, GREAdvanced, GRESubject, GREQuantitative, GREYear , TOEFLscore, TOEFLdate, areas_of_interest, experience, prior_degrees, gpa, major, grad_year, university) values (%s,NOW(), %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                                (user_id,                decision, semester, appYear, degreeType, GREVerbal, GREAdvanced, GRESubject, GREQuantitative, GREYear , TOEFLscore, TOEFLdate, areas_of_interest, experience, prior_degrees, gpa, major, grad_year, university))
        connection.commit()
        cursor.close()
        connection.close()
        return
    else:
        cursor.execute("UPDATE Application SET dateSubmitted = NOW(), decision = %s, semester = %s, appYear = %s, degreeType = %s, GREVerbal = %s, GREAdvanced = %s, GRESubject = %s, GREQuantitative = %s, GREYear = %s, TOEFLscore = %s, TOEFLdate = %s, areas_of_interest = %s, experience = %s, prior_degrees = %s, gpa = %s, major = %s, grad_year = %s, university = %s WHERE user_id = %s", (decision, semester, appYear, degreeType, GREVerbal, GREAdvanced, GRESubject, GREQuantitative, GREYear , TOEFLscore, TOEFLdate, areas_of_interest, experience, prior_degrees, gpa, major, grad_year, university, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        return

def get_student_application(user_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT * FROM Application WHERE user_id = %s", (user_id,))
    app = cursor.fetchone()
    if app is None:
        return None
    for key in app:
        if app[key] is None:
            app[key] = ''
    return app

def update_student_transcript(user_id, transcripts):
    #TODO
    #add the table for submitting and the update of the decision feild in the student transcript feild.
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT user_id FROM Application WHERE user_id = %s", (user_id,))
    cursor.execute("UPDATE Person SET transcripts = %s WHERE user_id = %s", (transcripts, user_id))
    connection.commit()
    cursor.close()
    connection.close()


def get_recomendation_letters(user_id):

    # cursor.execute(""" Select sender, senderemail FROM recommendationletters where studentUID = %s""", (session['uid'],))
    #     reqs = cursor.fetchall()
    #     print(len(reqs))
    #     if len(reqs) < 3:
    #         return render_template("sendletters.html",showRecomender = False, recrequest = None, requests= reqs, cansend= True)
    #     else:
    #         return render_template("sendletters.html",showRecomender = False, recrequest = None, requests= reqs, cansend= False)

    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT sender, sender_email FROM RecommendationLetter WHERE user_id = %s", (user_id,))
    letters = cursor.fetchall()
    cursor.close()
    connection.close()
    return letters

def update_application_status_for_letter(user_id):
    #removed that requirement from the status.
    #checks the status if it has been submitted it cannot be changed 

    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)


# case 'Incomplete Application':
#                 status = 'Incomplete Application'
#             case 'Application Submitted':
#                 status = 'Application Submitted and Under Review'
#             case 'Application Materials Missing: T':
#                 status = 'Application Materials Missing: Transcript'
#             case 'Application Materials Missing: TR':
#                 status = 'Application Materials Missing: Transcript and Recomendation Letters'
#             case 'Application Materials Missing: R':
#                 status = 'Application Materials Missing: Recomendation Letters'
#             case 'Application Ready':
#                 status = 'Application Ready'
#             case 'Admission Decision: Accepted':
#                 status = 'Admission Decision: Accepted'
#             case 'Admission Decision: Accepted with Aid':
#                 status = 'Admission Decision: Accepted with Aid'
#             case 'Admission Decision: Rejected':
#                 status = 'Admission Decision: Rejected'


    curstatus = application_status(user_id)
    newStatus = None
    print('curstatus' + curstatus)
    match curstatus:
        case 'Application not Started':
            #non
            return
        case 'Incomplete Application':
            #non
            return
        case 'Application Submitted and Under Review':
            #non
            return
        case 'Application Materials Missing: Transcript':
            return
        case 'Application Ready':
            return
        case 'Application Materials Missing: Transcript and Recomendation Letters':
            print('here')
            newStatus = 'Application Materials Missing: Transcript'
        case 'Application Materials Missing: Recomendation Letters':
            #cgane to
            newStatus = 'Application Ready'
        case 'Admission Decision: Accepted':
            return
        case 'Admission Decision: Accepted with Aid':
            return
        case 'Admission Decision: Rejected':
            return
    if newStatus is None:
        return 
    print('new status '+ newStatus)
    cursor.execute("UPDATE Application SET decision = %s WHERE user_id = %s", (newStatus, user_id))
    connection.commit()
    cursor.close()
    connection.close()
    return


def update_application_status_for_transcript(user_id):
    #removed that requirement from the status.
    #checks the status if it has been submitted it cannot be changed 

    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)

    curstatus = application_status(user_id)
    newStatus = None
    match curstatus:
        case 'Application not Started':
            #non
            return
        case 'Incomplete Application':
            #non
            return
        case 'Application Submitted':
            #non
            return
        case 'Application Materials Missing: T':
            #cgane to
            newStatus = 'Application Ready'

        case 'Application Ready':
            return
        case 'Application Materials Missing: TR':
            newStatus = 'Application Materials Missing: R'
        case 'Application Materials Missing: R':
            return
        case 'Admission Decision: Accepted':
            return
        case 'Admission Decision: Accepted with Aid':
            return
        case 'Admission Decision: Rejected':
            return
    if newStatus is None:
        return
    cursor.execute("UPDATE Application SET decision = %s, WHERE user_id = %s", (newStatus, user_id))
    connection.commit()
    cursor.close()
    connection.close()
    return
    

def add_recommendation_letter(user_id, sender, senderemail, letter, title, affiliation):
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("INSERT INTO RecommendationLetter (user_id, sender, sender_email, letter, title, affiliation) VALUES (%s, %s, %s, %s,%s,%s)",(user_id, sender, senderemail, letter, title, affiliation))
    update_application_status_for_letter(user_id)
    connection.commit()
    cursor.close()
    connection.close()

def check_if_unique_letter(sender):
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("SELECT sender FROM RecommendationLetter WHERE sender = %s",(sender,))
    row = cursor.fetchone()
    if row is None:
        cursor.close()
        connection.close()
        return True
    else:
        cursor.close()
        connection.close()
        return False
def get_applications(worker_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True,dictionary=True)
    cursor.execute("""SELECT Application.user_id, Person.first_name, Person.last_name FROM Application
            INNER JOIN Person on Application.user_id = Person.user_id
            LEFT JOIN ApplicationReview on Application.user_id = ApplicationReview.user_id 
            WHERE NOT EXISTS (SELECT worker_id FROM ApplicationReview WHERE worker_id = %s AND user_id = Application.user_id) AND Application.decision = 'Application Submitted'
             """,(worker_id,))
    pend = cursor.fetchall()
    cursor.close()
    connection.close()
    return pend

def get_next_user_id():
    for x in range(1000, 99999999):
        if in_database(x) is False:
            return x
    return -1


def in_database(x):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Person WHERE user_id = %s", (x, ))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result is None:
        return False
    else:
        return True

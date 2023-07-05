import os

from flask import Flask, request, render_template, session, redirect, url_for
from flask_mysqldb import MySQL

from app import app

from sql_connector import get_login_information, update_graduation_application_status, get_student_list, get_transcript, \
    get_student_form1, get_user_information, create_account, get_connection

db = get_connection()

@app.route('/regdashboard')
def regdashboard():
	if 'user_type' not in session:
		return render_template('errors/403.html')
	mycursor = db.connection.cursor()
	# get list of courses	
	# mycursor.execute("SELECT dept.abbreviation AS department_abbreviation, course.number AS course_number, section.number AS section_number, course.title AS course_title, course.hours AS course_hours, section.crn AS section_crn, CONCAT(user.firstname, ' ', user.lastname) AS section_instructor,GROUP_CONCAT(DISTINCT CONCAT(day.abbreviation, ' ', timeslot.starttime, '-', timeslot.endtime) SEPARATOR ', ') AS meeting_times FROM  section  JOIN course ON section.course_id = course.id JOIN department AS dept ON course.department_id = dept.id JOIN professor ON section.professor_id = professor.id JOIN staff ON professor.staff_id = staff.id JOIN user ON staff.user_id = user.id JOIN meetingtime ON section.id = meetingtime.section_id JOIN timeslot ON meetingtime.timeslot_id = timeslot.id JOIN day ON meetingtime.day_id = day.id GROUP BY section.id;")
	mycursor.execute("""
SELECT Course.department, Course.course_code, Course.title, Course.credit_hours, Section.crn, Section.number,
       CONCAT(Person.first_name, ' ', Person.last_name) AS professor_name, CONCAT(Meeting.startTime, '-' , Meeting.endTime) AS meeting_times, 
       Section.campus, Section.studentsEnrolled, Section.seatsAvailable
        FROM Course
        JOIN Section ON Course.course_code = Section.course
        JOIN Meeting ON Section.crn = Meeting.classCrn
        JOIN Person ON Section.professor = Person.user_id
        """)
	sections = mycursor.fetchall()
	#print(sections)
	# get list of courses student has registered for
	# mycursor.execute("SELECT dept.abbreviation AS department_abbreviation, course.number AS course_number, section.number AS section_number, course.title AS course_title, course.hours AS course_hours, section.crn AS section_crn, CONCAT(user.firstname, ' ', user.lastname) AS section_instructor, GROUP_CONCAT(DISTINCT CONCAT(day.abbreviation, ' ', timeslot.starttime, '-', timeslot.endtime) SEPARATOR ', ') AS meeting_times FROM student JOIN studentregistration ON student.id = studentregistration.student_id JOIN section ON studentregistration.section_id = section.id JOIN course ON section.course_id = course.id JOIN department AS dept ON course.department_id = dept.id JOIN professor ON section.professor_id = professor.id JOIN staff ON professor.staff_id = staff.id JOIN user ON staff.user_id = user.id JOIN meetingtime ON section.id = meetingtime.section_id JOIN timeslot ON meetingtime.timeslot_id = timeslot.id JOIN day ON meetingtime.day_id = day.id WHERE student.id = %s GROUP BY section.id;", (session.get('userid'), ))
	mycursor.execute("SELECT s.crn, c.course, c.title, CONCAT(p.first_name, ' ',p.last_name) \
                FROM enrollments e \
                JOIN sections s ON e.section = s.crn \
                JOIN courses c ON s.course = c.course_code \
                JOIN Person p ON s.professor = p.user_id \
                WHERE e.user_id = %s", (session.get('user_id'),))
	registered = mycursor.fetchall()
	# # get list of students 
	# mycursor.execute("SELECT s.id AS student_id, u.universityid, u.firstname, u.lastname FROM student s INNER JOIN user u ON s.user = u.id LEFT JOIN level l ON s.level = l.id;")
	# students = mycursor.fetchall()
	db.connection.commit()
	# mycursor.execute("SELECT * from studentRecords")
	# test = mycursor.fetchall()
	return render_template('extensions/regdashboard.html', sections = sections, registered = registered)


@app.route('/addclass/<crn>')
def addclass(crn):
	if 'user_type' not in session:
		return render_template('errors/403.html')
	# if session['role'] == 'student':
	# 	return render_template('errors/403.html')
	
	cursor = db.connection.cursor()
	print(crn)
	print(session.get('user_id'))
		
	cursor.execute('SELECT Meeting.date, Meeting.startTime, Meeting.endTime, section.semester, section.studentsEnrolled, section.seatsAvailable, section.course FROM section \
		JOIN Meeting ON section.crn = Meeting.id \
		WHERE section.crn = %s', (crn,))
	course_meeting_times = cursor.fetchone()
	print("course info:")
	print(course_meeting_times)
	
	if course_meeting_times['studentsEnrolled'] == course_meeting_times['seatsAvailable']:
		print("seats are full")
		jsonify(message = "No more seats available")
		
		return redirect(url_for('regdashboard'))
	
	# get sections student is registered for
	cursor.execute('SELECT section.crn, Meeting.date, Meeting.startTime, Meeting.endTime FROM section \
		JOIN Enrollments ON section.crn = Enrollments.section \
		JOIN Meeting ON section.crn = Meeting.classCrn \
		WHERE Enrollments.student_id = %s AND Enrollments.semester = section.semester', (session.get('id'),))
	student_sections = cursor.fetchall()
	print("student registered:")
	print(student_sections)
	
	overlap = 0

	starttime = course_meeting_times['starttime']  # Replace with the actual starttime
	endtime = course_meeting_times['endtime'] # Replace with the actual endtime
	semester = course_meeting_times['semester']  # Replace with the actual semester
	day = course_meeting_times['day']  # Replace with the actual day

	cursor.execute("""
		SELECT EXISTS(
			SELECT 1
			FROM Enrollments sr
			JOIN section s ON sr.section = s.crn
			JOIN Meeting md ON s.crn = md.classCrn
			WHERE sr.student_id = %s AND
				s.crn = %s AND
				md.startTime = %s AND
				md.endTime = %s AND
				sr.semester = %s AND
				md.date = %s AND 
				sr.grade IS NULL
		) AS exists_flag;
	""", (session.get('user_id'), crn, starttime, endtime, semester, day))

	result = cursor.fetchone()
	print("result: ")
	print(result)
	overlap = result['exists_flag']
	# 

	if overlap == 0:
		#Should I include term?
		cursor.execute('INSERT INTO Enrollments (student_id, section, course_id, semester, status) VALUES (%s, %s, %s, %s, %s)', (session.get('user_id'), crn, course_meeting_times['course'], semester, 'REGISTERED'))
		cursor.execute("""UPDATE section SET studentsEnrolled = studentsEnrolled + 1 WHERE crn = %s;""", (crn,))
		db.connection.commit()
		# return jsonify(success=True)
	if overlap == 1:
		print("overlap")
		jsonify(message = "There is overlap between the course you are trying to add and your current schedule")
		return redirect(url_for('regdashboard'))
	return redirect(url_for('regdashboard'))


@app.route('/drop/<crn>/<courseID>')
def drop(crn, courseID):
	
	mycursor = db.connection.cursor()
	# mycursor.execute("""SELECT sr.student, sr.section FROM studentRecords sr WHERE sr.student = %s AND sr.section = %s AND sr.finalgrade IS NULL""", (session.get('id'), crn))
	# result = mycursor.fetchone()
	print(session.get('user_id'))
	# # check if crn trying to drop is in result
	# x = any(crn in sublist for sublist in result)
	mycursor.execute("SELECT * FROM Enrollments where student_id = %s", (session.get('user_id'),))
	test = mycursor.fetchall()
	print("before drop:")
	print(test)
	# if x == True:
	print("crn in result")
	print(crn)
	mycursor.execute("""DELETE FROM Enrollments WHERE student_id = %s AND section = %s AND course_id = %s AND status = 'IN PROGRESS' OR status = 'REGISTERED';""", (session.get('user_id'), crn, courseID))
	mycursor.execute("""UPDATE section SET studentsEnrolled = studentsEnrolled - 1 WHERE crn = %s;""", (crn,))

	mycursor.execute("SELECT * FROM studentRecords where student = %s", (session.get('id'),))
	test = mycursor.fetchall()
	print("after drop:")
	print(test)

	db.connection.commit()
	

@app.route('/studentDetails/<id>', methods = ['GET', 'POST'])
def studentDetails(id):
	if 'user_type' not in session:
		return render_template('errors/403.html')
	print(session.get('user_role'))
	# temp = 0
	# if session.get('role') == 'sysAdmin':
	# 	temp = 1
	# if session.get('role') == 'gradSecretary':
	# 	temp = 1
	# if temp == 0:
	# 	return render_template('errors/403.html')
	if 'user_type' in session:
		cursor = db.connection.cursor()
		cursor.execute("SELECT u.first_name, u.last_name, sr.student_id, sr.section, sr.semester, sr.grade, c.title, c.course_code FROM Enrollments AS sr JOIN section AS sec ON sr.section = sec.crn JOIN course AS c ON sec.course = c.course_code JOIN Person AS u ON sr.student_id = u.user_id WHERE sr.student_id = %s", (id,))
		studentInfo = cursor.fetchall()
		db.connection.commit()
		if len(studentInfo) == 0:
			# flash("Student has no record!")
			# return redirect('/sysAdminDashboard')
			return render_template("extensions/studentError.html", message = "Student has no record!")
		else:
			return render_template("extensions/studentInfo.html", info = studentInfo, id = id)
	#db.connection.commit()
	#return render_template("extensions/studentInfo.html", info = studentInfo, id = id)
	
	return redirect(url_for('regdashboard'))
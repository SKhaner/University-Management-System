import random
from flask import (
    Flask,
    flash,
    request,
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
)

from sql_connector import (
    update_graduation_application_status,
    get_student_list,
    store_student_form1,
    verify_form1,
    get_advisee_list,
    get_connection,
    check_time_conflict,
    get_transcript, 
    get_student_form1, 
    get_user_information, 
    create_account, 
    get_program_major_list, 
    add_graduation_application,
    get_program_id, 
    update_personal_information, 
    get_graduation_date, 
    get_person_information, 
    get_advisor_list, 
    update_student_advisor, 
    update_alumni_status, 
    application_status, 
    is_personal_info_complete, 
    get_personal_info, 
    update_personal_info, 
    get_applicant_advisor_name,
    get_student_application,
    update_student_application,
    get_recomendation_letters,
    add_recommendation_letter,
    check_if_unique_letter,
    get_applications
)

app = Flask(__name__)
app.secret_key = "super secret"

db = get_connection()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/transcript", methods=["GET", "POST"])
def transcript():
    if "user_type" in session:
        if session["user_type"] == "STUDENT":
            transcript = get_transcript(session["user_id"])
            return render_template("view-transcript.html", course_list=transcript)
    return render_template("unauthorized-access.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            info = get_user_information(username)
            print(info)
            if info is None:
                return render_template("signin.html", error=True)
            if password == info["password"]:
                session["username"] = username
                session["password"] = password
                session["user_type"] = info["role"]
                session["user_id"] = info["user_id"]
                session["program_id"] = info["program_id"]
                session["first_name"] = info["first_name"]
                session["last_name"] = info["last_name"]
                session["advisor_id"] = info["advisor_id"]
                session["program_name"] = info["program_name"]
                return redirect(url_for("home"))
            else:
                return render_template("signin.html", error=True)
        else:
            return render_template("signin.html", error=False)


@app.route("/create-account", methods=["GET", "POST"])
def create_account_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        # Call the function to create a new account in your database
        result = create_account(username, password, email,'APPLICANT')

        if result is not None:
            # Display an error message if the username already exists

            flash('Error: Username already exists.')
            return render_template("create-account.html", session=session)
        else:
            # Redirect to the login page after the account is created
            return redirect(url_for("login"))
    else:
        return render_template("create-account.html", session=session)



@app.route("/home", methods=["GET", "POST"])
def home():
    if "username" in session:
        username = session["username"]
        print(username)
        user_type = session["user_type"]
        print(user_type)
        user_id = session["user_id"]
        print(user_id)
        match user_type:
            case "ALUMNI":
                transcript = get_transcript(user_id)
                graduation_date = get_graduation_date(session["user_id"])

                return render_template(
                    "alumni-home.html",
                    transcript=transcript,
                    graduation_date=graduation_date,
                )
            case "STUDENT":
                return render_template("student-home.html")
            case "FACULTY":
                student_id = ""
                student_list = get_student_list()
                mycursor = db.cursor(dictionary=True)
                mycursor.execute(
                    "SELECT course, number FROM Section WHERE professor = %s",
                    (user_id,),
                )
                courses = mycursor.fetchall()
                print(courses)
                if request.method == "POST":
                    student_id = request.form.get("student_id")
                return render_template(
                    "faculty-home.html",
                    student_list=student_list,
                    student_id=student_id,
                    courses=courses,
                )
            case "GS":
                mycursor = db.cursor(dictionary=True)
                mycursor.execute(
                    "SELECT u.user_id, p.first_name, p.last_name FROM User as u JOIN Person AS p ON p.user_id = u.user_id WHERE u.role = 'STUDENT' OR u.role = 'APPLICANT'"
                )
                students = mycursor.fetchall()
                print(students)
                return render_template("gs-home.html", students=students)
            
            case "ADMIN":
                mycursor = db.cursor(dictionary=True)
                mycursor.execute(
                    "SELECT u.user_id, p.first_name, p.last_name FROM User as u JOIN Person AS p ON p.user_id = u.user_id WHERE u.role = 'STUDENT'"
                )
                students = mycursor.fetchall()
                print(students)
                mycursor.execute("SELECT * FROM Section")
                courses = mycursor.fetchall()
                print(courses)
                return render_template(
                    "admin-home.html", students=students, courses=courses
                )
            case "ADVISOR":
                student_list = get_advisee_list(session["user_id"])
                form1 = []
                transcript = []

                student_id = ""
                if request.method == "POST":
                    user_id = request.form.get("student_id")
                    form1 = get_student_form1(user_id)
                    transcript = get_transcript(user_id)
                    student = get_person_information(user_id)
                    student_id = student["first_name"] + " " + student["last_name"]

                return render_template(
                    "advisor-home.html",
                    username=username,
                    user_type=user_type,
                    transcript=transcript,
                    session=session,
                    form1=form1,
                    student_list=student_list,
                    student_id=student_id,
                )

                if request.method == 'POST':
                    student_id = request.form.get("student_id")
                    form1 = get_student_form1(student_id)
                    transcript = get_transcript(student_id)

                return render_template("faculty-home.html", username=username, user_type=user_type,
                                       transcript=transcript,
                                       session=session, form1=form1, student_list=student_list)
            case 'APPLICANT':
                if not is_personal_info_complete(user_id):
                    flash("You must complete the personal information section before continuing!")
                    return redirect('/personal-information')
                status = application_status(user_id)      
                info = get_personal_info(user_id)
                if info is None:
                    name = None
                    advisor = None
                else:
                    name = str(info['first_name']) + ' ' + str(info['last_name'])
                    advisor = get_applicant_advisor_name(user_id) 

                return render_template("applicant-home.html", status = status, name = name, advisor = advisor)
            
 
    else:
        return redirect(url_for("login"))


@app.route("/classDetails/<course>", methods=["GET", "POST"])
def classDetails(course):
    mycursor = db.cursor(dictionary=True)
    mycursor.execute(
        "SELECT * FROM Person Join User ON Person.user_id = User.user_id JOIN Enrollments ON Enrollments.student_id = User.user_id JOIN Section ON Enrollments.section = Section.crn WHERE User.role = 'STUDENT' AND Section.course = %s",
        (course,),
    )
    students_in_class = mycursor.fetchall()
    print(students_in_class)
    return render_template("classDetails.html", students_in_class=students_in_class)


@app.route("/update-user-info", methods=["GET", "POST"])
def update_user_info():
    if (
        "username" not in session
    ):
        return redirect("/login")
    else:
        person = get_person_information(session["user_id"])
        print(person)
        if request.method == "POST":
            new_information = {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "email": request.form.get("email"),
                "street_address": request.form.get("street_address"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "zip": request.form.get("zip"),
                "country": request.form.get("country"),
                "phone": request.form.get("phone"),
                "birthdate": request.form.get("birthdate"),
                "ssn": request.form.get("ssn"),
                "gender": request.form.get("gender"),
                "pronouns": request.form.get("pronouns"),
                "race": request.form.get("race"),
            }
            succeeded = update_personal_information(session["user_id"], new_information)

            if succeeded:
                return render_template("success.html")
            else:
                return render_template("update-info.html", person=person, error=True)
        else:
            return render_template("update-info.html", person=person, error=False)


@app.route("/apply-grad", methods=["GET", "POST"])
def apply_grad():
    if "username" not in session:
        return redirect(url_for("home"))
    if "user_type" not in session or session["user_type"] != "STUDENT":
        return redirect("/login")
    else:
        majors = get_program_major_list()
        if request.method == "POST":
            user_id = session["user_id"]
            degree = request.form.get("degree")
            major = request.form["major"]
            thesis = request.form.get("phd_description", "")
            application_dictionary = {
                "user_id": user_id,
                "program_name": degree,
                "program_major": major,
                "thesis": thesis,
            }
            program = get_program_id(
                application_dictionary["program_name"],
                application_dictionary["program_major"],
            )
            program_id = program["program_id"]
            approved = add_graduation_application(application_dictionary, program_id)
            if approved:
                return redirect(url_for("succeeded"))
            else:
                return render_template(
                    "apply-grad.html", session=session, majors=majors, error=True
                )
        else:
            return render_template(
                "apply-grad.html", session=session, majors=majors, error=False
            )


@app.route("/success", methods=["GET"])
def succeeded():
    if "username" in session:
        return render_template("success.html")
    else:
        return render_template("unauthorized-access.html")


@app.route("/update-student", methods=["GET", "POST"])
def update_student():
    if "user_id" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        user_id = request.form.get("student-id")
        status = request.form.get("status")

        update_graduation_application_status(user_id, status)

        if status == "GRADUATED":
            update_alumni_status(user_id)
            return redirect(url_for("succeeded"))
        else:
            return redirect(url_for("update_student"))
    else:
        students = get_student_list()
        return render_template(
            "update-student.html", students=students, session=session
        )


@app.route("/update-thesis", methods=["GET", "POST"])
def update_thesis():
    if "user_id" not in session:
        return redirect(url_for("home"))
    # if session["user_type"] != 'ADVISOR' or 'ADMIN':
    #     print("Nope!")
        return redirect(url_for("home"))
    if request.method == "POST":
        user_id = request.form.get("student-id")
        status = request.form.get("status")

        saved = update_graduation_application_status(user_id, status)

        if saved is True:
            return redirect(url_for("succeeded"))
        else:
            return redirect(url_for("update_thesis"))
    else:
        students = get_student_list()
        return render_template(
            "thesis.html", students=students, session=session
        )


@app.route("/update-advisor", methods=["GET", "POST"])
def update_advisor():
    if "user_id" not in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        user_id = request.form.get("student-id")
        advisor_id = int(request.form.get("advisor"))
        if advisor_id == 0:
            advisor_id = None
        if advisor_id is not None:
            update_student_advisor(user_id, advisor_id)

        return redirect(url_for("succeeded"))
    else:
        students = get_student_list()
        advisors = get_advisor_list()

    return render_template(
        "update-advisor.html", students=students, advisors=advisors, session=session
    )


@app.route("/form1", methods=["GET", "POST"])
def form1():
    if "user_type" not in session:
        return redirect(url_for(login))

    if session["user_type"] != "STUDENT":
        return redirect(url_for("home"))

    programs = get_program_major_list()

    if request.method == "POST":
        univ_id = request.form.get("univ-id")

        degree = request.form.get("degree")
        program = request.form.get("program")
        program_id = get_program_id(degree, program)
        course_data = []
        for i in range(0, 12):
            course_field = request.form.get(f"course-{i}")
            course_number = request.form.get(f"courseNumber-{i}")
            if course_number is not None:
                course_data.append(
                    {
                        "user_id": univ_id,
                        "course_code": str(course_field) + " " + str(course_number),
                        "degree": degree,
                    }
                )
        valid = verify_form1(program_id["program_id"], course_data)
        if valid:
            success = store_student_form1(course_data)
            if success:
                return redirect(url_for("succeeded"))
        else:
            return render_template(
                "/form1.html", retry=True, session=session, programs=programs
            )

    return render_template(
        "/form1.html", retry=False, session=session, programs=programs
    )


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/application-requirements")
def application_requirements():
    if "username" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        if str(user_type) != 'APPLICANT':
            print('app')
            return redirect(url_for("login"))
        ## ADD CHECK IF PERSONAL INFOR IS DONE OTHERWISE FLASH
        if not is_personal_info_complete(user_id):
            flash("You must complete the personal information section before continuing!")
            return redirect('/personal-information')
        status = application_status(user_id)
        #TODO make the buttons selectable based 
        # match status:
        #     case 'Application not Started':
        #         appstatus = 'Not Started'
        #         recstatus = 'Not Started'
        #         transtatus = 'Not Started'
        #     case 'Incomplete Application':
        #         appstatus = 'Incomplete'
        #         recstatus = 'Not Started'
        #         transtatus = 'Not Started'
        #     case 'Application Submitted':
        #         set status for enable/complete viability
        #         appstatus = 'Completed'
        #         TODO FIGURE OUT IF ONE REC LETTER IS CONSIDERED COMPLETE
        #         recstatus = 'Completed'
        #         transtatus = 'Completed'
        #     case 'Application Materials Missing: T':
        #         appstatus = 'Completed'
        #         recstatus = 'Completed'
        #         transtatus = 'Incomplete'
        #     case 'Application Materials Missing: TR':
        #         appstatus = 'Completed'
        #         recstatus = 'Not Started'
        #         transtatus = 'Not Started'
        #     case 'Application Materials Missing: R':
        #         appstatus = 'Completed'
        #         recstatus = 'Not Started'
        #         transtatus = 'Completed'
        #     case 'Admission Decision: Accepted':
                
        #     case 'Admission Decision: Accepted with Aid':
        #         status = 'Admission Decision: Accepted with Aid'
        #     case 'Admission Decision: Rejected':
        #         status = 'Admission Decision: Rejected'


        return render_template('application-requirements.html',status = status)
    else:
        print('else')
        return redirect(url_for("login"))

@app.route('/personal-information', methods=["GET", "POST"] )
def personal_information():
    if "user_type" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        # if str(user_type) != 'APPLICANT':
        #     flash("Must be logged in!")
        #     return redirect(url_for("login"))
        
        if request.method == 'POST':
            #email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race
            email = request.form['email']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            street_address = request.form['street_address']
            city = request.form['city']
            state = request.form['state']
            zip = int(request.form['zip'])
            country = request.form['country']
            print(request.form['phone'])
            phone = int(str(request.form['phone'][0:3])+str(request.form['phone'][4:7])+str(request.form['phone'][8:13]))
            print(phone)
            birthdate = request.form['birthdate']
            print(request.form['ssn'])
            ssn = int(str(request.form['ssn'][0:3])+str(request.form['ssn'][4:6])+str(request.form['ssn'][7:12]))
            print(ssn)
            gender = request.form['gender']
            pronouns = request.form['pronouns']
            race = request.form['race']
            update_personal_info(user_id, email, first_name, last_name,street_address, city, state, zip, country, phone, birthdate, ssn, gender, pronouns, race)
            flash('Data Saved!')
            info = get_personal_info(user_id)
            for key in info:
                if info[key] is None:
                    flash("Missing: "+ str(key))
                    info[key] = ''
            info = get_user_information(username)
            session["username"] = username
            session["user_type"] = info["role"]
            session["user_id"] = info["user_id"]
            session["program_id"] = info["program_id"]
            session["first_name"] = info["first_name"]
            session["last_name"] = info["last_name"]
            session["advisor_id"] = info["advisor_id"]
            session["program_name"] = info["program_name"]

            return redirect('/personal-information')
                    
        
        info = get_personal_info(user_id)
        print(info)
        if info is None:
            print('none')
            info = {'email': '', 'first_name': '', 'last_name': '','street_address': '', 'city': '', 'state': '', 'zip': '', 'country': '', 'phone': '', 'birthdate': '', 'ssn': '', 'gender': '', 'pronouns': '', 'race': ''}
            return render_template('personal-info.html', info = info)
        else:
            for key in info:
                if info[key] is None:
                    #flash("Missing: "+ str(key))
                    info[key] = ''
            print(info)
            if info['ssn'] != '':
                #print(info['ssn'])
                info['ssn']= str(info['ssn'])[0:3] + '-' + str(info['ssn'])[3:5] + '-' + str(info['ssn'])[5:10]     
                #print(info['ssn'])
            if info['phone'] != '':
                #print(info['phone'])
                info['phone']=str(info['phone'])[0:3] + '-' + str(info['phone'])[3:6] + '-' + str(info['phone'])[6:10]
                #print(info['phone'])
            return render_template('personal-info.html', info=info )
    else:
        return redirect(url_for("login"))

@app.route('/application-form', methods=["GET", "POST"])
def application_form():
    if "username" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        if str(user_type) != 'APPLICANT':
            flash("Must be logged in!")
            return redirect(url_for("login"))
        
        curstatus=application_status(user_id)
        if curstatus != 'Application not Started' and curstatus != 'Incomplete Application':
            #cant submit
            #disable form entry
            edit = 'disabled'
            app = get_student_application(user_id)
            flash("You cannont submit an application more than once! You are in view only mode.")
            return render_template('application-form.html', app = app, edit = edit)

        if request.method == 'POST':
            #user_id, dateSubmitted, advisor, decision, semester, appYear, degreeType, GREVerbal,, GREAdvanced, GRESubject, GREQuantitative, GREYear , TOEFLscore, TOEFLdate, areas_of_interest, experience, transcripts, prior_degrees, gpa, major, grad_year, university
     ##NOW IN SQL        = request.form['dateSubmitted']
         ##advisor = request.form['advisor']
       ##     decision = request.form['decision']

            submittype = request.form['submittype']
            if submittype == 'save':
                #The application can still be edited.
                decision = 'Incomplete Application'

            if submittype == 'submit':
                #the application cannot be resubmitted
                decision = 'Application Materials Missing: TR'

            semester = request.form['semester']
            appYear = int(request.form['appYear'])
            degreeType = request.form['degreeType']
            GREVerbal = int(request.form['GREVerbal'])
            GREAdvanced = int(request.form['GREAdvanced'])
            GRESubject = request.form['GRESubject']
            GREQuantitative = int(request.form['GREQuantitative'])
            GREYear = int(request.form['GREYear'])
            TOEFLscore = int(request.form['TOEFLscore'])
            TOEFLdate = int(request.form['TOEFLdate'])
            areas_of_interest = request.form['areas_of_interest']
            experience = request.form['experience']
 ##TODO     transcripts = request.form['transcripts']       
            prior_degrees = request.form['prior_degrees']
            gpa = float(request.form['gpa'])
            major = request.form['major']
            grad_year = request.form['grad_year']
            university = request.form['university']
            update_student_application(user_id, decision, semester, appYear, degreeType, GREVerbal, GREAdvanced, GRESubject, GREQuantitative, GREYear , TOEFLscore, TOEFLdate, areas_of_interest, experience, prior_degrees, gpa, major, grad_year, university)
            
            if submittype == 'save':
                flash('Data Saved!')
                return redirect('/application-form')
            else:
                flash('Application submitted! Next Submit Recomendation letters and Transcripts!')
                return redirect('/application-requirements')
                    
        app = get_student_application(user_id)
        if app is None:
            app = {'user_id':'', 'decision':'', 'semester':'', 'appYear':'', 'degreeType':'', 'GREVerbal':'', 'GREAdvanced':'', 'GRESubject':'', 'GREQuantitative':'', 'GREYear':'' , 'TOEFLscore':'', 'TOEFLdate':'', 'areas_of_interest':'', 'experience':'', 'prior_degrees':'', 'gpa':'', 'major':'', 'grad_year':'', 'university':''}
            return render_template('application-form.html', app = app, edit='')
        else:
            
            return render_template('application-form.html', app=app, edit='')
    else:
        return redirect(url_for("login"))   

#
#Recomendation letters
@app.route('/recommendation-letters')
def recomendations():
    #TODO NEXT
   
    print('sendletters/:')
    #showRecomender - true shows the recomender view to write the recomendation
    #recrequest - dict - 'writername' , 'email' , 'sentfrom'- student first and last name
    #requests - list of dicts with ['sender'] ['email'] of the recomendation letters
    #cansend - changes weather the send recomendation letter displays or not.

    if "username" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        if str(user_type) != 'APPLICANT':
            flash("Must be logged in!")
            return redirect(url_for("login"))
        

        #Write the site here
        #Check that they are able to view this page
        curstatus=application_status(user_id)
        
        match curstatus:
            case 'Application not Started':
                flash('Need to finish the application first!')
                return redirect('/application-requirements')
            case 'Incomplete Application':
                flash('Need to finish the application first!')
                return redirect('/application-requirements')
            case 'Application Submitted':
                flash('Cannot change recommendation letters after submitting')
                #TODO RETURN - can view
            case 'Application Materials Missing: T':
                flash('Cannont submit anymore recomendation letters')
                #TODO RETURN - can view
            case 'Application Materials Missing: TR':
                #Can Submit rec letters
                print('can submit')
            case 'Application Materials Missing: R':
                #Can Submit rec letters
                print('can submit')
            case 'Application Ready':
                #can view
                print('can view')
            case 'Admission Decision: Accepted':
                flash('Cannot change recommendation letters after decision')
                return redirect('application-requirements')
            case 'Admission Decision: Accepted with Aid':
                flash('Cannot change recommendation letters after decision')
                return redirect('application-requirements')
            case 'Admission Decision: Rejected':
                flash('Cannot change recommendation letters after decision')
                return redirect('application-requirements')
        
        #then get the apps and display them
        reqs = get_recomendation_letters(user_id)
        if reqs is None:
            return render_template("recommendation-letters.html",showRecomender = False, recrequest = None, requests= None, cansend= True)
        if len(reqs) < 3:
            return render_template("recommendation-letters.html",showRecomender = False, recrequest = None, requests= reqs, cansend= True)
        else:
            return render_template("recommendation-letters.html",showRecomender = False, recrequest = None, requests= reqs, cansend= False)
    else:
        return redirect(url_for("login")) 

@app.route('/recommendation-letters/send', methods=['GET', 'POST'])
def recomendationsubmit():
    if "username" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        if str(user_type) != 'APPLICANT':
            flash("Must be logged in!")
            return redirect(url_for("login"))
       
       
        #showRecomender - true shows the recomender view to write the recomendation
        #recrequest - dict - 'writername' , 'email' , 'sentfrom'- student first and last name
        #requests - list of dicts with ['sender'] ['email'] of the recomendation letters
        #cansend - changes weather the send recomendation letter displays or not.

        #Write the site here
        if request.method == 'POST':
            #submited a new letter
            recrequest = dict()
            recrequest['writername'] = request.form['writername']
            recrequest['email'] = request.form['writeremail']
            recrequest['title'] = request.form['writertitle']
            recrequest['affiliation'] = request.form['writeraffiliation']
            recrequest['sentfrom'] = session['first_name'] + ' ' + session['last_name']
            unique = check_if_unique_letter(str(request.form['writername']))
            if not unique:
                flash("Sender must be Unique")
                return redirect('/recommendation-letters')
            
            reqs = get_recomendation_letters(user_id)
            if reqs is None:
                return render_template("recommendation-letters.html",showRecomender = True, recrequest = None, requests= None, cansend= True)
            if (len(reqs)+1) < 3:
                return render_template("recommendation-letters.html",showRecomender = True, recrequest = recrequest, requests= reqs, cansend= True)
            else:
                return render_template("recommendation-letters.html",showRecomender = True, recrequest = recrequest, requests= reqs, cansend= False)
        return redirect('/recommendation-letters')
    else:
        return redirect(url_for("login")) 

@app.route('/recommendation-letters/submit/recomender', methods=['GET', 'POST'])
def recomendationsubmitrecomender():
    #TODO FINISH THIS

    if "username" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        if str(user_type) != 'APPLICANT':
            flash("Must be logged in!")
            return redirect(url_for("login"))
        
        if request.method == 'POST':
            sender = request.form['writername']
            senderemail = request.form['writeremail']
            letter = request.form['recomendationresponce']
            title = request.form['writertitle']
            affiliation = request.form['writeraffiliation']

            add_recommendation_letter(user_id, sender, senderemail, letter, title, affiliation)
            flash('Submited Successfully')
            return redirect(url_for('recomendations'))
        return redirect(url_for('recomendations'))
            
           

    else:
        return redirect(url_for("login"))



@app.route('/pendingreview/')
def pendreview():

    if "username" in session:
        username = session["username"]
        print('username: ' + str(username))
        user_type = session["user_type"]
        print('user_type: '+ str(user_type))
        user_id = session["user_id"]
        print('user_id: ' + str(user_id))
        # if str(user_type) != '':
            # flash("Must be logged in!")
            # return redirect(url_for("login"))
        
        pend = get_applications(user_id)
        return render_template("apps_pend_review.html", rev=pend, prevreviewed = None)

    else:
        return redirect(url_for("login"))



    
    cursor = mydb.cursor(buffered=True, dictionary=True)
    if session.get('workerID') == None:
        print('not logged in')
        #user is not logged in so return all false
        return redirect('/')
    
    
    if 'workerID' not in session:        
        return render_template("apps_pend_review.html",rev= None)
    else:
        print('session ' + str(session['workerID']))

        print('session ' + str(session['workerID']))
        cursor.execute("""SELECT studentapplication.studentUID, studentapplication.firstname, studentapplication.lastname, studentapplication.studentUID FROM studentapplication
            LEFT JOIN studentapplicationreviews on studentapplication.studentUID  = studentapplicationreviews.studentUID 
            INNER JOIN students ON studentapplication.studentUID = students.UniID
            WHERE NOT EXISTS (SELECT workerID FROM studentapplicationreviews WHERE workerID = %s AND studentUID = studentapplication.studentUID) AND students.status = 'Application and Recomendations Complete'
             """,(int(session['workerID']),))

         #cursor.execute("""SELECT studentapplication.studentUID, studentapplication.firstname, studentapplication.lastname, studentapplication.studentUID FROM studentapplication
         #   LEFT JOIN studentapplicationreviews on  studentapplication.studentUID  = studentapplicationreviews.studentUID
         #   WHERE studentapplicationreviews.workerID != %s """, (int(session['workerID']),))
   
        
        print ("two")
        pend = cursor.fetchall()
        print (pend)
        cursor.execute("""SELECT studentapplication.studentUID, studentapplication.firstname, studentapplication.lastname, studentapplication.studentUID FROM studentapplication
            LEFT JOIN studentapplicationreviews on  studentapplication.studentUID  = studentapplicationreviews.studentUID
            WHERE studentapplicationreviews.workerID != %s """, (int(session['workerID']),))

        prevreviewed = cursor.fetchall()

        
        return render_template("apps_pend_review.html", rev=pend,prevreviewed = prevreviewed)

@app.route('/appreview/<ID>', methods=['GET', 'POST'])
def appreview(ID):
    
    
    if session.get('workerID') == None:
        print('not logged in')
        #user is not logged in so return all false
        return redirect('/')
    #app - application - 'name','studentUID','semester', etc
    #letters
    #reviews
    #canViewReviews
    #canAddReview
    #previouslyReviewed
    #canChangeApllicantStatus
    #showdecision
    # if 'workerID' not in session :
    #     return redirect('/')
    print('viewing review form:' + str(ID))
    cursor = mydb.cursor(buffered=True, dictionary=True)
    #get app from db
    cursor.execute("SELECT * FROM studentapplication WHERE studentUID = %s", (ID,))
    app = cursor.fetchone()
    #get letters from DB
    cursor.execute("SELECT * FROM recommendationletters WHERE studentUID = %s", (ID,))
    letters = cursor.fetchall()
    #get reviews
    cursor.execute("SELECT * FROM studentapplicationreviews INNER JOIN worker ON studentapplicationreviews.workerID = worker.wid WHERE studentUID = %s", (ID,))
    reviews = cursor.fetchall()
    #get permissions
    cursor.execute("SELECT * FROM roles WHERE roleID = (SELECT hasrole FROM worker WHERE wid = %s)", (session['workerID'],))
    perms = cursor.fetchone()
    canViewReviews = perms['canViewReviews']
    canAddReview = perms['canAddReview']
    canChangeApllicantStatus = perms['canChangeApllicantStatus']
    #check if a review exists from this wid
    cursor.execute("SELECT rating FROM studentapplicationreviews WHERE studentUID = %s AND workerID = %s", (ID,session['workerID']))
    exists = cursor.fetchone()
    if exists is None:
        previouslyReviewed = False
    else:
        previouslyReviewed = True
    print('status ' + app['status'])
    if app['status'] == 'Admit' or app['status'] == 'Reject':
        showdecision = True
    else:
        showdecision = False
    return render_template("applicationreview.html",app=app,letters=letters,reviews=reviews,canViewReviews=canViewReviews,canAddReview=canAddReview,canChangeApllicantStatus=canChangeApllicantStatus,previouslyReviewed=previouslyReviewed,showdecision=showdecision)

@app.route('/appreview/<ID>/reviewletter', methods=['GET', 'POST'])
def appreviewletter(ID):
    if session.get('workerID') == None:
        print('not logged in')
        #user is not logged in so return all false
        return redirect('/')
    # if 'workerID' not in session :
    #     return redirect('/')
    cursor = mydb.cursor(buffered=True, dictionary=True)
    print('submit on form review letter on review form')
    if request.method == 'POST':
        print('submit')
        letterID = request.form['letterID']
        rating = request.form['rating']
        generic = request.form['generic']
        credible = request.form['credible']
        cursor.execute("UPDATE recommendationletters SET rating = %s, generic = %s, credible = %s WHERE letterID = %s",(int(rating),generic,credible,int(letterID)))
        mydb.commit()
    return redirect('/appreview/'+str(ID))

@app.route('/appreview/<ID>/reviewsubmit', methods=['GET', 'POST'])
def appreviewsubmit(ID):
    if session.get('workerID') == None:
        print('not logged in')
        #user is not logged in so return all false
        return redirect('/')
    # if 'workerID' not in session :
    #     return redirect('/')
    cursor = mydb.cursor(buffered=True, dictionary=True)
    print('submit on form review ')
    if request.method == 'POST':
        print('submit')
        workerID = int(request.form['workerID'])
        studentUID = int(ID)
        rating = int(request.form['rating'])
        deficiencycourses = request.form['deficiencycourses']
        reasonsforreject = request.form['reasonsforreject']
        comments = request.form['comments']
        cursor.execute("INSERT INTO studentapplicationreviews (workerID,studentUID,rating,deficiencycourses,reasonsforreject,comments) VALUES (%s,%s,%s,%s,%s,%s)",(workerID,studentUID,rating,deficiencycourses,reasonsforreject,comments))
        mydb.commit()
    return redirect('/appreview/'+str(ID))

@app.route('/appreview/<ID>/submitdecision', methods=['GET', 'POST'])
def appreviewsubmitdecision(ID):
    if session.get('workerID') == None:
        print('not logged in')
        #user is not logged in so return all false
        return redirect('/')
    # if 'workerID' not in session :
    #     return redirect('/')
    cursor = mydb.cursor(buffered=True, dictionary=True)
    print('submit on form review on final dicision')
    if request.method == 'POST':
        print('submit')
        studentUID = int(ID)
        decision = request.form['decision']
        recommendedadvisor = request.form['recommendedadvisor']
        if decision == 'Admit with Aid' or decision == 'Admit':
            status = 'Admit'
        else:
            status = 'Reject'
        cursor.execute("UPDATE studentapplication SET status = %s, decision = %s, recommendedadvisor = %s WHERE studentUID = %s",(status,decision,recommendedadvisor,ID))
        mydb.commit()
        cursor.execute("UPDATE students SET status = %s WHERE UniID = %s",(status,ID))
        mydb.commit()
        
    return redirect('/appreview/'+str(ID))

# @app.route('/review')
# def reveiw(): 
#     cursor = mydb.cursor(buffered=True, dictionary=True)
#     cursor.execute("SELECT * FROM studentapplication")
#     application = cursor.fecthall()
#     return render_template("reviews.html")


@app.route("/regdashboard")
def regdashboard():
    if "user_type" not in session or session["user_type"] != "STUDENT":
        return redirect("/home")

    mycursor = db.cursor(dictionary=True)
    # get list of courses
    # mycursor.execute("SELECT dept.abbreviation AS department_abbreviation, course.number AS course_number, section.number AS section_number, course.title AS course_title, course.hours AS course_hours, section.crn AS section_crn, CONCAT(user.firstname, ' ', user.lastname) AS section_instructor,GROUP_CONCAT(DISTINCT CONCAT(day.abbreviation, ' ', timeslot.starttime, '-', timeslot.endtime) SEPARATOR ', ') AS meeting_times FROM  section  JOIN course ON section.course_id = course.id JOIN department AS dept ON course.department_id = dept.id JOIN professor ON section.professor_id = professor.id JOIN staff ON professor.staff_id = staff.id JOIN user ON staff.user_id = user.id JOIN meetingtime ON section.id = meetingtime.section_id JOIN timeslot ON meetingtime.timeslot_id = timeslot.id JOIN day ON meetingtime.day_id = day.id GROUP BY section.id;")
    mycursor.execute(
        """
SELECT Course.department, Course.course_code, Course.title, Course.credit_hours, Section.crn, Section.number,
       CONCAT(Person.first_name, ' ', Person.last_name) AS professor_name, CONCAT(Meeting.startTime, '-' , Meeting.endTime) AS meeting_times, 
       Section.studentsEnrolled, Section.seatsAvailable, Meeting.date AS day
        FROM Course
        JOIN Section ON Course.course_code = Section.course
        JOIN Meeting ON Section.crn = Meeting.classCrn
        JOIN Person ON Section.professor = Person.user_id
        """
    )
    sections = mycursor.fetchall()
    # get list of courses student has registered for
    # mycursor.execute("SELECT dept.abbreviation AS department_abbreviation, course.number AS course_number, section.number AS section_number, course.title AS course_title, course.hours AS course_hours, section.crn AS section_crn, CONCAT(user.firstname, ' ', user.lastname) AS section_instructor, GROUP_CONCAT(DISTINCT CONCAT(day.abbreviation, ' ', timeslot.starttime, '-', timeslot.endtime) SEPARATOR ', ') AS meeting_times FROM student JOIN studentregistration ON student.id = studentregistration.student_id JOIN section ON studentregistration.section_id = section.id JOIN course ON section.course_id = course.id JOIN department AS dept ON course.department_id = dept.id JOIN professor ON section.professor_id = professor.id JOIN staff ON professor.staff_id = staff.id JOIN user ON staff.user_id = user.id JOIN meetingtime ON section.id = meetingtime.section_id JOIN timeslot ON meetingtime.timeslot_id = timeslot.id JOIN day ON meetingtime.day_id = day.id WHERE student.id = %s GROUP BY section.id;", (session.get('userid'), ))
    mycursor.execute(
        "SELECT s.crn, c.course_code, c.title, CONCAT(p.first_name, ' ',p.last_name) AS professor_name, e.status\
                FROM Enrollments e \
                JOIN Section s ON e.section = s.crn \
                JOIN Course c ON s.course = c.course_code \
                JOIN Person p ON s.professor = p.user_id \
                WHERE e.student_id = %s AND e.status != 'FINAL' ",
        (session.get("user_id"),),
    )
    registered = mycursor.fetchall()
    # # get list of students
    # mycursor.execute("SELECT s.id AS student_id, u.universityid, u.firstname, u.lastname FROM student s INNER JOIN user u ON s.user = u.id LEFT JOIN level l ON s.level = l.id;")
    # students = mycursor.fetchall()
    db.commit()
    # mycursor.execute("SELECT * from studentRecords")
    # test = mycursor.fetchall()
    return render_template(
        "regdashboard.html", sections=sections, registered=registered
    )
    
@app.route("/regsResults", methods=["GET", "POST"])
def regsResults():
    if request.method == 'POST':
        search = request.form['search']
        print(search)
        if "user_type" not in session or session["user_type"] != "STUDENT":
            return redirect("/home")

        mycursor = db.cursor(dictionary=True)
        # get list of courses
        # mycursor.execute("SELECT dept.abbreviation AS department_abbreviation, course.number AS course_number, section.number AS section_number, course.title AS course_title, course.hours AS course_hours, section.crn AS section_crn, CONCAT(user.firstname, ' ', user.lastname) AS section_instructor,GROUP_CONCAT(DISTINCT CONCAT(day.abbreviation, ' ', timeslot.starttime, '-', timeslot.endtime) SEPARATOR ', ') AS meeting_times FROM  section  JOIN course ON section.course_id = course.id JOIN department AS dept ON course.department_id = dept.id JOIN professor ON section.professor_id = professor.id JOIN staff ON professor.staff_id = staff.id JOIN user ON staff.user_id = user.id JOIN meetingtime ON section.id = meetingtime.section_id JOIN timeslot ON meetingtime.timeslot_id = timeslot.id JOIN day ON meetingtime.day_id = day.id GROUP BY section.id;")
        mycursor.execute(
            """
    SELECT Course.department, Course.course_code, Course.title, Course.credit_hours, Section.crn, Section.number,
        CONCAT(Person.first_name, ' ', Person.last_name) AS professor_name, CONCAT(Meeting.startTime, '-' , Meeting.endTime) AS meeting_times, 
        Section.studentsEnrolled, Section.seatsAvailable, Meeting.date AS day
            FROM Course
            JOIN Section ON Course.course_code = Section.course
            JOIN Meeting ON Section.crn = Meeting.classCrn
            JOIN Person ON Section.professor = Person.user_id
            WHERE Course.course_code = %s OR Course.title = %s OR Section.crn = %s
            """, (search, search, search)
        )
        sections = mycursor.fetchall()
        # get list of courses student has registered for
        # mycursor.execute("SELECT dept.abbreviation AS department_abbreviation, course.number AS course_number, section.number AS section_number, course.title AS course_title, course.hours AS course_hours, section.crn AS section_crn, CONCAT(user.firstname, ' ', user.lastname) AS section_instructor, GROUP_CONCAT(DISTINCT CONCAT(day.abbreviation, ' ', timeslot.starttime, '-', timeslot.endtime) SEPARATOR ', ') AS meeting_times FROM student JOIN studentregistration ON student.id = studentregistration.student_id JOIN section ON studentregistration.section_id = section.id JOIN course ON section.course_id = course.id JOIN department AS dept ON course.department_id = dept.id JOIN professor ON section.professor_id = professor.id JOIN staff ON professor.staff_id = staff.id JOIN user ON staff.user_id = user.id JOIN meetingtime ON section.id = meetingtime.section_id JOIN timeslot ON meetingtime.timeslot_id = timeslot.id JOIN day ON meetingtime.day_id = day.id WHERE student.id = %s GROUP BY section.id;", (session.get('userid'), ))
        mycursor.execute(
            "SELECT s.crn, c.course_code, c.title, CONCAT(p.first_name, ' ',p.last_name) AS professor_name, e.status\
                    FROM Enrollments e \
                    JOIN Section s ON e.section = s.crn \
                    JOIN Course c ON s.course = c.course_code \
                    JOIN Person p ON s.professor = p.user_id \
                    WHERE e.student_id = %s AND e.status != 'FINAL' ",
            (session.get("user_id"),),
        )
        registered = mycursor.fetchall()
        # # get list of students
        # mycursor.execute("SELECT s.id AS student_id, u.universityid, u.firstname, u.lastname FROM student s INNER JOIN user u ON s.user = u.id LEFT JOIN level l ON s.level = l.id;")
        # students = mycursor.fetchall()
        db.commit()
        # mycursor.execute("SELECT * from studentRecords")
        # test = mycursor.fetchall()
        return render_template(
            "regdashboard.html", sections=sections, registered=registered
        )


@app.route("/addclass/<crn>")
def addclass(crn):
    if "user_type" not in session:
        return render_template("errors/403.html")
    # if session['role'] == 'student':
    # 	return render_template('errors/403.html')

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT Meeting.date, Meeting.startTime, Meeting.endTime, Section.semester, Section.studentsEnrolled, Section.seatsAvailable, Section.course FROM Section \
		JOIN Meeting ON Section.crn = Meeting.classCrn \
		WHERE Section.crn = %s",
        (crn,),
    )
    course_meeting_times = cursor.fetchone()
    print("course meets")
    print(course_meeting_times)
    if (
        course_meeting_times["studentsEnrolled"]
        == course_meeting_times["seatsAvailable"]
    ):
        jsonify(message="No more seats available")

        return redirect(url_for("regdashboard"))

    # get sections student is registered for
    cursor.execute(
        """
    SELECT Meeting.classCrn, Meeting.date, Meeting.startTime, Meeting.endTime
    FROM Enrollments
    JOIN Section ON Enrollments.section = Section.crn
    JOIN Meeting ON Section.crn = Meeting.classCrn
    WHERE Enrollments.student_id = %s;
    """,
        (session.get("user_id"),),
    )
    student_sections = cursor.fetchall()
    print("student meets")
    print(student_sections)

    overlap = 0

    starttime = course_meeting_times["startTime"]  # Replace with the actual starttime
    endtime = course_meeting_times["endTime"]  # Replace with the actual endtime
    semester = course_meeting_times["semester"]  # Replace with the actual semester
    print(semester)
    day = course_meeting_times["date"]  # Replace with the actual day

    cursor.execute(
        """
		SELECT EXISTS(
			SELECT 1
			FROM Enrollments sr
			JOIN Section s ON sr.section = s.crn
			JOIN Meeting md ON s.crn = md.classCrn
			WHERE sr.student_id = %s AND
				s.crn = %s AND
				md.startTime = %s AND
				md.endTime = %s AND
				sr.semester = %s AND
				md.date = %s AND 
				sr.grade IS NULL
		) AS exists_flag;
	""",
        (session.get("user_id"), crn, starttime, endtime, semester, day),
    )

    result = cursor.fetchone()
    overlap = result["exists_flag"]
    #

    if not check_time_conflict(session.get("user_id"), crn):
        # check if student meets prereqs
        course_id = course_meeting_times["course"]
        print("course_id: " + course_id)
        cursor.execute(
            "SELECT p.course_prereq1, p.course_prereq2 FROM Prerequisite p WHERE course_code = %s",
            (course_id,),
        )
        prereqs = cursor.fetchall()
        print(prereqs)
        completed = True
        cursor.execute(
            "SELECT * FROM Enrollments WHERE student_id = %s AND course_id = %s AND status != 'FINAL';",
            (session.get("user_id"), course_id),
        )
        records = cursor.fetchone()
        print("records:")
        print(records)
        # print(records["status"])
        # print(records["grade"])
        

        if prereqs:
            prereq_dict = prereqs[0]
            prereq1 = prereq_dict["course_prereq1"]
            prereq2 = prereq_dict["course_prereq2"]

            print(prereq1)
            print(prereq2)
            # len = len(prerequisites)
            # print("len")
            # print(len)
            cursor.execute(
                "SELECT * FROM Enrollments WHERE student_id = %s AND course_id = %s;",
                (session.get("user_id"), prereq1),
            )
            p1grade = cursor.fetchone()
            if (
                p1grade is None
                or p1grade["grade"] == "IP"
                or p1grade["status"] != "FINAL"
            ):
                completed = False
                add = False

            if prereq2:
                cursor.execute(
                    "SELECT * FROM Enrollments WHERE student_id = %s AND course_id = %s;",
                    (session.get("user_id"), prereq2),
                )
                p2grade = cursor.fetchone()
                if (
                    p2grade is None
                    or p2grade["grade"] == "IP"
                    or p2grade["status"] != "FINAL"
                ):
                    completed = False
                    add = False

        if completed == True:
            cursor.execute(
                "INSERT INTO Enrollments (student_id, section, course_id, status) VALUES (%s, %s, %s, %s)",
                (
                    session.get("user_id"),
                    crn,
                    course_meeting_times["course"],
                    "REGISTERED",
                ),
            )
            cursor.execute(
                """UPDATE Section SET studentsEnrolled = studentsEnrolled + 1 WHERE crn = %s;""",
                (crn,),
            )
            db.commit()
            # return jsonify(success=True)
        else:
            print("prereq not met")
            flash(
                "You must complete the appropiate Prerequisites to register for this class"
            )
            return redirect(url_for("regdashboard"))
    else:
        print("overlap")
        flash("There is an overlap between classes")
        return redirect(url_for("regdashboard"))
    return redirect(url_for("regdashboard"))


@app.route("/drop/<crn>/<courseID>")
def drop(crn, courseID):
    mycursor = db.cursor(dictionary=True)
    # mycursor.execute("""SELECT sr.student, sr.section FROM studentRecords sr WHERE sr.student = %s AND sr.section = %s AND sr.finalgrade IS NULL""", (session.get('id'), crn))
    # result = mycursor.fetchone()
    # # check if crn trying to drop is in result
    # x = any(crn in sublist for sublist in result)
    mycursor.execute(
        "SELECT * FROM Enrollments where student_id = %s AND status != 'FINAL'", (session.get("user_id"),)
    )
    test = mycursor.fetchall()
    print("before delete")
    print(test)
    # if x == True:
    mycursor.execute(
        """DELETE FROM Enrollments WHERE student_id = %s AND section = %s AND course_id = %s AND status != 'FINAL';""",
        (session.get("user_id"), crn, courseID),
    )
    db.commit()
    mycursor.execute(
        """UPDATE Section SET studentsEnrolled = studentsEnrolled - 1 WHERE crn = %s;""",
        (crn,),
    )
    db.commit()

    mycursor.execute(
        "SELECT * FROM Enrollments where student_id = %s AND status != 'FINAL'", (session.get("user_id"),)
    )
    test = mycursor.fetchall()
    print("after delete")
    print(test)

    db.commit()
    return redirect(url_for("regdashboard"))


@app.route("/studentDetails/<id>", methods=["GET", "POST"])
def studentDetails(id):
    if "user_type" not in session:
        return render_template("errors/403.html")
    # temp = 0
    # if session.get('role') == 'sysAdmin':
    # 	temp = 1
    # if session.get('role') == 'gradSecretary':
    # 	temp = 1
    # if temp == 0:
    # 	return render_template('errors/403.html')
    if "user_type" in session:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT p.first_name, p.last_name, p.advisor_id, sr.student_id, sr.section, sr.semester, sr.grade, sr.status, c.title, c.course_code, c.credit_hours FROM Enrollments AS sr JOIN Section AS sec ON sr.section = sec.crn JOIN Course AS c ON sec.course = c.course_code JOIN Person AS p ON sr.student_id = p.user_id WHERE sr.student_id = %s",
            (id,),
        )
        studentInfo = cursor.fetchall()
        print("student1")
        print(studentInfo)
        point_map = {
				'A' : 4.0,
				'A-' : 3.7,
				'B+' : 3.3,
				'B' : 3.0,
				'B-' : 2.7,
				'C+' : 2.3,
				'C' : 2.0,
				'F' : 0.0
			}
        credit_total = 0
        point_total = 0
        hasGrade = False
        gpa = 0
        for row in studentInfo:
            print(row)
            print(len(row))
            hours = row['credit_hours']
            final_grade = row['grade']
            print(final_grade)
            if final_grade != "IP" or final_grade != "None":
                hasGrade = True
            if final_grade == "IP" or final_grade == "None":
                #gpa = 0
                continue
            elif final_grade not in ["A", "A-", "B+", "B", "B-", "C+", "C", "F"]:
                #gpa = 0
                continue
            
            credit_total += hours

            point_total += point_map[row['grade']] * hours

        
            gpa = point_total / credit_total

            print("GPA:")
            print(gpa)
                
        if len(studentInfo) == 0:
            # return redirect('/sysAdminDashboard')
            cursor.execute(
            "SELECT p.first_name, p.last_name, p.advisor_id FROM Person AS p WHERE p.user_id = %s",
            (id,))
            studentInfo = cursor.fetchall()
            print("student2")
            print(studentInfo)
            return render_template("studentInfo.html", info=studentInfo, id=id)
        else:
            return render_template("studentInfo.html", info=studentInfo, id=id, gpa = gpa)
    # db.connection.commit()
    # return render_template("extensions/studentInfo.html", info = studentInfo, id = id)

    return redirect(url_for("regdashboard"))


@app.route("/changeFinalGrade/<student_id>/<cid>", methods=["POST"])
def changeFinalGrade(student_id, cid):
    if "user_type" not in session:
        return render_template("errors/403.html")
    if (
        session["user_type"] != "ADMIN"
        and session["user_type"] != "GS"
        and session["user_type"] != "FACULTY"
    ):
        return render_template("errors/403.html")
    new_grade = request.form["new_grade"]
    stat = request.form["status"]
    cursor = db.cursor()

    update_query = (
        "UPDATE Enrollments SET grade = %s WHERE student_id = %s AND section = %s"
    )
    cursor.execute(update_query, (new_grade, student_id, cid))
    db.commit()

    update_query = (
        "UPDATE Enrollments SET status = %s WHERE student_id = %s AND section = %s"
    )
    cursor.execute(update_query, (stat, student_id, cid))
    db.commit()

    # Redirect or render a template to inform the user that the grade has been changed
    return redirect(url_for("studentDetails", id=student_id))


@app.route("/adduser", methods=["GET", "POST"])
def adduser():
    if "user_type" not in session:
        return render_template("errors/403.html")
    if session["user_type"] != "ADMIN":
        return render_template("errors/403.html")

    cursor = db.cursor()
    print("in func")

    # get values
    role = request.form["Role"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    username = request.form["username"]
    password = request.form["password"]
    uid = random.randint(10000000, 99999999)
    # check if user_id already exists under someone else
    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE user_id = %s", (uid, ))
    check = cursor.fetchone()
    if check is None:
        uid = random.randint(10000000, 99999999)

    # insert into database
    cursor.execute(
        "INSERT INTO Person (first_name, last_name, user_id) VALUES (%s, %s, %s)",
        (fname, lname, uid),
    )
    db.commit()

    # insert into specefic role
    if role:
        cursor.execute(
            "INSERT INTO User (username, password, user_id, role, cac) VALUES (%s, %s, %s, %s, %s)",
            (username, password, uid, role, request.form["cac"]),
        )
        print("in stu")
        db.commit()

    return redirect(url_for("home"))


@app.route("/submitfeedback", methods=["GET", "POST"])
def submitfeedback():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT course_code FROM Course")
    courses = cursor.fetchall()
    print(courses)
    
    if request.method == 'POST':
        course = request.form["course"]
        feedback = request.form["feedback"]
        if request.form["name"]:
            name = request.form["name"]
        else:
            name = 'anonymous'
        cursor.execute("INSERT INTO courseFeedback (course, feedback, name) VALUES (%s, %s, %s)", (course, feedback, name))
        db.commit()
        flash("Feedback submitted")
        return redirect(url_for("submitfeedback"))

    
    return render_template("feedback.html", courses = courses)


@app.route("/viewFeedback/<course>", methods=["GET", "POST"])
def viewFeedback(course):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courseFeedback WHERE course = %s", (course,))
    feedback = cursor.fetchall()
    return render_template("viewFeedback.html", feedback=feedback)


@app.route("/gsResults", methods=["GET", "POST"])
def gsResults():
    if request.method == 'POST':
        search = request.form['search']
        mycursor = db.cursor(dictionary=True)
        mycursor.execute(
            "SELECT u.user_id, p.first_name, p.last_name FROM User as u JOIN Person AS p ON p.user_id = u.user_id JOIN Application ON Application.user_id = p.user_id WHERE (u.user_id = %s OR p.first_name = %s OR p.last_name = %s OR p.program_id = %s OR Application.appYear = %s)", (search, search, search, search, search))
        students = mycursor.fetchall()
        print(students)
        return render_template("gs-home.html", students=students)
    
@app.route("/gsResultsAlumni", methods=["GET", "POST"])
def gsResultsAlumni():
    if request.method == 'POST':
        search = request.form['search']
        print(search)
        mycursor = db.cursor(dictionary=True)
        mycursor.execute(
            "SELECT CONCAT(p.first_name + ' ' + p.last_name) AS name, p.email FROM Person p JOIN Alumni ON student_id=user_id JOIN Program ON Program.program_id=p.program_id WHERE (Alumni.graduation_date = %s OR Program.program_name = %s)", (search, search))
        alumni = mycursor.fetchall()
        flash(alumni)
        return redirect(url_for('home'))
    
@app.route("/gsResultsAdmitted", methods=["GET", "POST"])
def gsResultsAdmitted():
    if request.method == 'POST':
        search = request.form['search']
        print(search)
        mycursor = db.cursor(dictionary=True)
        mycursor.execute(
            "SELECT CONCAT(p.first_name + ' ' + p.last_name) AS name FROM Person p JOIN User ON p.user_id = User.user_id JOIN Program ON Program.program_id=p.program_id WHERE (Program.program_name = %s AND User.role = 'STUDENT')", (search, ))
        alumni = mycursor.fetchall()
        flash(alumni)
        return redirect(url_for('home'))
    
@app.route("/facultyResults", methods=["GET", "POST"])
def facultyResults():
    if request.method == 'POST':
        search = request.form['search']
        student_id = ""
        student_list = get_student_list()
        mycursor = db.cursor(dictionary=True)
        mycursor.execute(
            "SELECT course, number FROM Section WHERE professor = %s AND (course = %s OR crn = %s OR number = %s)",
            (session.get('user_id'),search, search, search))
        courses = mycursor.fetchall()
        print(courses)
        if request.method == "POST":
            student_id = request.form.get("student_id")
        return render_template(
            "faculty-home.html",
            student_list=student_list,
            student_id=student_id,
            courses=courses,
        )
        

@app.route("/adminResults", methods=["GET", "POST"])
def adminResults():
    if request.method == 'POST':
        search = request.form['search']
        mycursor = db.cursor(dictionary=True)
        mycursor.execute(
            "SELECT u.user_id, p.first_name, p.last_name, FROM User as u JOIN Person AS p ON p.user_id = u.user_id WHERE u.role = 'STUDENT' AND (u.user_id = %s OR p.first_name = %s OR p.last_name = %s)", (search, search, search))
        students = mycursor.fetchall()
        print(students)
        mycursor.execute("SELECT * FROM Section WHERE (course = %s OR crn = %s OR number = %s)", (search, search, search))
        courses = mycursor.fetchall()
        print(courses)
        return render_template(
            "admin-home.html", students=students, courses=courses
        )
        
    
@app.route("/getAdvisees")
def getAdvisees():
    mycursor = db.cursor(dictionary=True)
    mycursor.execute("SELECT first_name, last_name FROM Person WHERE advisor_id IS NOT NULL")
    advisees = mycursor.fetchall()
    strings = []
    for x in advisees:
        strings.append({
            "\n" + x['first_name'] + " " + x['last_name']
        })
    flash(advisees)
    return redirect(url_for('home'))

@app.route("/changeAdvisor", methods=["GET", "POST"])
def changeAdvisor():
    if request.method == 'POST':
        mycursor = db.cursor(dictionary=True)
        advisor = request.form["advisor"]
        student = request.form["student_id"]
        print(student)
        print(advisor)
        mycursor.execute("UPDATE Person SET advisor_id = %s WHERE user_id = %s;", (advisor, student))
        db.commit()
    flash("success")
    return redirect(url_for('home'))


@app.route("/reset")
def reset():
    cursor = db.cursor()
    # Read the SQL statements from the file
    with open("combined/phase-2-schema.sql", "r") as sql_file:
        sql_statements = sql_file.read()

        # Split the SQL statements and execute each one
    for sql in sql_statements.split(";"):
        if sql.strip():
            cursor.execute(sql)

            # Commit the changes and close the connection
    db.commit()
    return redirect("/login")


app.run(debug=True)

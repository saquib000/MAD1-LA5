from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.sqlite3"

db=SQLAlchemy(app)
app.app_context().push()

class Student(db.Model):
    student_id = db.Column(db.Integer , primary_key=True)
    roll_number = db.Column(db.String , unique=True, nullable=False)
    first_name = db.Column(db.String ,  nullable=False)
    last_name = db.Column(db.String ,  nullable=False)

class Course(db.Model):
    course_id = db.Column(db.Integer , primary_key=True)
    course_code = db.Column(db.String , unique=True, nullable=False)
    course_name = db.Column(db.String ,  nullable=False)
    course_description = db.Column(db.String ,  nullable=False)

class Enrollments(db.Model):
    enrollment_id = db.Column(db.Integer , primary_key=True)
    estudent_id = db.Column(db.Integer , db.ForeignKey("student.student_id"))
    ecourse_id = db.Column(db.Integer , db.ForeignKey("course.course_id"))

@app.route("/", methods=["POST","GET"])
def home():
    student = Student.query.all()
    return render_template("home.html",Students=student)

@app.route("/student/create", methods=["GET","POST"])
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    
    if request.method == "POST":
        try :
            #adding student data to db::Student
            roll=request.form.get("roll")
            f_name=request.form.get("f_name")
            l_name=request.form.get("l_name")
            s1=Student(roll_number=roll,first_name=f_name,last_name=l_name)
            db.session.add(s1)
            db.session.commit()

            #adding enrollment data to db::Enrollments
            students=Student.query.all()
            sid=students[-1].student_id
            courses=request.form.getlist("courses")
            print(courses)
            
            for cid in courses:
                e1=Enrollments(estudent_id=sid,ecourse_id=cid)
                db.session.add(e1)
                db.session.commit()

            return redirect("/")
        except IntegrityError:
            db.session.rollback()
            return render_template("roll_error.html")

#@app.route("/student/<int:student_id>")    
@app.route("/student/<student_id>")
def student(student_id):
    #querying Student object
    s1=Student.query.get(student_id)

    #getting Courses objects of student_id
    #Enrollments obejects
    e1=Enrollments.query.filter_by(estudent_id=student_id)
    # print(e1[0].ecourse_id)

    #getting course_id
    cidList=[]
    for enrolls in e1:
        # print(enrolls.ecourse_id)
        cidList.append(enrolls.ecourse_id)    

    #populating the list of Course objects
    clist=[]
    for cids in cidList:
        print(cids)
        c=Course.query.get(cids)
        clist.append(c)

    return render_template("student.html",student=s1,courses=clist)

@app.route("/student/<int:student_id>/delete")
def delete(student_id):
    s1=Student.query.get(student_id)
    db.session.delete(s1)
    
    e1=Enrollments.query.filter_by(estudent_id=student_id)
    for item in e1:
        db.session.delete(item)
    
    db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>/update",methods=["GET","POST"])
def update(student_id):
    s1=Student.query.get(student_id)

    if request.method=="GET":
        return render_template("update_student.html",student=s1)
    
    if request.method=="POST":
        #updating student data to db::Student
        s1.first_name=request.form.get("f_name")
        s1.last_name=request.form.get("l_name")
        
        #updating student courses
        c_list=request.form.getlist("courses")
        if len(c_list) >=1 :
            #deleting old enrollments records
            e1=Enrollments.query.filter_by(estudent_id=student_id)
            for item in e1:
                db.session.delete(item)

            #creating new enrollments
            for c_id in c_list:
                e2=Enrollments(estudent_id=student_id,ecourse_id=c_id)
                db.session.add(e2)

        db.session.commit()
        return redirect("/")




    

if __name__ == '__main__':
	app.debug=True
	app.run(
          port=8000
    )


    









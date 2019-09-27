import flask
from flask import Flask
from flask import *
import hashlib
import mysql.connector
import string
import base64
import datetime  
import random
import time
import re
from werkzeug.utils import secure_filename
import io
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from flask import session
import itertools
import cStringIO
from bs4 import BeautifulSoup
import os
import cv2
# -*- coding: utf-8 -*-
import sys
reload(sys)
import subprocess
import pipes
import socket
import webview
import threading

sys.setdefaultencoding("utf-8")
app=Flask(__name__)
app.config["UPLOAD"]="static/img"
conn = mysql.connector.connect(host="127.0.0.1",user="phpmyadmin",password="root",database="teach-me")
cursor = conn.cursor()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def cookiegenrator():
    return ''.join(random.choice(string.ascii_lowercase +string.digits) for _ in range(16))
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):

    return TAG_RE.sub('', text)
def update_cookie(cookie):
    sql="UPDATE Cookie SET time='{}' WHERE cookie='{}'".format(time.time()+1000,cookie)
    cursor.execute(sql)
    conn.commit()
def check_login(cookie):
    sql="SELECT time FROM Cookie WHERE cookie='{}'".format(cookie)
    cursor.execute(sql)
    result=cursor.fetchall()[0]
    if result < time.time():
        return redirect("/login")

def if_cookie_existe(cookie):
    sql="SELECT cookie FROM Cookie WHERE cookie='{}'".format(cookie)
    cursor.execute(sql)
    result=cursor.fetchall()
    if result:        
        return True
    else:
        return False
def Create_cookie(cookie,user_Id):
    sql="INSERT INTO Cookie(cookie,time,UserId) VALUES('{}','{}','{}')".format(cookie,1,user_Id)
    cursor.execute(sql)
    conn.commit()
def get_user_id(cookie):
    sql="SELECT UserId FROM Cookie WHERE cookie='{}'".format(cookie)
    cursor.execute(sql)
    userid=cursor.fetchall()[0][0]
    return userid
def get_user_name(user_id):
    sql="SELECT Username FROM Users WHERE ID='{}'".format(user_id)
    cursor.execute(sql)
    username=cursor.fetchall()[0][0]
    return username
    

def set_cookie(cookie):
    resp = make_response(redirect("/index"))
    resp.set_cookie('sessionid', cookie)
    return resp 

def get_Role():
    user_cookie=request.cookies.get("sessionid")
    sql="SELECT UserId FROM Cookie WHERE cookie='{}'".format(user_cookie)
    cursor.execute(sql)
    user_id=cursor.fetchall()[0][0]
    sql="SELECT Role FROM Users WHERE ID='{}'".format(user_id)
    cursor.execute(sql)
    role=int(cursor.fetchall()[0][0])
    return role

def login_manager():
    if get_cookie()==None:
        return redirect("/login")
    else:
        if not if_cookie_existe(get_cookie()):
            request.cookies.pop('sessionid', None)
            return redirect("/login")
        else:
            if check_connection(get_cookie()):
                update_cookie(get_cookie())
                
            else:
                return redirect("/login")
    return False

def get_cookie():
    return request.cookies.get("sessionid")


def get_requiremment(id_course):
    sql="SELECT requirement FROM Courses WHERE id='{}'".format(id_course)
    cursor.execute(sql)
    req=cursor.fetchall()
    
    return req[0][0]
def get_difficulty(id_course):
    sql="SELECT difficulty FROM Courses WHERE id='{}'".format(id_course)
    cursor.execute(sql)
    diff=cursor.fetchall()
    return diff[0][0]


def sign_for_course(id_user,id_course,course_name,progress,difficulty,requiremment,img):
    sql="INSERT INTO Lesson_inscrit(id_user,id_course,course_name,progress,difficulty,requiremment,image) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(id_user,id_course,course_name,progress,difficulty,requiremment,img)
    cursor.execute(sql)
    conn.commit()



def get_first_chapitre(id_course):
    sql="SELECT MIN(id) FROM chapitres WHERE Course_id='{}'".format(id_course)
    cursor.execute(sql)
    first_chapitre=cursor.fetchall()
    

    sql="SELECT title FROM Courses WHERE id='{}'".format(id_course)
    cursor.execute(sql)
    result=cursor.fetchall()[0][0]
    sql="SELECT image FROM Courses WHERE id='{}'".format(id_course)
    cursor.execute(sql)
    img=cursor.fetchall()[0][0]

    user_id=get_user_id(get_cookie())
    sign_for_course(user_id,id_course,result.encode('utf-8'),0,get_difficulty(id_course),get_requiremment(id_course).encode('utf-8').encode('utf-8'),img)
    return first_chapitre[0][0]

def get_Current_chapiter(id_course):
    url=request.url.split("/")[8]
    return url
    


def check_connection(cookie):
    current_time=time.time()
    sql="SELECT time FROM Cookie WHERE cookie='{}'".format(cookie)
    cursor.execute(sql)
    result=cursor.fetchall()[0][0]
   
    if current_time > result:
        return False
    else:
        return True

def get_courses_info(id_course):
    sql="SELECT difficulty, requirement, title,id FROM Courses WHERE id='{}'".format(id_course)
    cursor.execute(sql)
    courses_info=cursor.fetchall()
    
    return courses_info
def generate_certification(first_name,last_name):
    img = Image.open("cert.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Roboto-Regular.ttf", 40)
    
    draw.text((500, 450),first_name+" "+last_name,(12,18,130),font=font)
    d = datetime.datetime.today()
    draw.text((150, 615),str(d.day)+"/"+str(d.month)+"/"+str(d.year),(12,18,130),font=font)
    
    img.save('sample-out.jpg')

def backup():
    DB_NAME = 'teach-me'
    BACKUP_PATH ='/home/walid/Desktop/pfe/bak'
    DB_HOST = 'localhost' 
    DB_USER = 'phpmyadmin'
    DB_USER_PASSWORD ='root'
    DATETIME = time.strftime('%Y%m%d-%H%M%S')
    TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME 
    try:
        os.stat(TODAYBACKUPPATH)
    except:
        os.mkdir(TODAYBACKUPPATH)
    db = DB_NAME
    dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
    os.system(gzipcmd)
        
def gen_frames():
    while True:
        
        success, frame = camera.read()  
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Live_Streaming',methods=["GET","POST"])    
def Live_Streaming():
    return render_template("Live_Streaming.html")


@app.route("/Registration",methods=["GET","POST"])
def Registration():
    if request.method=="POST":
        name=request.form["name"]
        surname=request.form["surname"]
        username=request.form["username"]
        email=request.form["email"]
        birth=request.form["birth"]
        password=request.form["password"]
        Sexe = request.form["Sexe"]
        Role= request.form["Role"]
        h=hashlib.sha1()
        h.update(password)
        password = h.hexdigest()
        Registration_date = datetime.date.today()
        if Role == "Student":
            sql="INSERT INTO Users(Name,Surname,Username,Email,Birth_date,Registration_date,Password,Role ,Sexe)VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(name,surname,username,email,birth,Registration_date,password,int(3) ,Sexe)
            cursor.execute(sql)
            conn.commit()
        else:
            sql="INSERT INTO Users(Name,Surname,Username,Email,Birth_date,Registration_date,Password,Role ,Sexe)VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(name,surname,username,email,birth,Registration_date,password,int(2) ,Sexe)
            cursor.execute(sql)
            conn.commit()

    return render_template("Registration.html")


@app.route("/login",methods=["GET","POST"])
def login():
    
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        h=hashlib.sha1()
        h.update(password)
        hashe = h.hexdigest()
        sql="SELECT Password, ID FROM Users WHERE Username='{}'".format(username)
        cursor.execute(sql)
        info_login=cursor.fetchall()
        if info_login:
            if info_login[0][0]==hashe:
                if if_cookie_existe(get_cookie()):
                    update_cookie(get_cookie())
                else:
                    new_cookie=cookiegenrator()
                    Create_cookie(new_cookie,info_login[0][1])
                    update_cookie(new_cookie)

                    return set_cookie(new_cookie)
                return redirect("/index")
            else:
                return redirect("/login")

    return render_template("login.html")






@app.route("/index",methods=["GET","POST"])
def index():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT COUNT(id) FROM Lesson_inscrit WHERE id_user='{}'".format(get_user_id(get_cookie()))
    cursor.execute(sql)
    nb_courses=cursor.fetchall()

    sql="SELECT Mark FROM Lesson_inscrit WHERE id_user='{}'".format(get_user_id(get_cookie()))
    cursor.execute(sql)
    mark=cursor.fetchall()
    if mark:
        s=0
        for i in mark:
            if i[0]!=None:
                s=s+int(i[0])
    else:
        s=0
        mark=0
    sql="SELECT COUNT(id) FROM comment WHERE id_user='{}'".format(get_user_id(get_cookie()))
    cursor.execute(sql)
    cmt=cursor.fetchall()[0][0]
    sql="SELECT COUNT(id) FROM Forum_Question WHERE author='{}'".format(username)
    cursor.execute(sql)
    ques=cursor.fetchall()[0][0]

    sql="SELECT course_name,difficulty,total_progress FROM Lesson_inscrit WHERE id_user='{}'".format(get_user_id(get_cookie()))
    cursor.execute(sql)
    charts=cursor.fetchall()

    
    return render_template("index.html",charts=charts,cmt=cmt,username=username,s=s,ques=ques,nb_courses=nb_courses[0],role=role)


@app.route("/StudentManager",methods=["GET","POST"])
def StudentManager():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT * FROM Users WHERE Role='{}'".format(int(3))
    cursor.execute(sql)
    AllStudents=cursor.fetchall()
    
    return render_template("StudentManager.html", AllStudents=AllStudents,username=username,role=role)


@app.route("/TacherManager",methods=["GET","POST"])
def TeacherManager():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT * FROM Users WHERE Role='{}'".format(int(2))
    cursor.execute(sql)
    AllTeachers=cursor.fetchall()
  

    return render_template("TeacherManager.html",username=username,AllTeachers=AllTeachers,role=role)


@app.route("/Profile",methods=["GET","POST"])
def Profile():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    return render_template("Profile.html",username=username,role=role)


@app.route("/EditProfile",methods=["GET","POST"])
def EditProfile():
    if login_manager():
        return login_manager()
    role=get_Role()
    current_cookie=request.cookies.get("sessionid")
    user_id= get_user_id(current_cookie)
    
    
    if request.method == "POST":
        name=request.form["first_name"]
        surname=request.form["last_name"]
        email=request.form["email"]
        birth=request.form["birth"]
        if request.files:
            imgg= request.files["images"]
            height=250
            width=250
            imgg1=Image.open(imgg)
            im2 = imgg1.resize((width, height),Image.NEAREST)
            ext = ".png"
            im2.save("profile" + ext)
           
            buffer = cStringIO.StringIO()  
            im2.save(buffer, format="png")
            encodedimg=base64.b64encode(buffer.getvalue())
          
            sql="UPDATE Users SET Name='{}' , Surname='{}' , Email='{}' , Birth_date='{}' photo='{}'  WHERE ID='{}'".format(name,surname,email,birth,encodedimg,user_id)
            cursor.execute(sql)
            conn.commit()
        else:
         
            sql="UPDATE Users SET Name='{}' , Surname='{}' , Email='{}' , Birth_date='{}'   WHERE ID='{}'".format(name,surname,email,birth,user_id)
            cursor.execute(sql)
            conn.commit()
    sql="SELECT Name, Surname, Email, Username, Birth_date, photo FROM Users WHERE ID='{}'".format(get_user_id(current_cookie))
    cursor.execute(sql)
    user_information=cursor.fetchall()  
    
    return render_template("EditProfile.html",user_information=user_information,role=role)

@app.route("/MyCourses",methods=["GET","POST"])
def MyCourses():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT id_course,course_name,progress,difficulty,requiremment,total_progress,image FROM Lesson_inscrit WHERE id_user='{}'".format(get_user_id(request.cookies.get('sessionid')))
    cursor.execute(sql)
    signed_up_courses=cursor.fetchall()
    signed_up_courses2=list()
    for i in signed_up_courses:
        x=list(i)
        x[0]=str(x[0])
        x[1]=str(x[1])
        x[2]=str(x[2])
        signed_up_courses2.append(x)
    
   
   
    return render_template("MyCourses.html",signed_up_courses=signed_up_courses2,username=username,role=role)


@app.route("/logout", methods = ["GET","POST","DELETE"])
def logout():
    current_user_cookie=request.cookies.get("sessionid")
    sql="UPDATE Cookie SET time='{}' WHERE cookie='{}' ".format(1,current_user_cookie)
    cursor.execute(sql)
    conn.commit()
    resp = make_response(redirect("/login"))
    resp.set_cookie('sessionid', '', expires=0)
    return resp
    return redirect("/login")


@app.route("/indexc", methods = ["GET","POST"])
def indexc():
    if get_cookie()== None:

        login_button=1
        sql="SELECT id,title,requirement,image,introduction FROM Courses"
        cursor.execute(sql)
        all_courses=cursor.fetchall()
        Courses_list=list()
        for i in all_courses:
            x=list(i)
            x[0]=str(x[0])
            Courses_list.append(x)
         
        return render_template("indexc.html",all_courses=Courses_list,login_button=login_button)
    else:
        login_button=0
        role=get_Role()
        username=get_user_name(get_user_id(request.cookies.get('sessionid')))
        sql="SELECT id,title,requirement,image,introduction FROM Courses"
        cursor.execute(sql)
        all_courses=cursor.fetchall()
        Courses_list=list()
        for i in all_courses:
            x=list(i)
            x[0]=str(x[0])
            Courses_list.append(x)

        sql="SELECT * FROM Events"
        cursor.execute(sql)
        events=cursor.fetchall()
    
        return render_template("indexc.html",events=events,all_courses=Courses_list,username=username,role=role,login_button=login_button)

@app.route("/courses", methods = ["GET","POST"])
def courses():
    if get_cookie()== None:
        login_button=1
        role=5
        username=""
        sql="SELECT * FROM Courses"
        cursor.execute(sql)
        not_signed_course=cursor.fetchall()
        not_signed=list()
        for i in not_signed_course:
            x=list(i)
            x[0]=str(x[0])
            not_signed.append(x)
           
    else:
        login_button=0
        role=get_Role()
        username=get_user_name(get_user_id(request.cookies.get('sessionid')))
        sql="SELECT * FROM Courses WHERE id NOT IN (SELECT id_course FROM Lesson_inscrit WHERE id_user='{}')".format(get_user_id(get_cookie()))
        cursor.execute(sql)
        not_signed_course=cursor.fetchall()
        not_signed=list()
        for i in not_signed_course:
            x=list(i)
            x[0]=str(x[0])
            not_signed.append(x)
        


    return render_template("courses.html",Courses=not_signed,login_button=login_button,username=username,role=role)
        
@app.route("/teacher", methods = ["GET","POST"])
def teacher():
    return render_template("teacher.html")

@app.route("/about", methods = ["GET","POST"])
def about():
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role=get_Role()
    return render_template("about.html",login_button=login_button,role=role)

@app.route("/forum_manager",methods=["GET","POST"])
def forum_manager():
    if login_manager():
        return login_manager()
        
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT id,author,subject FROM Forum_Question"
    cursor.execute(sql)
    forum=cursor.fetchall()
    forum_list=list()
    for i in forum:
        x=list(i)
        x[0]=str(x[0])
        forum_list.append(x)
   

    return render_template("forum_manager.html",forum=forum_list,role=role,username=username)

@app.route("/contact", methods = ["GET","POST"])
def contact():
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role = get_Role()
    return render_template("contact.html",login_button=login_button,role=role)

@app.route("/forum", methods = ["GET","POST"])
def forum():
    if login_manager():
        return login_manager()
        
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    
    if request.method =="POST":
        subject=request.form["subject"]
        content=request.form["content"]
       
        sql="INSERT INTO Forum_Question (author,subject,content) VALUES('{}','{}','{}')".format("walid",subject,content)
        cursor.execute(sql)
        conn.commit()
    return render_template("forum.html",login_button=0,username=username,role=role)

@app.route("/forum_question", methods = ["GET","POST"])
def forum_question():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT subject, content, id FROM Forum_Question"
    cursor.execute(sql)
    all_question=cursor.fetchall()
    x=list()
    for i in all_question:
        x.append(map(str,i))
    
    return render_template("forum_question.html",all_question=x,username=username,role=role)

@app.route("/forum_question/forum_viewd_question/<string:id>", methods = ["GET","POST"])
def forum_viewd_question(id):
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT subject, content FROM Forum_Question WHERE id='{}'".format(id)
    cursor.execute(sql)
    result=cursor.fetchall()
   
    if request.method=="POST":
        content = request.form["addComment"]
        sql="SELECT photo FROM Users WHERE ID='{}'".format(get_user_id(request.cookies.get('sessionid')))
        cursor.execute(sql)
        img=cursor.fetchall()[0][0]
        
        sql="INSERT INTO comment(id_post, id_user,content,time,username,pic) VALUES('{}','{}','{}','{}','{}','{}')".format(id,get_user_id(request.cookies.get('sessionid')),content,datetime.datetime.now(),username,img)
        cursor.execute(sql)
        conn.commit()
    sql="SELECT * FROM comment WHERE id_post='{}'".format(id)
    cursor.execute(sql)
    result1=cursor.fetchall()
 
    
    return render_template("forum_viewd_question.html",result=result,result1=result1,username=username,role=role)


@app.route("/all_comments", methods = ["GET","POST"])
def all_comments():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))

    sql="SELECT id,content,username FROM comment"
    cursor.execute(sql)
    all_comments=cursor.fetchall()

    return render_template("all_comments.html",all_comments=all_comments,role=role,username=username)

@app.route("/all_comments/<int:id>/delete_cmt", methods = ["GET","POST"])
def delete_cmt():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    


    return render_template("delete_cmt.html",role=role, username=username)


@app.route("/forum_question/forum_viewd_question/comment/<string:id>", methods = ["GET","POST"])
def comment(id):
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    if request.method=="POST":
        content=request.form["comment"]
        sql="INSERT INTO comment(id_post, id_user,content,time) VALUES('{}','{}','{}','{}')".format(id,2,content,datetime.datetime.now())
        cursor.execute(sql)
        conn.commit()
        content = request.form["addComment"]
        
    
    return render_template("comment.html",username=username,role=role)


@app.route("/Create_page", methods = ["GET","POST"])
def Create_page():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    return render_template("Create_page.html",username=username,role=role)

@app.route("/Create_course", methods = ["GET","POST"])
def Create_course():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    if request.method=="POST":
        title=request.form["title"]
        intro=request.form["intro"]
        requirement=request.form["Requiremment"]
        difficulty=request.form["Difficulty"]
        
        title=title.encode('utf-8')
        intro=intro.encode('utf-8')
        requirement=requirement.encode('utf-8')
        if request.files:
            imgg= request.files["image"]
            height=250
            width=250
            imgg1=Image.open(imgg)
            im2 = imgg1.resize((width, height),Image.NEAREST)
            ext = ".png"
            im2.save("published_course" + ext)
           
            buffer = cStringIO.StringIO()  
            im2.save(buffer, format="png")
            encodedimg=base64.b64encode(buffer.getvalue())
            sql="INSERT INTO Courses(title,introduction,requirement,difficulty,image) VALUES('{}','{}','{}','{}','{}')".format(title,intro,requirement,difficulty,encodedimg)
            cursor.execute(sql)
            conn.commit()
        else:
            sql="INSERT INTO Courses(title,introduction,requirement,difficulty) VALUES('{}','{}','{}','{}')".format(title,intro,requirement,difficulty)
            cursor.execute(sql)
            conn.commit()
    return render_template("Create_course.html",username=username,role=role)

@app.route("/editor", methods = ["GET","POST"])
def editor():
    if login_manager():
        return login_manager()
    role=get_Role()
    if request.method=="POST":
        title=request.form["title"]
        content=request.form["content"]
        username=get_user_name(get_user_id(request.cookies.get('sessionid')))
        sql="INSERT INTO Forum_Question (author,subject,content) VALUES ('{}','{}','{}')".format(username,title,content)
        cursor.execute(sql)
        conn.commit()



    return render_template("editor.html",role=role)

@app.route("/Chapitre", methods=["GET","POST"])
def Chapitre():
    
    return render_template("Chapitre.html")


@app.route("/header",methods=["GET" , "POST"])
def header():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
   
    
    return render_template("header.html",username=username,role=role)


@app.route("/Courses_manager",methods=["GET" , "POST"])
def Courses_manager():
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT id, title , introduction, image FROM Courses "
    cursor.execute(sql)
    result=cursor.fetchall()
    courses=list()
    for i in result:
        x=list(i)
        x[0]=str(x[0])
        courses.append(x)

    if result:

        return render_template("Courses_manager.html",all_courses=courses,username=username,role=role)
    else:
        return render_template("Courses_manager.html",username=username,role=role)


@app.route("/Courses_manager/edit_course/<string:id>",methods=["GET" , "POST"])
def edit_course(id):
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    
    if request.method=="POST":
        title=request.form["title"]
        intro=request.form["intro"]
        req=request.form["Requiremment"]
        sql="UPDATE Courses SET title='{}' , introduction='{}', requirement='{}' WHERE id='{}'".format(title,intro,req,id)
        cursor.execute(sql)
        conn.commit()

    sql="SELECT title, introduction, requirement, difficulty,id,image FROM Courses WHERE id='{}'".format(id)
    cursor.execute(sql)
    course_info=cursor.fetchall()

    sql="SELECT title, content, id FROM chapitres WHERE Course_id='{}'".format(id)
    cursor.execute(sql)
    course_chapiters=cursor.fetchall()
    course_chapiters_liste=list()
    cpt=0
    for i in course_chapiters:
        cpt=cpt+1
        course_chapiters_liste2=list(i)
        course_chapiters_liste2.append("v-pills-tab"+str(cpt))
        course_chapiters_liste2.append(str(cpt))
        course_chapiters_liste.append(course_chapiters_liste2)



    return render_template("edit_course.html",course_info=course_info,course_chapiters_liste=course_chapiters_liste,id=id,username=username,role=role)


@app.route("/Courses_manager/edit_course/<string:id>/Add_chapitre",methods=["GET" , "POST"])
def Add_chapitre(id):
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))

    if request.method=="POST":
        title=request.form["title"].decode().encode('utf-8')
        content=request.form["content"].encode('ascii','ignore')
        content=content.decode().encode('utf-8')
        sql="INSERT INTO chapitres(title,content,Course_id) VALUES('{}','{}','{}')".format(title,content,id)
        cursor.execute(sql)
        conn.commit()

    return render_template("Add_chapitre.html",username=username,role=role)

@app.route("/Courses_manager/edit_course/<string:id>/Edit_chapitre/<string:id_chap>", methods=["GET","POST"])
def Edit_chapitre(id,id_chap):
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    
    sql="SELECT title, content, id FROM chapitres WHERE Course_id='{}'".format(id)
    cursor.execute(sql)
    chapitre_content=cursor.fetchall()
    return render_template("Edit_chapitre.html",chapitre_content=chapitre_content,username=username,role=role)




@app.route("/courses/Current_course/id/<string:id>", methods=["GET","POST"])
def Current_course(id):
    if login_manager():
        return login_manager()
    role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))

    sql="SELECT title, introduction, requirement FROM Courses WHERE id='{}'".format(id)
    cursor.execute(sql)
    Courses_info=cursor.fetchall()
    sql="SELECT title, content FROM chapitres WHERE Course_id ='{}'".format(id)
    cursor.execute(sql)
    Courses_chapitres=cursor.fetchall()
    page="/courses/Current_course/id/"+id+"/chapiter/"+str(get_first_chapitre(id))
  
    
           
   
    return render_template("Current_course.html",result=Courses_info,Courses_chapitres=Courses_chapitres,page=page,username=username,role=role,login_button=0)


@app.route("/courses/Current_course/id/<string:id>/chapiter/<string:id_chap>", methods=["GET","POST"])
def Current_chapiter(id,id_chap):
    if login_manager():
        return login_manager()
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role=get_Role()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))


    sql="SELECT title, content FROM chapitres WHERE Course_id ='{}' AND id='{}' ".format(id,id_chap)
    cursor.execute(sql)
    current_chapiter=cursor.fetchall()

    sql="SELECT * FROM chapitres WHERE Course_id='{}'".format(id)
    cursor.execute(sql)
    all_chapitres=cursor.fetchall()
    len_course=len(all_chapitres)
    
    

    sql="SELECT MAX(id) FROM chapitres WHERE course_id='{}'".format(id)
    cursor.execute(sql)
    last_chapitre=cursor.fetchall()[0]
    Current_chapiter_id= int(request.url.split('/')[8])
    #progress
    my_list=list()
    for i in all_chapitres:
        my_list.append(i[0])

    x=my_list.index(int(Current_chapiter_id))
   
    current_progress=((int(x)+1)*100)/len(my_list) 
    sql="UPDATE Lesson_inscrit SET total_progress='{}' WHERE id_course='{}'".format(current_progress,id)
    cursor.execute(sql)
    conn.commit()
    #progress
    
    #next_button_url
    next_chap_url=request.url.split('/')
    if int(next_chap_url[8])+1 <= int(last_chapitre[0]):
        next_chap=int(next_chap_url[8])+1
        next_chap_url[8]=str(next_chap)
    #nex_button_url
    
    if request.method=="GET":
        sql="UPDATE Lesson_inscrit SET progress='{}' WHERE id_user='{}' AND id_course='{}'".format(Current_chapiter_id,get_user_id(request.cookies.get('sessionid')),id)
        cursor.execute(sql)
        conn.commit()
    
  
    return render_template("Current_chapiter.html",current_chapiter=current_chapiter,login_button=login_button,id=id,all_chapitres=all_chapitres,Current_chapiter_id=Current_chapiter_id,len_course=int(last_chapitre[0]),next_chap_url=next_chap_url,username=username,role=role)


@app.route("/Courses_manager/edit_course/<string:id>/Add_quizz",methods=["GET" , "POST"])
def Add_quizz(id):
    if login_manager():
        return login_manager()
    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    if request.method=="POST":
        title=request.form["title"].encode("utf-8")
        quiz=request.form["all_quizz"].encode("utf-8")
        user_id=get_user_id(request.cookies.get('sessionid'))
        id_course=request.url.split('/')[5]
        good_answers=request.form["correct"].encode("utf-8")
        sql="INSERT INTO quizz(name,content,id_course,id_user,correct_answer) VALUES('{}','{}','{}','{}','{}')".format(title,quiz,id_course,user_id,good_answers)
        cursor.execute(sql)
        conn.commit()
       
    return render_template("Add_quizz.html",username=username)


@app.route("/courses/Current_course/id/<string:id>/quizz", methods=["GET","POST"])
def quizz(id):
    if login_manager():
        return login_manager()
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role=get_Role()
    sql="SELECT * FROM quizz WHERE id_course='{}'".format(id)
    cursor.execute(sql)
    result=cursor.fetchall()
    if result:
        correct_answers=list()
        form_name=list()
        for i in result:
            correct_answers.append(i[5].split(',')[:-1])
            soup = BeautifulSoup(i[2],"html.parser")
            names=soup.find_all(name=True)
            for i in names:
                if i.get('name') != None:
                    form_name.append(i.get('name'))
            
        if request.method=="POST":
            chosen_answers=list()
            
            for i in form_name:
                x=request.form[i]
                chosen_answers.append(x)

            result_list=list()
            result_list=zip(correct_answers,chosen_answers)
           
            
            total=len(result_list)
            for i in result_list:
                if i[0][0] != i[1]:
                    total=total-1
            if total>=len(result_list):
                user_id=get_user_id(request.cookies.get('sessionid'))
                sql="UPDATE Lesson_inscrit SET Mark='{}' WHERE id_course='{}' AND id_user='{}'".format(total,id,user_id)
                cursor.execute(sql)
                conn.commit()
                return redirect("/courses/Current_course/id/"+id+"/Felicitation")
            

        return render_template("Quizz.html",quizes=result,login_button=login_button)
    else:
        return render_template("Quizz.html",login_button=login_button)


@app.route("/courses/Current_course/id/<string:id>/Felicitation", methods=["GET","POST"])
def Felicitation(id):
    if login_manager():
        return login_manager()
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role=get_Role()
    user_id=get_user_id(request.cookies.get("sessionid"))
    sql="SELECT Mark FROM Lesson_inscrit WHERE id_course='{}' AND id_user='{}'".format(id,user_id)
    cursor.execute(sql)
    mark=cursor.fetchall()

    sql="SELECT COUNT(id) FROM quizz WHERE id_course='{}' ".format(id)
    cursor.execute(sql)
    all_mark=cursor.fetchall()

    username=get_user_name(get_user_id(request.cookies.get('sessionid')))
    sql="SELECT id_course,course_name,progress,difficulty,requiremment,total_progress,image FROM Lesson_inscrit WHERE id_user='{}' AND id_course='{}'".format(get_user_id(request.cookies.get('sessionid')),id)
    cursor.execute(sql)
    signed_up_courses=cursor.fetchall()
    signed_up_courses2=list()
    for i in signed_up_courses:
        x=list(i)
        x[0]=str(x[0])
        x[1]=str(x[1])
        x[2]=str(x[2])
        signed_up_courses2.append(x)

    sql="SELECT Name,Surname FROM Users WHERE id='{}'".format(get_user_id(get_cookie()))
    cursor.execute(sql)
    info=cursor.fetchall()
   
    generate_certification(info[0][0],info[0][1])
    if request.method=="POST":
        os.system("gm convert sample-out.jpg cert.pdf")
        f=open("cert.pdf","r")
        return send_file(f, attachment_filename="cert.pdf")



        
    return render_template("Felicitation.html",mark=mark,all_mark=all_mark,signed_up_courses=signed_up_courses2)

@app.route("/Add_Events", methods=["GET","POST"])
def Add_Events():
    if login_manager():
        return login_manager()
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role=get_Role()
        username=get_user_name(get_user_id(request.cookies.get("sessionid")))
    if request.method=="POST":
        title=request.form["title"].decode().encode('utf-8')
        content=request.form["content"].encode('ascii','ignore')
        content=content.decode().encode('utf-8')
        sql="INSERT INTO Events(name,content,id_user) VALUES('{}','{}','{}')".format(title,content,get_user_id(request.cookies.get("sessionid")))
        cursor.execute(sql)
        conn.commit()    
    return render_template("Add_Events.html",username=username,role=role,ipadd=socket.gethostbyname(socket.gethostname()))
@app.route("/Event/<int:id>", methods=["GET","POST"])
def Event(id):
    if login_manager():
        return login_manager()
    if get_cookie()== None:
        login_button=1
        role=5
    else:
        login_button=0
        role=get_Role()
        username=get_user_name(get_user_id(request.cookies.get("sessionid")))

    sql="SELECT * FROM Events WHERE id='{}'".format(id)
    cursor.execute(sql)
    event_info=cursor.fetchall()

    return render_template("Event.html",event_info=event_info,login_button=login_button,username=username)

        
    
    return render_template('Stream.html',login_button=login_button)

if __name__ == '__main__':
    backup()
    
    t = threading.Thread(target=app.run(host="0.0.0.0",port=5000,debug=True,use_reloader=True))
    t.daemon = True
    t.start()
    print "ok1"
    webview.create_window(title="teach-me", url='http://0.0.0.0:5000/login', width=800, height=600, resizable=True,\
                      fullscreen=False, min_size=(200, 100), confirm_close=False, text_select=False)

    webview.start()
    print "ok2"
    sys.exit()
    
    
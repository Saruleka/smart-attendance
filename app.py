from flask import Flask,render_template,request,redirect,flash
import sqlite3
from datetime import datetime
import os

def get_db():
    conn=sqlite3.connect("student.db")
    conn.row_factory=sqlite3.Row
    return conn

if not os.path.exists("student.db"):
    import db

app=Flask(__name__)
app.secret_key="saruleka"

@app.route("/")
def login():
    
    return render_template("login.html")

@app.route("/home",methods=["POST"])
def home():
    if request.method=="POST":
        name=request.form["username"]
        password=request.form["Password"]
        if not name:
            flash("Name is required!","error")
            return redirect("/")
        
        elif name == "admin" and password=="12345":
            return render_template("home.html")
        
        else:
            flash("Invalid Login","error")
            return redirect("/")

@app.route("/add_student",methods=["POST","GET"])
def add_student():
    if request.method=="POST":
        cls = request.form["class"]
        names_raw = request.form["names"]
        
        names = [name.strip() for name in names_raw.splitlines() if name.strip()]
        if not names:
            flash("No valid student names entered", "error")
            return redirect("/add_student")

        conn = get_db()
        for name in names:
            last_reg = conn.execute("SELECT MAX(reg) FROM student where class = ?",(cls,)).fetchone()[0]
            if last_reg:
                reg=last_reg+1
            else:
                reg=1000*int(cls)
            
            conn.execute("INSERT INTO student (reg, name, class) VALUES (?, ?, ?)", (reg, name, cls))
        conn.commit()

        flash(f"Students added to Class {cls}", "success")
        return redirect("/add_student")



    return render_template("add.html")

import datetime

@app.route("/mark",methods=["POST","GET"])
def mark_attendance():
    if request.method=="POST":
        cls=request.form["class"] 
        date=datetime.today()

        conn=get_db()
        count=conn.execute("Select count(*) from student").fetchone()[0]
        data=conn.execute(""" Select name , reg from student where class = ? order by name asc""",(cls,)).fetchall()
    
        if data:
            return render_template("home.html",data=data,cls=cls,date=date)
        
        else:
    
            flash("No Records Found","error")
            return render_template("home.html")
    return render_template("home.html")

@app.route("/status",methods=["POST"])
def status_update():
    if request.method == "POST":
        cls = request.form["st_class"]
        date = request.form["date"]
        reg_list = request.form.getlist("st_id[]")
        status_list = request.form.getlist("status[]")

        conn = get_db()
        cursor = conn.cursor()

        for reg, status in zip(reg_list, status_list):
            cursor.execute("""
                SELECT * FROM attendance WHERE reg = ? AND class = ? AND date = ?
            """, (reg, cls, date))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE attendance SET status = ? WHERE reg = ? AND class = ? AND date = ?
                """, (status, reg, cls, date))
            else:
                cursor.execute("""
                    INSERT INTO attendance (reg, class, date, status)
                    VALUES (?, ?, ?, ?)
                """, (reg, cls, date, status))

        conn.commit()

        flash("Submitted Attendance", "success")
        return render_template("home.html")


@app.route("/view",methods=["POST","GET"])
def view_attendance():
    if request.method=="POST":
        cls=request.form["class"]
        
        date=request.form["date"]
              
        conn=get_db()
        count=conn.execute("Select count(*) from student where class = ?",(cls,)).fetchone()[0] 
        data=conn.execute(""" Select s.name , a.status from student s join attendance a on a.reg = s.reg where a.date=? and a.class = ?""",(date,cls)).fetchall()
        
        if data:

            present = sum(1 for row in data if row[1] == 'present')
            absent = sum(1 for row in data if row[1] == 'absent') 
            absent_names=[row[0] for row in data if row[1] =='absent']
        
            return render_template("view.html", data=data, present=present, absent=absent,count=count,names=absent_names) 
        
        else:
            flash("No Data Found","error")
            return render_template("view.html", data=None , count=count) 
    return render_template("view.html")

from datetime import datetime, timedelta

@app.route("/report")
def report():
    conn = get_db()
    cursor = conn.cursor()

    today = datetime.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT class, COUNT(*) FROM attendance WHERE date = ? AND status = 'present' GROUP BY class", (today,))
    daily_rows = cursor.fetchall()
    daily_data = {
        "labels": [row[0] for row in daily_rows],
        "data": [row[1] for row in daily_rows]
    }

    labels = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(4, -1, -1)]
    cursor.execute("SELECT DISTINCT class FROM attendance")
    class_list = [row[0] for row in cursor.fetchall()]

    weekly_data = {
        "labels": labels,
        "datasets": []
    }

    for cls in class_list:
        attendance_counts = []
        for date in labels:
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE class = ? AND date = ? AND status = 'present'", (cls, date))
            count = cursor.fetchone()[0]
            attendance_counts.append(count)

        weekly_data["datasets"].append({
            "label": f"Class {cls}",
            "data": attendance_counts,
            "fill": False,
            "borderColor": f"rgba({int(cls)*40 % 255}, {int(cls)*80 % 255}, 200, 1)",
            "backgroundColor": f"rgba({int(cls)*40 % 255}, {int(cls)*80 % 255}, 200, 0.2)"
        })

    return render_template("search.html", daily_data=daily_data, weekly_data=weekly_data)


if __name__ =="__main__":
    app.run(debug=True)


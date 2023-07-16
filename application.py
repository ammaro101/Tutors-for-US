import sqlite3
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
import requests
import flask
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage




# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///teacher.db")


@app.route("/")
def index():
    """Show selecting options"""
    # return main page
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Show teacher registering menu"""
    expereince = ["one year or less", "2 years", "3 years", "4 years", "5 years or more"]
    subject = ["English or Language Arts", "Mathematics", "Science", "Social Studies", "Foreign Languages", "Other"]
    # if user method is get
    if request.method == "GET":
        return render_template("register.html", exp=expereince, sub= subject)
    # if the user method is post
    else:
        # get the user input
        name = request.form.get("name")
        sub = request.form.get("subject")
        exp = request.form.get("experience")
        phone = request.form.get("phone")
         # if the user didn't provide the required information
        if not name or not sub or not exp or not phone:
            error = "ERROR! YOU DIDN'T PROVIDE ALL THE REQUIRED INFORMATION"
            return render_template("error.html", error=error)
        # check if the phone field is numbers
        if phone.isdigit() == False:
            error = "ERROR! YOU NEED TO ENTER ONLY NUMBERS IN THE PHONE FIELD."
            return render_template("error.html", error=error)
        # make sure that there is no more than the maximum phone number
        if len(phone) > 15:
            error = "ERROR! NO PHONE NUMBER HAS MORE THAN 15 DIGITS."
            return render_template("error.html", error=error)
        phone = int(phone)
        # get the user's location
        x = request.form.get("latitude")
        y = request.form.get("longitude")
        # get 5K meter in latitude and longitude
        xx = float(10 * (360/40075) )
        yy = float(10 * (360/23903.297))
        # it's possible that the user won't provide his location
        if not x or not y:
            # insert in the database
            sql = "INSERT INTO teachers (name, sub, exp, phone) VALUES (?, ?, ?, ?)"
            db.execute(sql, name, sub, exp, phone)
            # inform the user for the success of the proccess
            return render_template("success.html")
        
        # calcolate the 5K to the north, south, east and west oft he user's location
        x = float(x)
        y = float(y)
        east = x+xx
        west = x-xx
        north = y+yy
        south = y-yy
        # insert in the database
        sql = "INSERT INTO teachers (name, sub, exp, phone, north, south, east, west) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        db.execute(sql, name, sub, exp, phone, north, south, east, west)
        # inform the user for the success of the proccess
        return render_template("success.html")
       
        


@app.route("/student", methods=["GET", "POST"])
def student():
    """ Show data """
    if request.method == "POST":
        # get the user location
        sx = request.form.get("latitude")
        sy = request.form.get("longitude")
        # if the user didn't provide his location
        if not sx or not sy:
            error = "ERROR! WE CAN'T ACCESS YOUR LOCATION"
            return render_template("error.html", error=error)
           
        sx = float(sx)
        sy = float(sy)
        # if teacher location < user location < teacher locaton+10
        # or if teacher location > user location > teacher locaton+10
        teachers = """SELECT name, sub, exp, phone FROM teachers
        WHERE north > %s AND south < %s AND east > %s AND west < %s"""
        cards = db.execute(teachers, sy, sy, sx, sx)
        # render the results page
        return render_template("xy.html", x=cards)
        # if there is no teacher in a 5K range from the user
        if len(cards) == 0:
            error = "ERROR! THERE IS NO TEACHERS NEARBY"
            return render_template("error.html", error=error)
            
    # if the method is get
    else:
        teachers = """SELECT name, sub, exp, phone FROM teachers"""
        cards = db.execute(teachers)
        # render a page to show all teachers
        return render_template("student.html", x=cards)


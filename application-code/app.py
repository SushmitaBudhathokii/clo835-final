from flask import Flask, render_template, request
from pymysql import connections
import os
import argparse
import boto3
import logging

app = Flask(__name__)

# DB Config from environment (Secrets in K8s)
DBHOST = os.environ.get("DBHOST", "mysql-db")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "mypassword123")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

# Group info from ConfigMap
GROUP_NAME = os.environ.get("GROUP_NAME", "SUWAYS")
GROUP_SLOGAN = os.environ.get("GROUP_SLOGAN", "EAT.SLEEP.REPEAT")

# Background image info from ConfigMap
background_url=os.environ.get("background_url")
BG_BUCKET = os.environ.get("BG_BUCKET")
BG_KEY = os.environ.get("BG_KEY")  # e.g., "background.jpg"

# AWS credentials from Secrets
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Static file path
BG_LOCAL_PATH = os.path.join("application-code","static", "background.jpg")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Download background image from private S3
def download_background():
    if not background_url:
        app.logger.warning("Background image S3 details are not set.")
        return
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        s3_client.download_file(BG_BUCKET, BG_KEY, BG_LOCAL_PATH)
        app.logger.info(f"Background image downloaded from s3://{BG_BUCKET}/{BG_KEY}")
    except Exception as e:
        app.logger.error(f"Failed to download background image: {e}")

# # MySQL Connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE,
    charset='utf8mb4'
)

# MySQL Connection - Make it optional for local testing
# db_conn = None
# try:
#     db_conn = connections.Connection(
#         host=DBHOST,
#         port=DBPORT,
#         user=DBUSER,
#         password=DBPWD,
#         db=DATABASE
#     )
#     app.logger.info("Successfully connected to MySQL database")
# except Exception as e:
#     app.logger.warning(f"Could not connect to MySQL database: {e}")
#     app.logger.warning("Running in local test mode without database")

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', group_name=GROUP_NAME, group_slogan=GROUP_SLOGAN, background_url="/static/background.jpg")

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', group_name=GROUP_NAME, group_slogan=GROUP_SLOGAN)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    return render_template('addempoutput.html', name=emp_name, group_name=GROUP_NAME, group_slogan=GROUP_SLOGAN)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", group_name=GROUP_NAME, group_slogan=GROUP_SLOGAN)

@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if result:
            output["emp_id"], output["first_name"], output["last_name"], output["primary_skills"], output["location"] = result
        else:
            return f"No employee found with ID {emp_id}"
    except Exception as e:
        app.logger.error(e)
    finally:
        cursor.close()

    return render_template(
        "getempoutput.html",
        id=output["emp_id"],
        fname=output["first_name"],
        lname=output["last_name"],
        interest=output["primary_skills"],
        location=output["location"],
        group_name=GROUP_NAME,
        group_slogan=GROUP_SLOGAN
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=False, type=int, default=81)
    args = parser.parse_args()

    download_background()
    app.run(host='0.0.0.0', port=args.port, debug=True)
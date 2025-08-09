CREATE DATABASE IF NOT EXISTS employees;
USE employees;

CREATE TABLE IF NOT EXISTS employee(
emp_id VARCHAR(20),
first_name VARCHAR(20),
last_name VARCHAR(20),
primary_skill VARCHAR(20),
location VARCHAR(20));

INSERT INTO employee VALUES ('1','Emily','Green','Student','North York');
INSERT INTO employee VALUES ('2','Roy','Smith','Empathy','Nepal');
INSERT INTO employee VALUES ('3','Sam','Gomez','Doc','KTM');
INSERT INTO employee VALUES ('4','George','Smith','Developer','canada');
SELECT * FROM employee;


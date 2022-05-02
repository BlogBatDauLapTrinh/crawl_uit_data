import sqlite3
import os
DATABASE_PATH="database/database_uit.db"

class SQliteHelper():
    def __init__(self,is_new_database=True, database_name=DATABASE_PATH):
        if is_new_database: self.recreate_db()
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()
        if is_new_database: self.create_all_tables()

    def recreate_db(self):
        os.system(f'rm {DATABASE_PATH}')
        os.system(f'touch {DATABASE_PATH}')

    def create_all_tables(self):
        table = """ CREATE TABLE "course_table" (
            "id"	INTEGER PRIMARY KEY,
            "code" 	TEXT,
            "name"	TEXT,
            "school_year"	TEXT,
            "semester"	INTEGER
        ); """
        self.cursor.execute(table)
        table = """ CREATE TABLE "student_table" (
            "id"	INTEGER PRIMARY KEY,
            "code" 	TEXT,
            "name"	TEXT,
            "class" TEXT,
            "email"	TEXT,
            "image"	TEXT,
            "first_access"	TEXT,
            "last_access"	TEXT
        );"""
        self.cursor.execute(table)
        table = """ CREATE TABLE "instructor_table" (
            "id"	INTEGER PRIMARY KEY,
            "name"	TEXT,
            "email"	TEXT,
            "image"	TEXT,
            "first_access"	TEXT,
            "last_access"	TEXT
        );"""
        self.cursor.execute(table)
        table = """ CREATE TABLE "enroll_table" (
            "user_id"	TEXT,
            "course_id"	TEXT
        );"""
        self.cursor.execute(table)
        
    def insert_into_course_table(self, course_id, course_code, course_name, year_school, semester):
        self.cursor.execute('insert into course_table values (?,?,?,?,?)', (
            course_id, course_code, course_name, year_school, semester))
        self.connection.commit()

    def insert_into_student_table(self, student_id, student_code, student_name, class_name, student_email, sudent_image_url, first_access, last_access):
        self.cursor.execute('insert into student_table values (?,?,?,?,?,?,?,?)', (student_id, student_code, student_name, class_name, student_email, sudent_image_url, first_access, last_access))
        self.connection.commit()

    def insert_into_instructor_table(self, instructor_id, instructor_name, instructor_email, instructor_image_url, first_access, last_access):
        self.cursor.execute('insert into instructor_table values (?,?,?,?,?,?)', (instructor_id, instructor_name, instructor_email, instructor_image_url, first_access, last_access))
        self.connection.commit()

    def insert_into_enroll_table(self,instructor_id,all_courese_id):
        for course_id in all_courese_id:
            self.cursor.execute('insert into enroll_table values (?,?)', (instructor_id,course_id))
            self.connection.commit()
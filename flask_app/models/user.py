# pymysql connection 
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash
from flask_bcrypt import Bcrypt
import re

bcrypt = Bcrypt(app)
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User():
    # class variable: schema name for this app
    db = "chess_schema"

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.hashed_pwd = data['hashed_pwd']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # insert a new user in the database
    @classmethod
    def create(cls, data):
        # hash the password using Bcrypt
        # add hashed_pwd to data dictionary before insert into db
        data['hashed_pwd'] = bcrypt.generate_password_hash(data['password'])

        query = "INSERT INTO users (first_name, last_name, email, hashed_pwd) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(hashed_pwd)s);"
        new_id = connectToMySQL(cls.db).query_db(query, data)
        return new_id 

    # update existing user
    @classmethod
    def update(cls, data):
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE users.id = %(id)s;"
        connectToMySQL(cls.db).query_db(query, data)

        return

    # get all users in the database
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users"

        result = connectToMySQL(cls.db).query_db(query)
        if len(result) < 1:
            return None

        all_users = []
        for row in result:
            all_users.append(cls(row))
 
        return all_users


    # look up user by id
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"

        result = connectToMySQL(cls.db).query_db(query, data)
        if len(result) < 1:
            return None

        row = result[0]

        return cls( row )

    # look up a user by email
    @classmethod 
    def get_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        rows = connectToMySQL(cls.db).query_db(query, data)
        if len(rows) < 1:
            return False

        return cls( rows[0] )

    # validation of user data provided upon registration or update    
    @staticmethod
    def is_valid(data):
        is_valid = True

        # first name
        flash_catg = 'invalid_first_name'
        
        if len(data['first_name']) < 2:
             flash("Please provide a first name (at least 2 characters)", flash_catg)
             is_valid = False
        if len(data['first_name']) > 45:
             flash("First name cannot exceed 45 characters", flash_catg)
             is_valid = False

        # last name
        flash_catg = 'invalid_last_name'

        if len(data['last_name']) < 2:
             flash("Please provide a last name (at least 2 characters)", flash_catg)
             is_valid = False
        if len(data['last_name']) > 45:
             flash("Last name cannot exceed 45 characters", flash_catg)
             is_valid = False
        
        # email
        flash_catg = 'invalid_email'
        if len(data['email']) < 1:
            flash("Please provide an email address", flash_catg)
            is_valid = False
        elif not email_regex.match(data['email']):
             flash("Invalid email address", flash_catg)
             is_valid = False
        elif User.get_by_email(data):
            flash("Email address is already registered", flash_catg)
            is_valid = False

        return is_valid



    # validation of user data provided upon registration or update    
    @staticmethod
    def is_valid_password(data):
        is_valid = True

        # password
        flash_catg = 'invalid_password'

        if len(data['password']) < 1:
            flash('Please provide a password', flash_catg)
            is_valid = False
        elif len(data['password']) < 8:
            flash('Password must be at least 8 characters long', flash_catg)
            is_valid = False
        # # cannot get the regex to work as expected
        # #
        # # elif not re.match(r'[0-9]', data['password']):
        # #     flash('Password must contain at least 1 number and 1 uppercase letter', flash_catg)
        # #     is_valid = False
        # # elif not re.match(r'[A-Z]', data['password']):
        # #     flash('Password must contain at least 1 number and uppercase letter', flash_catg)
        # #     is_valid = False
        # else:
        #     found_digit = False
        #     found_caps = False
        #     for character in data['password']:
        #         if character.isdigit():
        #             found_digit = True
        #         elif character.isupper():
        #             found_caps = True
        #     if not (found_digit and found_caps):
        #         flash('Password must contain at least 1 number and 1 uppercase letter', flash_catg)
        #         is_valid = False

        # password confirmation
        flash_catg = 'invalid_confirm'
        
        if len(data['password_confirm']) < 1:
            flash('Please confirm password', flash_catg)
            is_valid = False
        elif not data['password'] == data['password_confirm']:
            flash('Password confirmation does not match password', flash_catg)
            is_valid = False

        return is_valid


    # arguments: email, password (string)
    @staticmethod
    def check_email_and_password(data):
        # verify that email is registered in database
        user = User.get_by_email(data)        
        if not user:
            return False
        
        # if so, use Bcrypt to check password against hashed pwd in database
        if not bcrypt.check_password_hash(user.hashed_pwd, data['password']):
            return False

        return True    


# validation of user data provided upon registration or update    
    @staticmethod
    def is_valid_name(data):
        is_valid = True

        # first name
        flash_catg = 'invalid_first_name'
        
        if len(data['first_name']) < 3:
             flash("Please provide a first name (at least 3 characters)", flash_catg)
             is_valid = False
        if len(data['first_name']) > 45:
             flash("First name cannot exceed 45 characters", flash_catg)
             is_valid = False

        # last name
        flash_catg = 'invalid_last_name'

        if len(data['last_name']) < 3:
             flash("Please provide a last name (at least 3 characters)", flash_catg)
             is_valid = False
        if len(data['last_name']) > 45:
             flash("Last name cannot exceed 45 characters", flash_catg)
             is_valid = False
        
        return is_valid






    
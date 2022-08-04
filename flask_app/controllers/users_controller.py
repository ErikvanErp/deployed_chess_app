from flask import render_template, request, redirect, session
from flask import flash
from flask_app import app
from flask_app.models import user, game


# controller for registration and login

@app.route('/')
def index():
    # get the opening board
    board  = "54312345"
    board += "60066666"
    board += "00600000"
    board += "06000000"
    board += "000C0000"
    board += "00000000"
    board += "CCC0CCCC"
    board += "BA9789AB"
    
    # convert to 8 x 8 array of ucodes for display
    board_array = [list(board[i:i+8]) for i in range(0,64,8)]
    ucodes_array = [[game.Game.pieces[tile][2] for tile in row] for row in board_array]

    return render_template("index.html", ucodes_array=ucodes_array)

@app.route('/user/new')
def user_new():

    return render_template("register.html")

    
@app.route('/user/register', methods=['POST'])
def user_register():
    # save posted form input as data dictionary in User object format
    data = {
        'first_name' : request.form['first_name'],
        'last_name' : request.form['last_name'],
        'email' : request.form['email'],
        'password' : request.form['password'],
        'password_confirm' : request.form['password_confirm'],
    }

    # check if form data are valid
    # register and login if valid
    # redirect back to root if invalid
    is_valid_user = user.User.is_valid(data)
    is_valid_password = user.User.is_valid_password(data)

    if is_valid_user and is_valid_password:
        new_id = user.User.create(data)
        session.clear()
        session["user_id"] = new_id
        session['first_name'] = data["first_name"]
        session['is_logged_in'] = True
        return redirect('/games')
    else:
        return redirect('/')

@app.route('/user/login', methods=['POST'])
def user_login():
    # save posted form input as data dictionary in User object format
    data = {
        'email' : request.form['email'],
        'password' : request.form['password']
    }
    
    # flash category 'is_valid_login'
    # tells the template where to display the messages
    if len(data['email']) < 1 or len(data['password']) < 1:
        flash("Please provide an email and password", 'invalid_login')
        return redirect('/')

    if not user.User.check_email_and_password(data):
        flash("invalid email/password", 'invalid_login')
        return redirect('/')
    
    # on valid login: store user data in session
    session.clear()
    this_user = user.User.get_by_email(data)
    session["user_id"] = this_user.id
    session['first_name'] = this_user.first_name
    session['is_logged_in'] = True
    return redirect('/games')
        

@app.route('/user/logout')
def user_logout():
    session.clear()
    return redirect('/')









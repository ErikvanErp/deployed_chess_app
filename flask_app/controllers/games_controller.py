from flask import render_template, request, redirect, session
from flask import flash
from flask_app import app
from flask_app.models import user, game
from flask_app.helpers.chess_rules import is_valid_move
from flask import json, jsonify

import math

# show all the active games of this user
@app.route('/games')
def games_show():
    if not session['is_logged_in']:
        return redirect('/')

    # show all active games (status == 1, 2, or 3)
    # in which current player is involved
    my_games = game.Game.get_active_games_by_user_id({"user_id": session["user_id"]})

    games_my_turn = []
    games_waiting = []
    for this_game in my_games:
        if ((this_game.current_is_white and this_game.number_of_moves % 2 == 0) 
            or (not this_game.current_is_white and this_game.number_of_moves % 2 == 1)):
            games_my_turn.append(this_game)
        else:
            games_waiting.append(this_game)

    # retrieve all pending games in which user is involved
    pending_games = game.Game.get_by_user_id({"user_id": session["user_id"], "status": 0})

    # filter out only those pending games not initiated by user
    number_pending = 0
    for pending_game in pending_games:
        if pending_game.opponent_id ==  session["user_id"]:
            number_pending += 1

    return render_template("games.html", games_my_turn=games_my_turn, games_waiting=games_waiting, number_pending=number_pending)


# load the form where user can invite other users to play
# and the form where user can accept invitations received
@app.route('/games/new')
def games_new():
    if not session['is_logged_in']:
        return redirect('/')

    all_users = user.User.get_all()

    # retrieve all pending games in which user is involved
    pending_games = game.Game.get_by_user_id({"user_id": session["user_id"], "status": 0})

    # filter out only those pending games not initiated by user
    invitations = []
    for pending_game in pending_games:
        if pending_game.opponent_id ==  session["user_id"]:
            invitations.append(pending_game)

    return render_template("games_invites.html", all_users=all_users, invitations=invitations)


# user has invited another user to play
# create a new game in the database
@app.route('/games/invite', methods=['POST'])
def games_invite():
    if not session['is_logged_in']:
        return redirect('/')

    if request.form["opponent"] == "-1":
        flash("Please select a player", "invite_error")
        return redirect('/games/new')
    
    data = {
        "user_id": session["user_id"],
        "opponent_id": request.form['opponent'],
        "white": request.form["white"]
    }
    new_game_id = game.Game.create(data)

    return redirect('/games')

# accept a game invitation
# this changes the status of the game to 1
@app.route('/games/<int:game_id>/accept')
def games_accept(game_id):
    if not session['is_logged_in']:
        return redirect('/')

    game.Game.accept_invitation({"games_id": game_id})
    return redirect('/games/new')


# render the game board
@app.route('/games/<int:game_id>/play')
def games_play(game_id):
    if not session['is_logged_in']:
        return redirect('/')

    this_game = game.Game.get_by_game_id({"game_id": game_id})

    return render_template("play.html", this_game=this_game)


# process a proposed move
@app.route('/games/move', methods=['POST'])
def make_move():
    if not session['is_logged_in']:
        return redirect('/')

    print(request.form)

    # retrieve the game 
    game_id = request.form['game_id']
    move_str = request.form['your_move']

    this_game = game.Game.get_by_game_id({"game_id": game_id})

    # status code greater than 3: game over     
    if int(this_game.status) > 3:
        return False

    # convert standard row-column notation used for user input
    # to array indices
    # example: f2f4 -> (1, 2, 3, 2)
    columns = {"a":7, "b":6, "c":5, "d":4, "e":3, "f":2, "g":1, "h":0}
    rows = {"1":0, "2":1, "3":2, "4":3, "5":4, "6":5, "7":6, "8":7}

    if len(move_str) != 4:
        is_valid = False
    elif (move_str[0] in columns
            and move_str[1] in rows
            and move_str[2] in columns 
            and move_str[3] in rows
            ):
        is_valid = True
    else:
        is_valid = False

    # make the move
    if is_valid:

        from_col = columns[move_str[0]]
        from_row = rows[move_str[1]]
        to_col = columns[move_str[2]]
        to_row = rows[move_str[3]]
        
        # if the move is valid according to the rules of chess
        # make the move
        if is_valid_move( this_game.game_state, from_row, from_col, to_row, to_col ):
            this_game.make_move( from_row, from_col, to_row, to_col )

    return redirect(f'/games/{game_id}/play')

# process a move submitted by player
# sent as a fetch request (method = "POST") in play.js
@app.route('/api/games/move', methods=['POST'])
def make_move_js():
    if not session['is_logged_in']:
        return (jsonify({}), 401)

    data = json.loads(request.data)

    game_id = int(data['game_id'])
    from_row = int(data['move_from'][0])
    from_col = int(data['move_from'][1])
    to_row = int(data['move_to'][0])
    to_col = int(data['move_to'][1])
        
    print("********************************")
    print("********************************")
    print("********************************")
    print(f"game {game_id}, move: {from_row}{from_col}{to_row}{to_col}")    
    print("********************************")
    print("********************************")
    print("********************************")

    this_game = game.Game.get_by_game_id({"game_id": game_id})

    print(f"this_game after query: {this_game.id}")

    if is_valid_move( this_game.game_state, from_row, from_col, to_row, to_col ):
        this_game.make_move( from_row, from_col, to_row, to_col )
        return (jsonify({}), 201)
    else:
        return (jsonify({}), 400)
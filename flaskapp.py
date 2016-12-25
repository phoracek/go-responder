from flask import Flask, request, render_template, send_from_directory

import match_manager

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

mm = match_manager.MatchManager()
mm.create_custom_match("debug", 9)

"""
print "---------------------------------------------------------"
mm.access_match("debug").place_stone(4, 4, 1)
mm.access_match("debug").place_stone(4, 5, 2)
mm.access_match("debug").place_stone(3, 5, 1)
print mm.access_match("debug").get_board_string()
mm.access_match("debug").place_stone(2, 5, 2)
mm.access_match("debug").place_stone(5, 5, 1)
mm.access_match("debug").place_stone(4, 6, 2)
print mm.access_match("debug").get_board_string()
mm.access_match("debug").place_stone(3, 6, 1)
"""

# DEBUG BUG
bug1 = [(5, 3, 1), (4, 3, 2),
        (5, 4, 1), (4, 4, 2),
        (4, 5, 1), (7, 7, 2),
        (4, 2, 1), (3, 3, 2),
        (3, 4, 1)]
bug12 = [(1, 8, 1), (1, 7, 2),
         (0, 7, 1), (3, 8, 2),
         (2, 7, 1), (4, 8, 2),
         (1, 6, 1), (5, 8, 2),

         (5, 3, 1), (4, 3, 2),
         (5, 4, 1), (4, 4, 2),
         (4, 5, 1), (7, 7, 2),
         (4, 2, 1), (3, 3, 2), ]
bug2 = [(5, 3, 1), (4, 3, 2),
        (5, 4, 1), (4, 4, 2),
        (4, 5, 1), (7, 7, 2),
        (4, 2, 1), (3, 3, 2),
        (3, 4, 1), (8, 8, 2),
        (2, 3, 1), (7, 8, 2),
        (3, 2, 1), (8, 7, 2), ]

for i in bug12:
    mm.access_match("debug").place_stone(i[0], i[1], i[2])
print mm.access_match("debug").get_board_string()

mm.access_match("debug").place_stone(3, 4, 1)
print mm.access_match("debug").get_board_string()

# DEBUG WIN 1
mm.create_custom_match("win_one", 9)
mm.access_match("win_one").place_stone(1, 0, 1)
mm.access_match("win_one").place_stone(1, 1, 2)
mm.access_match("win_one").place_stone(0, 1, 1)
mm.access_match("win_one").pass_turn(2)
mm.access_match("win_one").place_stone(2, 1, 1)
mm.access_match("win_one").pass_turn(2)
mm.access_match("win_one").place_stone(1, 2, 1)
mm.access_match("win_one").pass_turn(2)
mm.access_match("win_one").pass_turn(1)

# DEBUG WIN 2
mm.create_custom_match("win_two", 9)
mm.access_match("win_two").place_stone(1, 0, 2)
mm.access_match("win_two").place_stone(1, 1, 1)
mm.access_match("win_two").place_stone(0, 1, 2)
mm.access_match("win_two").pass_turn(1)
mm.access_match("win_two").place_stone(2, 1, 2)
mm.access_match("win_two").pass_turn(1)
mm.access_match("win_two").place_stone(1, 2, 2)
mm.access_match("win_two").pass_turn(1)
mm.access_match("win_two").pass_turn(2)

# ELSE
mm.create_custom_match("smaller", 5)
mm.create_custom_match("bigger", 15)



@app.route('/postit', methods=['POST', 'GET', 'PUT', 'CREATE'])
def postit():
    return str(request.method) + "\n" + str(request.form) + "\n"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)


@app.route("/test")
def test():
    return "<strong>It's Alive!</strong>"


#
@app.route('/try_to_respond')
def try_to_respond():
    return 'hello'


# remove pls
@app.route('/gimme')
def gimme():
    return str(mm.matches.keys())


@app.route('/watch_match', methods=['GET'])
def watch_match():
    match_id = request.args.get('match_id')
    if match_id:
        try:
            match = mm.access_match(match_id).get_board()
            return render_template("watch_match.html",
                                   match=match,
                                   history=mm.access_match(match_id).debug_history)
        except match_manager.MatchNotFound:
            return render_template("respond.html")  # TODO  += ERROR

    return render_template("respond.html")


@app.route('/game/match', methods=['PUT'])
def create_match():
    return str(mm.create_match(9))


@app.route('/game/<string:match_id>/board', methods=['GET'])
def get_board(match_id):
    if not match_id:
        return 'must pass match_id', 400
    try:
        return str(mm.access_match(match_id).get_board_string())
    except match_manager.MatchNotFound:
        return 'match not found', 404


@app.route('/game/<string:match_id>/stone', methods=['PUT'])
def place_stone(match_id):
    x = request.form['x']
    y = request.form['y']
    stone = request.form['stone']

    print request.form, request.args

    if not (match_id or x or y or stone):
        return 'must pass all parameters', 400

    try:
        return str(mm.access_match(match_id).place_stone(int(x), int(y), int(stone)))
    except match_manager.MatchNotFound:
        return 'match not found', 404
    except match_manager.StoneNotFound:
        return 'stone not found', 404
    except match_manager.OutOfRange:
        return 'out of range', 404
    except match_manager.InvalidMove:
        return 'invalid move', 404


@app.route('/game/<string:match_id>/pass_turn', methods=['PUT'])
def pass_turn(match_id):
    stone = request.form['stone']
    if not (match_id or stone):
        return 'must pass all parameters', 400

    try:
        return str(mm.access_match(match_id).pass_turn(int(stone)))
    except match_manager.MatchNotFound:
        return 'match not found', 404
    except match_manager.StoneNotFound:
        return 'stone not found', 404


@app.route('/game/<string:match_id>/forfeit', methods=['PUT'])
def forfeit(match_id):
    stone = request.form['stone']
    if not (match_id or stone):
        return 'must pass all parameters', 400

    try:
        return str(mm.access_match(match_id).forfeit(int(stone)))
    except match_manager.MatchNotFound:
        return 'match not found', 404
    except match_manager.StoneNotFound:
        return 'stone not found', 404


@app.route('/game/<string:match_id>/winner', methods=['GET'])
def get_on_turn(match_id):
    if not match_id:
        return 'must pass match_id', 400
    try:
        return str(mm.access_match(match_id).get_winner())
    except match_manager.MatchNotFound:
        return 'match not found', 404


@app.route('/game/<string:match_id>/on_turn', methods=['GET'])
def get_winner(match_id):
    if not match_id:
        return 'must pass match_id', 400
    try:
        return str(mm.access_match(match_id).get_on_turn())
    except match_manager.MatchNotFound:
        return 'match not found', 404


if __name__ == '__main__':
    print 'starting'
    app.run()

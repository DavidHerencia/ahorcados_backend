#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from flask_cors import CORS
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

@dataclass
class Player(db.Model):
    id: int
    username: str
    password: str
    logged_in: bool
    wins: int
    defeats: int
    ties: int

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    logged_in = db.Column(db.Boolean, nullable=False, default=False)
    wins = db.Column(db.Integer, nullable=False, default=0)
    defeats = db.Column(db.Integer, nullable=False, default=0)
    ties = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<player {self.username}>'

@dataclass
class Lobby(db.Model):
    id: int
    name: str
    player_id: int
    active: bool

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False, default=f'lobby {id}')
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f'<lobby {self.id}>'


@dataclass
class Word(db.Model):
    word: str
    length: int

    word = db.Column(db.String(20), primary_key=True)
    length = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<word {self.word}>'

@dataclass
class Game(db.Model):
    id: int
    player1_id: int
    player2_id: int
    word1: str
    word2: str
    lives1: int
    lives2: int
    guesses1: str
    guesses2: str
    outcome: int
    date: str

    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    word1 = db.Column(db.String(20), db.ForeignKey('word.word'), nullable=False)
    word2 = db.Column(db.String(20), db.ForeignKey('word.word'), nullable=False)
    lives1 = db.Column(db.Integer, nullable=False, default=6)
    lives2 = db.Column(db.Integer, nullable=False, default=6)
    guesses1 = db.Column(db.String(20), nullable=False, default='')
    guesses2 = db.Column(db.String(20), nullable=False, default='')
    outcome = db.Column(db.Integer, nullable=False, default=0)
    date = db.Column(db.String(20), nullable=False, default=f'{datetime.datetime.now()}')

    def __repr__(self):
        return f'<game {self.id}>'


with app.app_context():
        db.create_all()
        db.session.commit()

# routes
@app.route('/player', methods=['GET', 'POST'])
def route_player():
    if request.method == 'GET':
        return get_player()
    elif request.method == 'POST':
        return post_player()

@app.route('/player/<id>', methods=['GET', 'PUT', 'DELETE'])
def route_player_id(id):
    if request.method == 'GET':
        return get_player_id(id)
    elif request.method == 'PUT':
        return update_player_id(id)
    elif request.method == 'DELETE':
        return delete_player(id)
    
@app.route('/player/login', methods=['POST'])
def route_player_login():
    return player_login()


@app.route('/lobby', methods=['GET', 'POST'])
def route_lobby():
    if request.method == 'GET':
        return get_lobby()
    elif request.method == 'POST':
        return post_lobby()

@app.route('/lobby/<id>', methods=['GET', 'DELETE'])
def route_lobby_id(id):
    if request.method == 'GET':
        return get_lobby_id(id)
    elif request.method == 'DELETE':
        return delete_lobby(id)


@app.route('/game', methods=['GET', 'POST'])
def route_game():
    if request.method == 'GET':
        return get_game()
    elif request.method == 'POST':
        return post_game()

@app.route('/game/<id>', methods=['GET', 'PUT', 'DELETE'])
def route_game_id(id):
    if request.method == 'GET':
        return get_game_id(id)
    elif request.method == 'PUT':
        return update_game_id(id)
    elif request.method == 'DELETE':
        return delete_game(id)

@app.route('/game/<id>/guess', methods=['PUT'])
def route_game_id_guess(id):
    return update_game_id_guess(id)


@app.route('/word', methods=['GET', 'POST'])
def route_word():
    if request.method == 'GET':
        return get_word()
    elif request.method == 'POST':
        return post_word()

@app.route('/word/<word>', methods=['GET'])
def route_word_word(word):
    if request.method == 'GET':
        return get_word_word(word)

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = Player.query.order_by(Player.wins.desc()).all()
    leaderboard_data = [
        {
            'username': player.username,
            'wins': player.wins,
            'defeats': player.defeats,
            'gamesPlayed': player.wins + player.defeats + player.ties,
        }
        for player in leaderboard
    ]
    return jsonify(leaderboard_data)


# methods

####################
# Player
####################
def get_player():
    player = Player.query.all()
    return jsonify(player)


def post_player():
    json = request.get_json()
    player = Player.query.filter_by(username=json['username']).first()
    if player is None:
        player = Player(username=json['username'], password=json['password'])
        db.session.add(player)
        db.session.commit()
        return 'SUCCESS'
    else:   
        return 'FAIL'


def get_player_id(id):
    player = Player.query.get(id)
    return jsonify(player)


def update_player_id(id):
    json = request.get_json()
    player = Player.query.get(id)
    player.wins += json['wins']
    player.defeats += json['defeats']
    player.ties += json['ties']
    db.session.commit()
    return 'SUCCESS'


def delete_player(id):
    player = Player.query.get(id)
    db.session.delete(player)
    db.session.commit()
    return 'SUCCESS'

def player_login():
    input_player = request.get_json()
    player = Player.query.filter_by(username=input_player['username']).first()
    if player is not None:
        if player.password == input_player['password']:
            player.logged_in = True
            db.session.commit()
            return jsonify({"response": str(player.id)})
        else:
            return jsonify({"response": "FAIL"})
    else:
        return jsonify({"response": "FAIL"})

####################
# Lobby
####################
def get_lobby():
    lobby = Lobby.query.filter_by(active=True).all()
    return jsonify(lobby)


def post_lobby():
    json = request.get_json()
    lobby = Lobby(name=json['name'], player_id=json['player_id'])
    db.session.add(lobby)
    db.session.commit()
    return {'id': lobby.id}


def get_lobby_id(id):
    lobby = Lobby.query.get(id)
    return jsonify(lobby)


def delete_lobby(id):
    lobby = Lobby.query.get(id)
    lobby.active = False
    db.session.commit()
    return 'SUCCESS'


####################
# Game
####################
def get_game():
    game = Game.query.all()
    return jsonify(game)


def post_game():
    json = request.get_json()
    game = Game(id=json['id'], player1_id=json['player1_id'], player2_id=json['player2_id'], word1=json['word1'], word2=json['word2'])
    db.session.add(game)
    db.session.commit()
    return 'SUCCESS'


def get_game_id(id):
    game = Game.query.get(id)
    return jsonify(game)


def update_game_id(id):
    json = request.get_json()
    game = Game.query.get(id)
    game.outcome = json['outcome']
    db.session.commit()
    return 'SUCCESS'


def update_game_id_guess(id):
    json = request.get_json()
    game = Game.query.get(id)
    # check if guess1 or guess2 was sent
    if 'guesses1' in json:
        game.guesses1 = json['guesses1']
        if game.guesses1[-1] not in game.word1:
            game.lives1 -= 1
        db.session.commit()
        return 'SUCCESS'
    elif 'guesses2' in json:
        game.guesses2 = json['guesses2']
        if game.guesses2[-1] not in game.word2:
            game.lives2 -= 1
        db.session.commit()
        return 'SUCCESS'
    else:
        return 'FAIL'



####################
# Word
####################
def get_word():
    word = Word.query.all()
    return jsonify(word)


def post_word():
    json = request.get_json()
    string = json['word'].upper()
    length = len(string)
    word = Word(word=string, length=length)
    db.session.add(word)
    db.session.commit()
    return 'SUCCESS'




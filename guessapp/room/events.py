#importing socketio from events instead of extensions to load the object with all events
from flask import request, session, flash, redirect, url_for
from guessapp.room.extensions import socketio
from guessapp.room.routes import room_data
from flask_socketio import send, emit, join_room, leave_room

users = []
#GAME ARENA
@socketio.on("connect", namespace="/game")
def handle_game_connect():
    room_code = session.get("room_code")
    name = session.get("name")

    join_room(room_code)
    users.append({request.sid : name})
    print(users)
    message = {
        "name" : name,
        "message" : "has joined the game"
    }
    send(message, to = room_code, namespace = "/game")
    print("Player connected", request.sid)


@socketio.on("disconnect", namespace="/game")
def handle_game_disconnect():
    users.clear()
    room_code = session.get("room_code")
    name = session.get("name")
    
    leave_room(room_code)
    message = {
        "name" : name,
        "message" : "has left the game"
    }
    send(message, to = room_code, namespace = "/game")
    print("Player disconnected", request.sid)


@socketio.on("message", namespace="/game")
def handle_game_message(data):
    room_code = session.get("room_code")
    name = session.get("name")
    message = {
        "name" : name ,
        "message": data["data"]
    }
    print("Message received " , message)
    current_turn = users[0]
    print("Current Turn", current_turn, " Current requeest ", request.sid)
    if request.sid in current_turn:
        print("Correct Turn///i.e", current_turn[request.sid])
        users.pop(0)
        print("Popping",users)
        users.append(current_turn)
        send(message, to=room_code, namespace = "/game" )
    else:
        emit("alert", {"message": "Not Your Turn"}, to=request.sid, namespace = "/game")



#############################CHAT ARENA###############################################
@socketio.on("connect", namespace="/chat")
def handle_chat_connect():
    room_code = session.get("room_code")
    name = session.get("name")

    join_room(room_code)
    room_data[room_code]["members"]+=1
    message = {
        "name" : name,
        "message" : "has joined the chat"
    }
    send(message, to = room_code, namespace = "/chat")
    print("Client connected", request.sid)

@socketio.on("disconnect", namespace="/chat")
def handle_chat_disconnect():
    room_code = session.get("room_code")
    name = session.get("name")
    
    leave_room(room_code)
    room_data[room_code]["members"]-=1
    if room_data[room_code]["members"] == 0:
        del room_data[room_code]
    message = {
        "name" : name,
        "message" : "has left the chat"
    }
    send(message, to = room_code, namespace = "/chat")
    print("Client disconnected", request.sid)


@socketio.on("message", namespace="/chat")
def handle_chat_message(data):
    room_code = session.get("room_code")
    name = session.get("name")
    message = {
        "name" : name ,
        "message": data["data"]
    }
    room_data[room_code]["messages"].append(message)
    print("Message received " , message)
    send(message, to=room_code, namespace = "/chat" )
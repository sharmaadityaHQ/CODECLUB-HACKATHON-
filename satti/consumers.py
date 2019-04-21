from channels import Group
from .models import ChatMessage, ChatRoom, ChatUser
import json
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from django.conf import settings
from django.utils.timezone import now

debug = settings.DEBUG

@channel_session_user_from_http
def ws_add(message):
    author = ChatUser.objects.get(user=message.user)
    author.connect()
    if debug:
        print("WebSocket for user {} connected".format(message.user.username))
    rooms = author.chatrooms
    if debug:
        print("User {} in rooms {}".format(message.user.username, rooms.all()))
    for room in rooms.all():
        Group("chat-%s" % room.pk).send({"text": json.dumps({"connect": message.user.username, "room": room.pk})})
        Group("chat-%s" % room.pk).add(message.reply_channel)

@channel_session_user
def ws_message(message):
    read = json.loads(message.content['text'])
    room_id = read['room']
    room = ChatRoom.objects.get(pk=read['room'])
    author = ChatUser.objects.get(user=message.user)
    action_type = read["type"]
    group = Group("chat-%s" % room_id)

    if action_type == "message":
        send_message(room, author, read["msg"])
    
    elif action_type == "open":
        open_room(room, author)

    elif action_type == "join":
        join(room, author, message.reply_channel)

    elif action_type == "leave":
        leave(room, author)

    elif room.is_creator(author) or room.is_admin(author):
        if action_type == "ban":
            chatuser = ChatUser.objects.get(pk=read["target"])
            ban(room, author, chatuser)
            return
        
        elif action_type == "delete":
            ChatMessage.objects.get(pk=read["target"]).delete()
            group.send({
                "text": json.dumps({
                    "type": "delete",
                    "admin": message.user.username,
                    "message": read["target"],
                    "room": room_id
                    })
                })
        elif action_type == "admin":
            chatuser = ChatUser.objects.get(pk=read["target"])
            room.set_admin(chatuser)
            send_notify(room, "{} is now an admin".format(chatuser), chatuser)
    return

@channel_session_user
def ws_disconnect(message):
    author = ChatUser.objects.get(user=message.user)
    author.disconnect()
    rooms = author.chatrooms
    for room in rooms.all():
        room.users_online.remove(author)
        Group("chat-%s" % room.pk).send({"text": 
            json.dumps({"disconnect": message.user.username})})
        Group("chat-%s" % room.pk).discard(message.reply_channel)
        room.save()
    author.save()

"""
Following functions are for handling message data, making
model changes and sending notifications to group after
getting message type
"""

def send_message(room, author, text):
    new_message = ChatMessage.objects.create(
        room=room,
        text=text,
        author=author
        )
    room.add_message()
    Group("chat-%s" % room.pk).send({
        "text": json.dumps({
            "type": "message",
            "content": text,
            "user": author.user.username,
            "room": room.pk
            })
        })

def send_notify(room, text, author):
    new_message = ChatMessage.objects.create(
        room=room,
        text=text,
        notification=True,
        author=author
        )
    room.add_message()
    Group("chat-%s" % room.pk).send({
        "text": json.dumps({
            "type": "notify",
            "content": text,
            "room": room.pk
            })
        })

def ban(room, admin, banned):
    room.ban(banned)
    send_notify(room, "{} banned {}".format(admin, banned), admin)

def join(room, chatuser, reply_channel):
    if not room.is_banned(chatuser):
        room.users.add(chatuser)
        chatuser.chatrooms.add(room)
        group = Group("chat-%s" % room.pk)
        group.add(reply_channel)
        send_notify(room, "{} joined the room".format(chatuser), chatuser)

def leave(room, chatuser):
    room.users.remove(chatuser)
    chatuser.chatrooms.remove(room)
    send_notify(room, "{} left the room".format(chatuser), chatuser)

def open_room(room, chatuser):
    #mark all messages as read
    chatuser.read(room)
    #send signal to room
    Group("chat-%s" % room.pk).send({"text": json.dumps({
        "type": "open",
        "user": chatuser.user.username,
        "room": room.pk
        })
    })
    return
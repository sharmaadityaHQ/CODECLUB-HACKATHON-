# -*- coding: utf-8 -*-
from .helpers import *
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import ChatMessage, ChatRoom, ChatUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.template.loader import render_to_string
from .forms import ImageUploadForm, RoomCreationForm
import os.path

@login_required
def chat(request, id):
	"""
	Display individual chatroom

	**Context**

	``ìd``
		Primary key of the chatroom
		type: Int
	``room_name``
		Name of the room
		type: String
	``messages``
		Messages in the room to be rendered
		type: QuerySet[ChatMessage]

	**Template:**

	:template:`templates/chat.html`
	"""
	room = ChatRoom.objects.get(pk=id)
	return render(request, 'templates/chat.html', context = {
		'id': room.pk,
		'room_name': room.name,
		'messages': ChatMessage.objects.filter(room=room).order_by('created_at'),
		'users': room.users.all(),
		})

def json_messages(request, pk):
	chatuser = get_chatuser(request.user)
	room = ChatRoom.objects.get(pk=pk)
	content = {"data": []}
	if chatuser.in_room(room):
		messages = Message.objects.get(chatroom=room)
		for message in messages:
			content["data"].append({"user": message.author.user.username,
				"text": message.text, "time": iso_timestamp(message.created_at)})
	return JsonResponse(content)

def chat_list_json(request):
	chatuser = get_chatuser(request.user)
	chatrooms = chatuser.chatrooms.all()
	content = {"data": []}
	for chatroom in chatrooms:
		content["data"].append(chat_list_item(chatroom.pk, request.user))
	return JsonResponse(content)

def chat_info_json(request, id):
	return JsonResponse(chat_list_item(id, request.user))

def render_chat_list_item(request, pk):
	context = chat_list_item(pk, request.user)
	return render(request, "templates/chat_list_item.html", context)

def private_chat(request, username):
	names = ["Private chat between {} and {}".format(request.user.username, username),
			"Private chat between {} and {}".format(username, request.user.username)]
	if not ChatRoom.objects.filter(name__in=names).exists():
		create_private_chat(request, username)
	room = ChatRoom.objects.get(name=name)
	return render(request, 'templates/chat.html', context = {
		'id': room.pk,
		'room_name': username,
		'messages': ChatMessage.objects.filter(room=room),
		'users': room.users.all(),
		})

@login_required
def join_chatroom(request, id):
	room = ChatRoom.objects.get(pk=id)
	chatuser = get_chatuser(request.user)
	room.users.add(chatuser)
	chatuser.chatrooms.add(room)
	return HttpResponse(status=204)

@login_required
def leave_chatroom(request, id):
	room = ChatRoom.objects.get(pk=id)
	chatuser = get_chatuser(request.user)
	room.users.remove(chatuser)
	chatuser.chatrooms.remove(room)
	return HttpResponse(status=204)

@login_required
def main(request):
	chatuser = get_chatuser(request.user)
	chatuser.connect()
	chatuser.save()
	chats = chat_list(request)
	return render(request, 'templates/index.html', context = {
		"chats": chats,
		"in_chats": len(chats)>0
		})

def login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		auth_login(request, user)
	else:
		user = User.objects.create_user(username, '', password)
		chatuser = ChatUser.objects.create(user=user)
		auth_login(request, user)
	return redirect('/')

def logout(request):
	auth_logout(request)
	return redirect('/')

def profile(request, username):
	chatuser = get_chatuser(User.objects.get(username=username))
	return render(request, 'templates/profile.html', context = {
		"chatuser": chatuser,
		"username": username
		})

def chatroom(request, id):
	chatroom = ChatRoom.objects.get(pk=id)
	users = chatroom.users.all()
	chatuser = get_chatuser(request.user)
	if chatroom.is_private:
		other = chatroom.users.all().exclude(user=request.user).get()
		return profile(request, other.user.username)
	in_room = chatuser in users
	stats = chat_statistics(chatroom)
	context = {
		"is_admin": chatroom.is_admin(chatuser),
		"is_creator": chatroom.is_creator(chatuser),
		"chatroom": chatroom,
		"name": chatroom.name,
		"description": chatroom.description,
		"image": chatroom.image,
		"users": users,
		"pk": chatroom.pk,
		"in_room": in_room,
		"creator": chatroom.creator.user.username
		}
	return render(request, 'templates/chatroom.html', context = {**context, **stats})

def image(request, username):
	chatuser = get_chatuser(User.objects.get(username=username))
	image_data = open(chatuser.image.path, "rb").read()
	return HttpResponse(image_data, content_type="image/jpg")

def room_menu(request):
	return render(request, 'templates/room_menu.html', context = {
		"rooms": request.user.chatuser.chatrooms.all(),
		})

def upload_image(request):
	if request.method == "POST":
		form = ImageUploadForm(request.POST, request.FILES)
		if form.is_valid():
			chatuser = get_chatuser(request.user)
			chatuser.image = form.cleaned_data['image']
			chatuser.save()
	return HttpResponse(status=204)

def upload_chat_image(request, id):
	if request.method == "POST":
		form = ImageUploadForm(request.POST, request.FILES)
		if form.is_valid():
			chatroom = ChatRoom.objects.get(pk=id)
			chatroom.image = form.cleaned_data['image']
			chatroom.save()
	return HttpResponse(status=204)

def change_profile_text(request):
	if request.method =="POST":
		chatuser = get_chatuser(request.user)
		chatuser.profile_text = request.POST['text']
		chatuser.save()
	return HttpResponse(status=204)

def create_chatroom(request):
	if request.method=="POST":
		form = RoomCreationForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			creator = get_chatuser(request.user)
			new_room = ChatRoom.objects.get(name=form.cleaned_data['name'])
			new_room.users.add(creator)
			creator.chatrooms.add(new_room)
			new_room.creator = creator
			new_room.save()
			creator.save()
	return HttpResponse(status=204)

def create_private_chat(request, username):
	sender = get_chatuser(request.user)
	receiver = get_chatuser(User.objects.get(username=username))
	name = "Private chat between {} and {}".format(request.user.username, username)
	new_room = ChatRoom.objects.create(name=name)
	new_room.users.add(sender)
	new_room.users.add(receiver)
	sender.chatrooms.add(new_room)
	receiver.chatrooms.add(new_room)
	new_room.is_private = True
	new_room.save()
	sender.save()
	receiver.save()
	return HttpResponse(status=204)

def room_create_menu(request):
	form = RoomCreationForm()
	return render(request, "templates/create_chatroom.html", {"form": form})

def room_join_menu(request):
	chatuser = request.user.chatuser
	joinable_rooms = ChatRoom.objects.exclude(users=chatuser).exclude(is_private=True).exclude(banned=chatuser)
	return render(request, "templates/join_chatroom.html", {"joinable_rooms": joinable_rooms})
from django.contrib import admin

from .models import ChatRoom, ChatUser, ChatMessage

for i in (ChatRoom, ChatUser, ChatMessage):
	admin.site.register(i)
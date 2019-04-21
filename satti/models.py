from django.db import models
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils import timezone
from datetime import datetime

PROFILE_TEXT = "This is my profile text. Isn't it fun?"
CHATROOM_TEXT = "This is the default chatroom description. It is a bit longe"\
                "r than the default text for profiles, and that's intentional."
DEFAULT_IMAGE_PATH = "images/default.jpg"

class ChatRoom(models.Model):
	def __str__(self):
		return self.name

	name = models.CharField(max_length=100)
	image = models.ImageField(upload_to='images/', default=DEFAULT_IMAGE_PATH)
	max_users = models.PositiveSmallIntegerField(default=50)
	description = models.TextField(max_length=200, blank=True, default=CHATROOM_TEXT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	modified = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey('ChatUser', null=True, related_name="created_rooms")
	admins = models.ManyToManyField('ChatUser', related_name="admin_in")
	is_private = models.BooleanField(default=False)
	users = models.ManyToManyField('ChatUser', related_name="user_in")
	users_online = models.ManyToManyField('ChatUser')
	banned = models.ManyToManyField('ChatUser', related_name="banned_in")

	def add_message(self):
		self.modified = timezone.now()
		self.save()

	def is_creator(self, chatuser):
		return self.creator == chatuser

	def is_admin(self, chatuser):
		return self.admins.filter(pk=chatuser.pk).exists()

	def set_admin(self, chatuser):
		self.admins.add(chatuser)

	def is_banned(self, chatuser):
		return self.banned.filter(pk=chatuser.pk).exists()

	def has_messages(self):
		return ChatMessage.objects.filter(room=self).exists()

	def latest_message(self):
		return ChatMessage.objects.filter(room=self).latest('created_at')

	def get_users_online(self):
		return self.users_online.count()

	def ban(self, chatuser):
		self.banned.add(chatuser)
		chatuser.chatrooms.remove(self)
		if chatuser in self.users.all():
			self.users.remove(chatuser)

	def get_banned(self, chatuser):
		return chatuser.banned_in(self).exists()


class ChatUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	chatrooms = models.ManyToManyField(ChatRoom, blank=True)
	image = models.ImageField(upload_to='images/', default=DEFAULT_IMAGE_PATH)
	profile_text = models.CharField(default=PROFILE_TEXT, max_length=200)
	contacts = models.ManyToManyField("self", blank=True, related_name="contacts")
	online = models.BooleanField(default=False)
	last_seen = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username

	def connect(self):
		self.online = True

	def disconnect(self):
		self.online = False
		self.last_seen = timezone.now()

	def read(self, chatroom):
		messages = ChatMessage.objects.filter(room=chatroom).filter(read_by=self)
		for msg in messages:
			msg.set_read(self)

	"""
	Gets the last seen timestamp in as a string
	"""
	def get_last_seen(self):
		from .helpers import list_timestamp
		if self.last_seen is not None:
			return list_timestamp(self.last_seen)
		else: return "never"

class ChatMessage(models.Model):
	author = models.ForeignKey('ChatUser', blank=True, null=True)
	room = models.ForeignKey('ChatRoom')
	text = models.TextField(max_length = 1000)
	created_at = models.DateTimeField(auto_now_add=True)
	image = models.ImageField(blank=True)
	notification = models.BooleanField(default=False)
	read_by = models.ManyToManyField('ChatUser', related_name="has_read")

	def is_seen(self):
		return self.read_by.all().exists()

	def set_read(self, chatuser):
		self.read_by.add(chatuser)
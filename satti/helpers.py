from datetime import datetime
from satti.models import ChatMessage, ChatRoom, ChatUser

def get_chatuser(user):
	return ChatUser.objects.get(user=user)

def chat_list_item(pk, user):
	"""
	Helper function for getting contextual information about a chatroom.

	Arguments:
		pk -- room primary key (type: Int)
		user -- user (type django.auth.User)

	Return:
		A dict
	"""
	chatroom = ChatRoom.objects.get(pk=pk)
	time = list_timestamp(chatroom.modified)
	has_msg = chatroom.has_messages()
	if chatroom.is_private:
		other = chatroom.users.exclude(
			user__username=user.username).get()
		name = other.user.username
		img_url = other.image.url
		private = True
		if other.online:
			online = "online"
		else:
			online = "last seen {}".format(other.get_last_seen())
	else:
		private = False
		name = chatroom.name
		img_url = chatroom.image.url
		online_count = chatroom.get_users_online()
		if(online_count > 1):
			online = "{} users online (including you)".format(online_count)
		else:
			online = ""
	if has_msg:
		last_msg = chatroom.latest_message()
		notification = last_msg.notification
		data = {"name": name, 
			"last_msg_text": last_msg.text,
			"last_msg_time": time,
			"img_url": img_url,
			"has_msg": has_msg,
			"pk": pk,
			"online": online,
			"private": private
			}
		if notification:
			return data
		else:
			data['last_msg_author'] = last_msg.author.user.username
			return data
	else:
		return {"has_msg": has_msg, "img_url": img_url, "last_msg_time": time,
			"name": name, "online": online, "private": private, "pk": pk}

def chat_list_item_with_messages(chatroom, user):
	data = chat_list_item(chatroom.pk, user)
	data["messages"] = []
	messages = Message.objects.get(chatroom=chatroom).all()
	for message in messages:
		data["messages"].append({"user": message.author,
		"text": message.text, "time": iso_timestamp(message.created_at)})

def chat_list(request):
	chatuser = get_chatuser(request.user)
	chatrooms = chatuser.chatrooms.all().order_by('-modified')
	chats = [chat_list_item(chat.pk, request.user) for chat in chatrooms]
	return chats

def chat_statistics(chatroom):
	message_count =  ChatMessage.objects.filter(room=chatroom).count()
	user_count = chatroom.users.count()
	created_at = chatroom.created_at
	days = max((timezone.now() - created_at).days, 1)
	avg_daily_msgs = message_count / days
	return{
		"message_count": message_count,
		"chatroom_name": chatroom.name,
		"user_count": user_count,
		"created_at": created_at,
		"avg_daily_msgs": avg_daily_msgs
		}

def iso_timestamp(time):
	return time.isoformat()[0:19].replace("T"," ")
	
def list_timestamp(time):
	today = datetime.now()
	days = (datetime.today().date() - time.date()).days
	day_of_year = today.timetuple().tm_yday
	if days == 0:
		return "{}".format(time.strftime("%H:%M"))
	elif days == 1:
		return "yesterday at {}".format(time.strftime("%H:%M"))
	else:
		return time.strftime("%d.%m.%y")
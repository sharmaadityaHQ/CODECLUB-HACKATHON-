"""sattisite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from satti import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.main),
    url(r'^admin/', admin.site.urls),
    url(r'^chat/(?P<id>[0-9]{1,4})/', views.chat),
    url('^', include('django.contrib.auth.urls')),
    url(r'^signin/$', views.login),
    url(r'^signout/$', views.logout),
    url(r'^profile/(?P<username>\w+)/', views.profile),
    url(r'^chatroom/(?P<id>[0-9]{1,4})/', views.chatroom, name="chatroom-menu"),
    url(r'^image/(?P<username>\w+)/', views.image),
    url(r'^menu/', views.room_menu),
    url(r'^upload/', views.upload_image, name="upload-image"),
    url(r'^upload-chat/(?P<id>[0-9]{1,4})/', views.upload_chat_image, name="upload-chat-image"),
    url(r'^text/', views.change_profile_text, name="text"),
    url(r'^create/', views.create_chatroom, name="create-chatroom"),
    url(r'^new-room/', views.room_create_menu, name="room-create-menu"),
    url(r'^join-room/', views.room_join_menu, name="room-join-menu"),
    url(r'^join/(?P<id>[0-9]{1,4})/', views.join_chatroom, name="join-chatroom"),
    url(r'^leave/(?P<id>[0-9]{1,4})/', views.leave_chatroom, name="leave-chatroom"),
    url(r'^private/(?P<username>\w+)/', views.private_chat, name="private-chat"),
    url(r'^list/', views.chat_list_json, name="chat-list-json"),
    url(r'^info/(?P<id>[0-9]{1,4})/', views.chat_info_json, name="chat-info-json"),
    url(r'^chat-list-item/(?P<pk>[0-9]{1,4})/', views.render_chat_list_item, name="chat-list-item"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
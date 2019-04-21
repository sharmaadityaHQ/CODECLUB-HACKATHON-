from django import forms
from .models import ChatRoom

class ImageUploadForm(forms.Form):
	image = forms.ImageField()

class RoomCreationForm(forms.ModelForm):
	class Meta:
		model = ChatRoom
		fields = ['name', 'description']
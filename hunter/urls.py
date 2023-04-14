from django.urls import path

from hunter.views import index, event, supported_websites


urlpatterns = [
	path('', index, name="index"),
	path('event/', event, name="index"),
	path('supported-websites/', supported_websites, name="index")
]
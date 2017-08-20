from django.conf.urls import url, include
from .views import homepage, chatbot, response

urlpatterns = [
    url(r'^$', homepage, name='homepage' ),
    url(r'^chatbot/$', chatbot, name='chatbot' ),
    url(r'^response/$', response, name='response' ),
]

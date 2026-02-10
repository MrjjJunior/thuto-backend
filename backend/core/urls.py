from django.urls import path
from .views import hello, register, login

urlpatterns = [
    # path('', home),
    path('hello/', hello),
    path("register/", register),
    path("login/", login),

]
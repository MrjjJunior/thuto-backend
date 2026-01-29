from django.urls import path
from .views import hello, register

urlpatterns = [
    # path('', home),
    path('hello/', hello),
    path("register/", register),
]
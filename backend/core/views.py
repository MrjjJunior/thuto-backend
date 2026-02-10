from django.shortcuts import render
# Create your views here.
# from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from core.services.retriever import retrieve_context
# from core.services.generate import genrate_answer

# def home(request):
#     return HttpResponse("Hello, Django 👋")

@api_view(['GET'])
def hello(request):
    return Response({"message": "Reponding with request"})

@api_view(["POST"])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response(
            {"error": "username, email, and password are required"},
            status=400
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=400
        )

    User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response(
        {"message": "User registered successfully"},
        status=201
    )

@api_view(["POST"])
def login(request):
    identifier = request.data.get("identifier")  # username or email
    password = request.data.get("password")

    if not identifier or not password:
        return Response(
            {"error": "identifier and password are required"},
            status=400
        )

    # Allow login via email OR username
    try:
        user = User.objects.get(email=identifier)
        username = user.username
    except User.DoesNotExist:
        username = identifier

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {"error": "Invalid credentials"},
            status=401
        )

    return Response(
        {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        },
        status=200
    )

@api_view(["POST"])
def ask_question(request):
    question = request.data.get("question")

    ...

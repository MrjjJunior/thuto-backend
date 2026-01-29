from django.shortcuts import render
# Create your views here.
# from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# def home(request):
#     return HttpResponse("Hello, Django 👋")

@api_view(['GET'])
def hello(request):
    return Response({"message": "Reponding with request"})

@api_view(["POST"])
def register(request):
    try:
        data = request.data # DRF parses JSON automatically

        if User.objects.filter(username=data["username"]).exists():
            return Response(
                {"error": "Username already exits"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"]
        )

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
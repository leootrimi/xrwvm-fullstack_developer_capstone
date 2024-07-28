from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from .models import CarMake, CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"userName": username, "status": "Failed"})
    except Exception as e:
        logger.error("Error in login_user: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_cars(request):
    try:
        count = CarMake.objects.filter().count()
        if count == 0:
            initiate()
        car_models = CarModel.objects.select_related('car_make')
        cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
        return JsonResponse({"CarModels": cars})
    except Exception as e:
        logger.error("Error in get_cars: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def registration(request):
    try:
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        first_name = data['firstName']
        last_name = data['lastName']
        email = data['email']
        username_exist = User.objects.filter(username=username).exists()
        email_exist = User.objects.filter(email=email).exists()

        if not username_exist and not email_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"userName": username, "error": "Already Registered"})
    except Exception as e:
        logger.error("Error in registration: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def logout_user(request):
    try:
        logout(request)
        return JsonResponse({"status": "Logged out"})
    except Exception as e:
        logger.error("Error in logout_user: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

def get_dealerships(request, state="All"):
    try:
        if state == "All":
            endpoint = "/fetchDealers"
        else:
            endpoint = f"/fetchDealers/{state}"
        dealerships = get_request(endpoint)
        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        logger.error("Error in get_dealerships: %s", e)
        return JsonResponse({"status": 500, "error": str(e)})


def get_dealer_reviews(request, dealer_id):
    try:
        if dealer_id:
            endpoint = f"/fetchReviews/dealer/{dealer_id}"
            reviews = get_request(endpoint)
            for review_detail in reviews:
                response = analyze_review_sentiments(review_detail['review'])
                review_detail['sentiment'] = response['sentiment']
            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            return JsonResponse({"status": 400, "message": "Bad Request"})
    except Exception as e:
        logger.error("Error in get_dealer_reviews: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

def get_dealer_details(request, dealer_id):
    try:
        if dealer_id:
            endpoint = f"/fetchDealer/{dealer_id}"
            dealership = get_request(endpoint)
            return JsonResponse({"status": 200, "dealer": dealership})
        else:
            return JsonResponse({"status": 400, "message": "Bad Request"})
    except Exception as e:
        logger.error("Error in get_dealer_details: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def add_review(request):
    try:
        if not request.user.is_anonymous:
            data = json.loads(request.body)
            response = post_review(data)
            return JsonResponse({"status": 200})
        else:
            return JsonResponse({"status": 403, "message": "Unauthorized"})
    except Exception as e:
        logger.error("Error in add_review: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

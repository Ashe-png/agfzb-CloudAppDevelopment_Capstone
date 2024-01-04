from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .restapis import get_dealers_from_cf, get_dealer_by_id, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
import logging
from datetime import datetime
from django.http import HttpResponse
# from .models import CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


def about(request):
    return render(request, 'djangoapp/about.html')


def contact(request):
    return render(request, 'djangoapp/contact.html')


def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(to=reverse('djangoapp:index'))
        else:
            return redirect('djangoapp:index')


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


def registration_request(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)
  


def get_dealerships(request):
    if request.method == "GET":
        url = "https://ashishkhatak-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://ashishkhatak-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context["reviews"] = reviews
        dealer = get_dealer_by_id(
            "https://ashishkhatak-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get", dealer_id)
        context["dealer"] = dealer
        # return render(request, 'djangoapp/dealer_details.html', context)
        return HttpResponse(reviews)


def add_review(request, dealer_id):
    context = {}
    # if request.method == "GET":
    #     url = "https://e29b86ca.eu-gb.apigw.appdomain.cloud/api/dealership"
    #     dealer = get_dealer_from_cf_by_id(url, dealer_id)
    #     cars = CarModel.objects.filter(dealer_id=dealer_id)
    #     context["cars"] = cars
    #     context["dealer"] = dealer
    #     return render(request, 'djangoapp/add_review.html', context)


    if request.user.is_authenticated:
        if request.method == "POST":
            url = "https://ashishkhatak-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"      
            # if 'purchasecheck' in request.POST:
            #     was_purchased = True
            # else:
            #     was_purchased = False
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            for car in cars:
                if car.id == int(request.POST['car']):
                    review_car = car  
            review = {}
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = request.POST['name']
            review["dealership"] = dealer_id
            review["review"] = request.POST['content']
            review["purchase"] = was_purchased
            review["purchase_date"] = request.POST['purchasedate']
            review["car_make"] = review_car.make.name
            review["car_model"] = review_car.name
            review["car_year"] = review_car.year.strftime("%Y")
            json_payload = {}
            json_payload["review"] = review
            response = post_request(url, json_payload)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    else:
        # User is not authenticated, you might want to redirect to a login page
        return HttpResponse("You are not authenticated. Please log in.")
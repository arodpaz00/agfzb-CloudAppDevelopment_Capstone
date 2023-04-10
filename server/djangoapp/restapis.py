# import requests
# import json
# # import related models here
# from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



from requests.auth import HTTPBasicAuth

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import json
import requests
from .restapis import get_request, analyze_review_sentiments, post_request
from .models import CarDealer, DealerReview
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from datetime import datetime


# Create a `get_request` to make HTTP GET requests
# def get_request(url,**kwargs):
#     print(kwargs)
#     print("GET from {} ".format(url))
#     try:
#         # Call get method of requests library with URL and parameters
#         response = requests.get(url, headers={'Content-Type': 'application/json'},
#                                     params=kwargs)
#     except:
#         # If any error occurs
#         print("Network exception occurred")
#     status_code = response.status_code
#     print("With status {} ".format(status_code))
#     json_data = json.loads(response.text)
#     return json_data
def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key:
            # Call get method of requests library with URL, parameters, and API key
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        # Call post method of requests library with URL, payload and parameters
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def analyze_review_sentiments(dealerreview):
    api_key = "your_api_key"
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/your_instance_id/v1/analyze?version=2021-09-01"
    features = {"sentiment": {}}
    response = get_request(url, text=dealerreview, version='2021-09-01', features=features, return_analyzed_text=True)
    sentiment = response["sentiment"]["document"]["score"]
    return sentiment

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        for dealer in dealers:
            # Check if the dealer ID matches
            if dealer["doc"]["dealership"]["id"] == dealerId:
                # Get the list of reviews from dealerdoc
                dealerreviews = dealer["doc"]["reviews"]
                for dealerreview in dealerreviews:
                    review_obj = DealerReview()
                    # Set the review attributes
                    review_obj.id = dealerreview["id"]
                    review_obj.name = dealerreview["name"]
                    review_obj.review = dealerreview["review"]
                    review_obj.sentiment = analyze_review_sentiments(review_obj.review)
                    review_obj.purchase = dealerreview["purchase"]
                    review_obj.purchase_date = dealerreview["purchase_date"]
                    review_obj.car_make = dealerreview["car_make"]
                    review_obj.car_model = dealerreview["car_model"]
                    review_obj.car_year = dealerreview["car_year"]
                    results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def get_dealer_details(request, dealer_id):
    url = "https://c74e65dd.eu-gb.apigw.appdomain.cloud/api/review"
    dealer_url = "https://c74e65dd.eu-gb.apigw.appdomain.cloud/api/dealership?dealerId={}".format(dealer_id)
    reviews = get_dealer_reviews_from_cf(dealer_url, dealer_id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Get the review data
            review = dict()
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = request.user.first_name + " " + request.user.last_name
            review["dealership"] = dealer_id
            review["review"] = request.POST["review"]
            review["purchase"] = request.POST.get("purchasecheck")
            sentiment = analyze_review_sentiments(review["review"])
            post_result = post_request(url, json_payload={"review": review})
            print(post_result)
        context = {"dealer": get_dealer_by_id(dealer_id), "reviews": reviews}
        return render(request, "djangoapp/dealer_details.html", context=context)
    else:
        url = reverse("djangoapp:login")
        return HttpResponseRedirect(url)

@login_required
def add_review(request, dealer_id):
    if request.method == 'POST':
        # Get the review data
        review = dict()
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.user.first_name + " " + request.user.last_name
        review["dealership"] = dealer_id
        review["review"] = request.POST["review"]
        review["purchase"] = request.POST.get("purchasecheck")
        sentiment = analyze_review_sentiments(review["review"])
        post_result = post_request(url="https://us-south.functions.appdomain.cloud/api/v1/web/5467d6f6-b359-4248-85ba-89608b3eba5c/dealership-package/post-review", json_payload={"review": review})
        print(post_result)
        return HttpResponseRedirect(reverse("djangoapp:dealer_details", kwargs={"dealer_id": dealer_id}))
    else:
        cars = CarModel.objects.all()
        context = {"dealer": get_dealer_by_id(dealer_id), "cars": cars, "review_form": ReviewForm()}
        return render(request, "djangoapp/add_review.html", context=context)
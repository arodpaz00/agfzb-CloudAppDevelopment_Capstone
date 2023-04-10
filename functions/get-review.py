import json
import requests
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

def main(dict):
    
    # Get dealerId parameter from request
    dealer_id = dict.get('dealerId', '')
    
    # Check if dealerId parameter is provided
    if not dealer_id:
        return {"error": "dealerId parameter is missing"}
    
    # Connect to IBM Cloudant service
    client = Cloudant.iam(
        account_name=dict["COUCH_USERNAME"],
        api_key=dict["IAM_API_KEY"],
        connect=True,
    )
    
    # Check if connection is successful
    if not client:
        return {"error": "Failed to connect to Cloudant service."}
    
    try:
        # Get reviews database
        reviews_db = client['reviews']
        
        # Create a query index for dealership id
        query = {
            "selector": {
                "dealership": {
                    "$eq": int(dealer_id)
                }
            }
        }
        
        # Search for reviews for the given dealership
        reviews = reviews_db.get_query_result(query)
        
        # Create a list of reviews
        review_list = []
        for review in reviews:
            review_dict = {
                "id": review['_id'],
                "name": review['name'],
                "dealership": review['dealership'],
                "review": review['review'],
                "purchase": review.get('purchase', False),
                "purchase_date": review.get('purchase_date', ''),
                "car_make": review.get('car_make', ''),
                "car_model": review.get('car_model', ''),
                "car_year": review.get('car_year', '')
            }
            review_list.append(review_dict)
        
        # Close Cloudant client connection
        client.disconnect()
        
        # Return the list of reviews
        return review_list
    
    except CloudantException as ex:
        # Handle CloudantException
        return {"error": "A CloudantException occurred: {}".format(ex)}
    
    except Exception as ex:
        # Handle other exceptions
        return {"error": "An exception occurred: {}".format(ex)}

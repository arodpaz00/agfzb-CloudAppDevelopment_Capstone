#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import json
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def main(dict):
    authenticator = IAMAuthenticator(dict["IAM_API_KEY"])
    client = CloudantV1(
        authenticator=authenticator,
        url=dict["CLOUDANT_URL"],
        disable_ssl_verification=True
    )
    client.set_service_url(dict["CLOUDANT_URL"])

    # Get the JSON data from the request body
    review = json.loads(dict["__ow_body"])["review"]

    # Create the new document to be added to the reviews database
    new_review = {
        "_id": str(review["id"]),
        "name": review["name"],
        "dealership": review["dealership"],
        "review": review["review"],
        "purchase": review["purchase"],
        "purchase_date": review["purchase_date"],
        "car_make": review["car_make"],
        "car_model": review["car_model"],
        "car_year": review["car_year"]
    }

    try:
        # Add the new review document to the reviews database
        response = client.post_document(
            db="reviews",
            document=new_review
        ).get_result()

        return {
            "message": "Review added successfully"
        }

    except:
        return {
            "message": "Something went wrong on the server"
        }

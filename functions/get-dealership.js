const { CloudantV1 } = require("@ibm-cloud/cloudant");
const { IamAuthenticator } = require("ibm-cloud-sdk-core");

function main(params) {
  const authenticator = new IamAuthenticator({ apikey: "roacRYxCB_uuFUF2wDL4LPCJG3D9PxbQvZuE0ePyNLjj"});
  const cloudant = CloudantV1.newInstance({
    authenticator: authenticator,
  });
  cloudant.setServiceUrl("https://apikey-v2-z5nu84ow61883zgqin76h4rcoiglruuq37hf86xg1i7:eae61a55f614be341991206100509812@b57f565c-8ca6-4d73-b6d8-10a18a902ad2-bluemix.cloudantnosqldb.appdomain.cloud");

  // check if a state was provided
  if (params.state) {
    return getDealershipsByState(cloudant, params.state);
  } else {
    return getAllDealerships(cloudant);
  }
}

function getAllDealerships(cloudant) {
  return cloudant
    .postFind({
      db: "dealerships",
      selector: {},
      fields: ["id", "city", "state", "st", "address", "zip", "lat", "long"],
    })
    .then((response) => {
      return { dealerships: response.result.docs };
    })
    .catch((err) => {
      console.log(err);
      return { error: "Something went wrong on the server" };
    });
}
function getDealershipsByState(cloudant, state) {
  return cloudant
    .postFind({
      db: "dealerships",
      selector: { st: state },
      fields: ["id", "city", "state", "st", "address", "zip", "lat", "long"],
    })
    .then((response) => {
      if (response.result.docs.length === 0) {
        return { error: "The state does not exist" };
      } else {
        return { dealerships: response.result.docs };
      }
    })
    .catch((err) => {
      console.log(err);
      return { error: "Something went wrong on the server" };
    });
}


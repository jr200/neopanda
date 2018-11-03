import json
import sys
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

VALID_DATA = 0
NO_DATA = 1
INVALID_FIELD = 2

@app.route("/")
def default():
    return "Here is nothing"

@app.route("/onboardPerson", methods=["POST","GET"])
def onboardPerson():
    print("called onboardPerson", file=sys.stderr)
    print(request.data, file=sys.stderr)
    validation_result = validateDocumentData(request.data)

    if validation_result == NO_DATA:
        return getJsonResponse(400, "Error", "No document data provided")
    elif validation_result == INVALID_FIELD:
        return getJsonResponse(400, "Error", "Not all fields are valid")
    
    return getJsonResponse(200, "Approved", "Document data posted successfully")

@app.route("/checkAttestation", methods=["POST", "GET"])
def checkAttestation():
    print("called checkAttestation") 
    validation_result = validateAttestationData(request.data)

    if validation_result == NO_DATA:
        return getJsonResponse(400, "Error", "No attestation data provided")
    elif validation_result == INVALID_FIELD:
        return getJsonResponse(400, "Error", "Not all fields are valid")
    
    return getJsonResponse(200, "Approved", "Attestation approved")

def validateDocumentData(documentData):
    if documentData == None or not documentData.strip():
        return NO_DATA

    return VALID_DATA

def validateAttestationData(attestationData):
    if attestationData == None or not attestationData.strip():
        return NO_DATA

    return VALID_DATA

def getJsonResponse(statusCode, status, message):
    return json.dumps({
        statusCode: statusCode,
        status: status,
        message: message
    })

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="127.0.0.1", debug=True, port=80)

import json
import sys
import requests
from flask import Flask, request
from flask_cors import CORS
import rsa
import rsa.pkcs1
import base64

app = Flask(__name__)
cors = CORS(app)

VALID_DATA = 0
NO_DATA = 1
INVALID_FIELD = 2

HASH_METHOD = "SHA-512"


@app.route("/")
def default():
    return "Here is nothing"


def getPublicKey(identity):

    id_map = {
        "tai.lung@gmail.com": {
            "public": "/demo-keys/tailung_rsa.pem.pub",
            "private": "/demo-keys/tailung_rsa"
        },
        "munich": {
            "public": "/demo-keys/munich_rsa.pem.pub",
            "private": "/demo-keys/munich_rsa"
        },
        "zurich": {
            "public": "/demo-keys/zurich_rsa.pem.pub",
            "private": "/demo-keys/zurich_rsa"
        }
    }

    return id_map[identity.lower()]


@app.route("/signData", methods=["POST", "GET"])
def signData():
    user_id = request.json["userId"]
    privateKeyFile = request.json["privateKeyFile"]

    with open(privateKeyFile, 'r') as f:
        file_data = f.read()

    privateKey = rsa.PrivateKey.load_pkcs1(file_data, "PEM")

    user_id_hash = rsa.compute_hash(user_id.encode("utf-8"), HASH_METHOD)

    signedUserId = rsa.sign_hash(user_id_hash, privateKey, HASH_METHOD)

    res = {
        "userId": user_id,
        # "userIdHash": base64.encodestring(user_id_hash).decode("ascii"),
        "privateKeyFile": privateKeyFile,
        "signedUserId": base64.encodestring(signedUserId).decode("ascii")
    }

    return json.dumps(res)


@app.route("/verifyData", methods=["POST", "GET"])
def verifyData():
    user_id = request.json["userId"]
    signedUserId = request.json["signedUserId"]
    publicKeyFile = request.json["publicKeyFile"]

    user_id_hash = rsa.compute_hash(user_id.encode("utf-8"), HASH_METHOD)

    with open(publicKeyFile, 'r', encoding="ascii") as f:
        file_data = f.read()

    publicKey = rsa.PublicKey.load_pkcs1(file_data)
    signedUserId = base64.decodestring(signedUserId.encode("ascii"))

    try:
        verify = rsa.verify(user_id.encode("utf-8"), signedUserId, publicKey)
        verifyResult = "Success"
    except rsa.pkcs1.VerificationError as e:
        verifyResult = "Failed"

    res = {
        "userId": user_id,
        # "userIdHash": base64.encodestring(user_id_hash).decode("ascii"),
        "publicKeyFile": publicKeyFile,
        # "signedUserId": base64.encodestring(signedUserId).decode("ascii"),
        "verifyResult": verifyResult
    }

    return json.dumps(res)


@app.route("/testNeoConnection", methods=["POST", "GET"])
def testNeoConnection():
    print("called testNeoConnection")
    payload = {"jsonrpc": "2.0", "id": 5, "method": "getversion", "params": []}

    res = requests.post(
        "http://neo-nodes:30333/testNeoConnection", json=payload)
    print("received POST result")
    print(res.status_code)
    result = res.json()
    print(result)
    return json.dumps(result)


@app.route("/onboardPerson", methods=["POST", "GET"])
def onboardPerson():
    print("called onboardPerson", file=sys.stderr)
    validation_result = validateDocumentData(request.data)

    if validation_result == NO_DATA:
        return getJsonResponse(400, "Error", "No document data provided")
    elif validation_result == INVALID_FIELD:
        return getJsonResponse(400, "Error", "Not all fields are valid")

    data = request.json["data"]
    user_id = data["userId"]
    print(user_id)
    signedUserId = request.json["signedUserId"]
    signedUserId = base64.decodestring(signedUserId.encode("ascii"))

    issuerPrivateKeyFile = getPublicKey("Munich")["private"]
    with open(issuerPrivateKeyFile, 'r') as f:
        file_data = f.read()

    issuerPrivateKey = rsa.PrivateKey.load_pkcs1(file_data, "PEM")
    docHash = rsa.compute_hash(json.dumps(data).encode("utf-8"), HASH_METHOD)
    signedDocHash = rsa.sign_hash(docHash, issuerPrivateKey, HASH_METHOD)
    signedDocHash = base64.encodestring(signedDocHash).decode("ascii")

    userPublicKeyFile = getPublicKey(user_id)["public"]
    print(userPublicKeyFile)
    with open(userPublicKeyFile, 'r', encoding="ascii") as f:
        file_data = f.read()

    userPublicKey = rsa.PublicKey.load_pkcs1(file_data)

    try:
        verify = rsa.verify(user_id.encode("utf-8"),
                            signedUserId, userPublicKey)
        verifyUserResult = "Success"
    except rsa.pkcs1.VerificationError as e:
        verifyUserResult = "Failed"

    # post to blockchain
    SC_onboardPayload = [
        "Munich",
        user_id,
        signedDocHash
    ]

    sc_res = requests.post(
        "http://neo-nodes:30333/onboard", json=SC_onboardPayload)
    print("received POST result")
    print(sc_res.status_code)
    # result = sc_res.json()
    # print(result)

    res = {
        "docHash": base64.encodestring(docHash).decode("ascii"),
        "signedDocHash": signedDocHash,
        "verifyUserResult": verifyUserResult,
        # "smartContractResult": result

    }

    return json.dumps(res)


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

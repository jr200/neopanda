import json
import sys
import requests
from flask import Flask, request
from flask_cors import CORS
import rsa
import rsa.pkcs1
import base64


import binascii
import hashlib
from neo.Implementations.Wallets.peewee.UserWallet import UserWallet
from neo.Core.TX.InvocationTransaction import InvocationTransaction
from neo.Core.TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from neo.Core.CoinReference import CoinReference
from neo.SmartContract.ContractParameterContext import ContractParametersContext
from neocore.Fixed8 import Fixed8
from neocore.UInt256 import UInt256
from neocore.UInt160 import UInt160
from neocore.KeyPair import KeyPair
from neo import Blockchain
from base58 import b58decode
from neo.VM.ScriptBuilder import ScriptBuilder
from neo.Wallets.utils import to_aes_key


app = Flask(__name__)
cors = CORS(app)

VALID_DATA = 0
NO_DATA = 1
INVALID_FIELD = 2

HASH_METHOD = "SHA-512"
CONTRACT_HASH = "0xb3bcbda2439fb3129f302c33b8a17f72210f29a3"


@app.route("/")
def default():
    return "Here is nothing"


def getKeys(identity):

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


@app.route("/testNeoClient", methods=["POST", "GET"])
def testNeoClient():
    invocation_tx = InvocationTransaction()

    smartcontract_scripthash = UInt160.ParseString(CONTRACT_HASH)
    sb = ScriptBuilder()
    sb.EmitAppCallWithOperationAndArgs(
        smartcontract_scripthash,
        'onboard',
        [b'Munich', b'tai.lung@mail.com', b'xxx'])
    invocation_tx.Script = binascii.unhexlify(sb.ToArray())

    wallet = UserWallet.Create(
        'neo-privnet.wallet', to_aes_key('coz'), generate_default_key=False)
    private_key = KeyPair.PrivateKeyFromWIF(
        "KxDgvEKzgSBPPfuVfw67oPQBSjidEiqTHURKSDL1R7yGaGYAeYnr")

    wallet.CreateKey(private_key)
    context = ContractParametersContext(invocation_tx)
    wallet.Sign(context)

    invocation_tx.scripts = context.GetScripts()
    raw_tx = invocation_tx.ToArray()

    payload = {"jsonrpc": "2.0", "id": 1,
               "method": "sendrawtransaction",
               "params": [raw_tx.decode("ascii")]}

    res = requests.post(
        "http://neo-nodes:30333/testNeoConnection", json=payload)
    print("received POST result")
    print(res.status_code)
    result = res.text
    print(result)

    return json.dumps({
        "raw_tx": raw_tx.decode("ascii"),
        "result": result,
        "payload": payload,
    })


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

    issuerPrivateKeyFile = getKeys("Munich")["private"]
    with open(issuerPrivateKeyFile, 'r') as f:
        file_data = f.read()

    issuerPrivateKey = rsa.PrivateKey.load_pkcs1(file_data, "PEM")
    docHash = rsa.compute_hash(json.dumps(data).encode("utf-8"), HASH_METHOD)
    signedDocHash = rsa.sign_hash(docHash, issuerPrivateKey, HASH_METHOD)
    signedDocHash = base64.encodestring(signedDocHash).decode("ascii")

    userPublicKeyFile = getKeys(user_id)["public"]
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
    invocation_tx = InvocationTransaction()

    smartcontract_scripthash = UInt160.ParseString(CONTRACT_HASH)
    sb = ScriptBuilder()
    sb.EmitAppCallWithOperationAndArgs(
        smartcontract_scripthash,
        'onboard',
        [b"Munich", user_id.encode("utf-8"), signedDocHash.encode("utf-8")])
    invocation_tx.Script = binascii.unhexlify(sb.ToArray())

    wallet = UserWallet.Create(
        'neo-privnet.wallet', to_aes_key('coz'), generate_default_key=False)
    private_key = KeyPair.PrivateKeyFromWIF(
        "KxDgvEKzgSBPPfuVfw67oPQBSjidEiqTHURKSDL1R7yGaGYAeYnr")

    wallet.CreateKey(private_key)
    context = ContractParametersContext(invocation_tx)
    wallet.Sign(context)

    invocation_tx.scripts = context.GetScripts()
    raw_tx = invocation_tx.ToArray()

    payload = {"jsonrpc": "2.0", "id": 1,
               "method": "sendrawtransaction",
               "params": [raw_tx.decode("ascii")]}

    res = requests.post(
        "http://neo-nodes:30333/testNeoConnection", json=payload)
    print("received POST result")
    print(res.status_code)
    result = res.text
    print(result)

    res = {
        "docHash": base64.encodestring(docHash).decode("ascii"),
        "signedDocHash": signedDocHash,
        "verifyUserResult": verifyUserResult,
        "smartContractResult": result,
        "raw_tx": raw_tx.decode("ascii"),
        "payload": payload,
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

    data = request.json["data"]
    user_id = data["userId"]
    print(user_id)
    signedUserId = request.json["signedUserId"]
    signedUserId = base64.decodestring(signedUserId.encode("ascii"))

    docHash = rsa.compute_hash(json.dumps(data).encode("utf-8"), HASH_METHOD)

    issuerId = request.json["issuerId"]
    issuerPublicKeyFile = getKeys(issuerId)["public"]
    with open(issuerPublicKeyFile, 'r', encoding="ascii") as f:
        file_data = f.read()

    issuerPublicKey = rsa.PublicKey.load_pkcs1(file_data)
    try:
        verify = rsa.verify(json.dumps(data).encode(
            "utf-8"), signedUserId, issuerPublicKey)
        verifyResult = "Success"
    except rsa.pkcs1.VerificationError as e:
        verifyResult = "Failed"

    SC_getAttestation_payload = {
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            CONTRACT_HASH,
            ["getAttestation",
             [issuerId, user_id]
             ]]
    }
    SC_getAttestation_res = requests.post(
        "http://neo-nodes:30333/testNeoConnection", json=SC_getAttestation_payload)

    return json.dumps({
        "result": "X",
        "attestationRes": SC_getAttestation_res.text
    })


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

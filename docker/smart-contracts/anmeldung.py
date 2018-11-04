# build /smart-contracts/anmeldung.py test 0710 07 True False False "onboard" ["issuer", "userId", "signedHashOfDoc"]]


from boa.interop.Neo.Runtime import Log, Notify
from boa.interop.Neo.Storage import Get, Put, GetContext
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.builtins import concat


def deserialize_bytearray(data):

    collection_length_length = data[0:1]

    # get length of collection
    collection_len = data[1:collection_length_length + 1]

    # create a new collection
    new_collection = list(length=collection_len)

    # trim the length data
    offset = 1 + collection_length_length

    for i in range(0, collection_len):

        # get the data length length
        itemlen_len = data[offset:offset + 1]

        # get the length of the data
        item_len = data[offset + 1:offset + 1 + itemlen_len]

        # get the data
        item = data[offset + 1 + itemlen_len: offset +
                    1 + itemlen_len + item_len]

        # store it in collection
        new_collection[i] = item

        offset = offset + item_len + itemlen_len + 1

    return new_collection


def serialize_array(items):

    # serialize the length of the list
    itemlength = serialize_var_length_item(items)

    output = itemlength

    # now go through and append all your stuff
    for item in items:

        # get the variable length of the item
        # to be serialized
        itemlen = serialize_var_length_item(item)

        # add that indicator
        output = concat(output, itemlen)

        # now add the item
        output = concat(output, item)

    # return the stuff
    return output


def serialize_var_length_item(item):

    # get the length of your stuff
    stuff_len = len(item)

    # now we need to know how many bytes the length of the array
    # will take to store

    # this is one byte
    if stuff_len <= 255:
        byte_len = b'\x01'
    # two byte
    elif stuff_len <= 65535:
        byte_len = b'\x02'
    # hopefully 4 byte
    else:
        byte_len = b'\x04'

    out = concat(byte_len, stuff_len)

    return out


def Main(operation, args):
    print("THE operation")
    print(operation)

    if operation == 'onboard':
        issuer = args[0]
        user_id = args[1]
        attestation = args[2]

        print("THE issuer")
        print(issuer)
        print("THE userid")
        print(user_id)
        print("THE attestation")
        print(attestation)

        # if not CheckWitness(issuer):
        #     Notify("Issuer argument is not the same as the sender")
        #     return False

        issuer_user_key = concat(issuer, user_id)
        context = GetContext()
        # exists = Get(context, issuer_user_key)
        # if exists:
        #     # What should we do in this case? Overwrite the document
        #     return False

        Put(context, issuer_user_key, attestation)
        return "Success"

    elif operation == 'getAttestation':
        from_issuer = args[0]
        user_id = args[1]

        issuer_user_key = concat(from_issuer, user_id)

        print("THEissueruserkey")
        print(issuer_user_key)

        context = GetContext()
        attestation = Get(context, issuer_user_key)
        print("THEattestation")
        print(attestation)

        if not attestation or attestation == "":
            return "Failed"

        blacklist_bytes = Get(context, "blacklist")
        actual_blacklist = deserialize_bytearray(blacklist_bytes)

        print("THEactualblacklist")
        print(actual_blacklist)

        for blacklisted_attestation in actual_blacklist:
            if blacklisted_attestation == attestation:
                return "Attestation has been Revoked!"

        return attestation

    elif operation == "revokeAttestation":
        from_issuer = args[0]
        user_id = args[1]

        issuer_user_key = concat(from_issuer, user_id)
        print(issuer_user_key)

        context = GetContext()
        attestation = Get(context, issuer_user_key)
        print("ABOUTto revoke")
        print(attestation)

        blacklist_bytes = Get(context, "blacklist")
        actual_blacklist = deserialize_bytearray(blacklist_bytes)

        print("OLDblacklist")
        print(actual_blacklist)

        actual_blacklist.append(attestation)

        print("NEWblacklist")
        print(actual_blacklist)
        new_blacklist = serialize_array(actual_blacklist)

        print(new_blacklist)
        Put(context, "blacklist", new_blacklist)

        return "Success"

    return "Error: operation not recognised"

"""
Testing:

neo> build 4-domain.py test 0710 05 True False query ["test.com"]
neo> build 4-domain.py test 0710 05 True False register ["test.com","AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y"]
neo> build 4-domain.py test 0710 05 True False delete ["test.com"]
neo> build 4-domain.py test 0710 05 True False transfer ["test.com","AK2nJJpJr6o664CWJKi1QRXjqeic"]

Importing:

neo> import contract 4-domain.avm 0710 05 True False
neo> contract search ...

Using:

neo> testinvoke 5030694901a527908ab0a1494670109e7b85e3e4 query ["test.com"]
neo> testinvoke 5030694901a527908ab0a1494670109e7b85e3e4 register ["test.com","AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y"]
neo> testinvoke 5030694901a527908ab0a1494670109e7b85e3e4 delete ["test.com"]
neo> testinvoke 5030694901a527908ab0a1494670109e7b85e3e4 transfer ["test.com","AZ9Bmz6qmboZ4ry1z8p2KF3ftyA2ckJAym"]
"""
from boa.interop.Neo.Runtime import Log, Notify
from boa.interop.Neo.Storage import Get, Put, GetContext
from boa.interop.Neo.Runtime import GetTrigger,CheckWitness
from boa.builtins import concat


def Main(operation, args):
    nargs = len(args)
    if nargs == 0:
        print("No domain name supplied")
        return 0


    if oepration == "onboard":
        issuer = args[0]
        user_id = args[1]
        attestation = args[2]

        if nargs < 3:
            print("required arguments: [issuer] [userId] [signedHashOfDoc]")
            return 0

        return OnboardAttestation(issuer, user_id, attestation)

    if operation == "getAttestation":
        from_issuer = args[0]
        user_id = args[1]

        if nargs < 2:
            print("required arguments: [issuer] [userId]")
            return 0

        return GetAttestation(from_issuer, user_id)

    if operation == "revokeAttestation":
        from_issuer = args[0]
        user_id = args[1]

        if nargs < 2:
            print("required arguments: [issuer] [userId]")
            return 0

        return RevokeAttestation(from_issuer, user_id)


    if operation == "isAttestationValid":
        attestation = args[0]

        return IsAttestationVAlid(attestation)





def OnboardAttestation(issuer, user_id, attestation):
    msg = concat("Doing OnboardAttestation: [{0}] [{1}] [{2}]".format(issuer, user_id, attestation))
    Notify(msg)

    if not CheckWitness(issuer):
        Notify("Issuer argument is not the same as the sender")
        return False

    issuer_user_key = "{0}.{1}".format(issuer, user_id)
    context = GetContext()
    # exists = Get(context, issuer_user_key)
    # if exists:
    #     What should we do in this case? Overwrite the document
    #     return False

    Put(context, issuer_user_key, attestation)
    return True

def GetAttestation(from_issuer, user_id):
    msg = concat("GetAttestation: {0} {1}".format(from_issuer, user_id))
    Notify(msg)

    issuer_user_key = "{0}.{1}".format(from_issuer, user_id)
    context = GetContext()
    attestation = Get(context, issuer_user_key)

    return attestation


def RevokeAttestation(from_issuer, user_id)
    msg = concat("RevokeAttestation: ", attestation)
    Notify(msg)

    attestation = GetAttestation(from_issuer, user_id)
    context = GetContext()
    # add attestation to blacklist storage

    return True

def TransferDomain(domain_name, to_address):
    msg = concat("TransferDomain: ", domain_name)
    Notify(msg)

    context = GetContext()
    owner = Get(context, domain_name)
    if not owner:
        Notify("Domain is not yet registered")
        return False

    if not CheckWitness(owner):
        Notify("Sender is not the owner, cannot transfer")
        return False

    if not len(to_address) != 34:
        Notify("Invalid new owner address. Must be exactly 34 characters")
        return False

    Put(context, domain_name, to_address)
    return True


def DeleteDomain(domain_name):
    msg = concat("DeleteDomain: ", domain_name)
    Notify(msg)

    context = GetContext()
    owner = Get(context, domain_name)
    if not owner:
        Notify("Domain is not yet registered")
        return False

    if not CheckWitness(owner):
        Notify("Sender is not the owner, cannot transfer")
        return False

    Delete(context, domain_name)
    return True

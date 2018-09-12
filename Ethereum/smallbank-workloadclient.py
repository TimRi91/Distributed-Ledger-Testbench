import time
import os
import json
from web3 import Web3

#----------------Set Variables----------------
#Testsetrate (#requests/sec)
n = 6
maxRate = False
#Coinbase-Account
coinbasePrivateKey='private-key'
#Contract-Address
contractAddress='contract-Address'
#---------------------------------------------

#connect to localnode
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:30311", request_kwargs={'timeout': 60}))

#path to the folder of the abi-files
dir_path = ('contracts')
#get the abi from json-file
with open(str(os.path.join(dir_path,'smallbank_abi.json')),'r') as abi_definition:
    abi = json.load(abi_definition)

contract_adress = web3.toChecksumAddress(contractAddress)
# Create the contract instance with the deployed address
contract = web3.eth.contract(address = contract_adress, abi = abi)

if maxRate == True:
    #result-file
    n = 100.0
    filename = 'max-Requestrate_smallbank_'+str(time.strftime("%d-%m-%Y_%H-%M-%S"))+'.txt'
    pathname = os.path.join('results', filename)    

def updateBalance(iNonce, account, amount):
    transaction = contract.functions.updateBalance(account,amount).buildTransaction(
            {
                'nonce': iNonce,
                'gas': 100000,
                'gasPrice': web3.eth.gasPrice
            }
        )
    signed_txn = web3.eth.account.signTransaction(transaction,coinbasePrivateKey)
    #send Transaction
    web3.eth.sendRawTransaction(signed_txn.rawTransaction)

def sendPayment(iNonce, sender, receiver, amount):
    transaction = contract.functions.sendPayment(sender,receiver, amount).buildTransaction(
            {
                'nonce': iNonce,
                'gas': 100000,
                'gasPrice': web3.eth.gasPrice
            }
        )
    signed_txn = web3.eth.account.signTransaction(transaction,coinbasePrivateKey)
    #send Transaction
    web3.eth.sendRawTransaction(signed_txn.rawTransaction)

def getBalance(account):
    sValue = contract.functions.getBalance(account).call()


iNonce = web3.eth.getTransactionCount(web3.eth.coinbase)
iRate = 0
tBeginn = time.time()
tPeriode = time.time()

#Assign Tokens to A
updateBalance(iNonce, "A", 300)
iNonce = iNonce + 1
#Assign Tokens to B
updateBalance(iNonce, "B", 300)
iNonce = iNonce + 1

while True:
    if time.time()-tBeginn <  320:

        #Send Token from A to B
        tStart = time.time()
        sendPayment(iNonce, "A", "B", 10)
        iRate = iRate + 1
        iNonce = iNonce + 1
        tDelay = time.time()-tStart
        if(1/n)-tDelay > 0:
            time.sleep((1/n)-tDelay)

        #get Balance from B
        tStart = time.time()
        getBalance("B")
        iRate = iRate + 1
        tDelay = time.time()-tStart
        if(1/n)-tDelay > 0:
            time.sleep((1/n)-tDelay)
   
        if time.time()-tPeriode > 1.0:
            print('Requestrate: ', iRate)
            if maxRate == True:
                #write Rate into file
                with open(pathname, "a") as file:
                    file.write(str(iRate) + ' #req/sec \n')
                file.close()   
            tPeriode = time.time()
            iRate = 0

        #Send Token from B to A
        tStart = time.time()
        sendPayment(iNonce, "B", "A", 10)
        iRate = iRate + 1
        iNonce = iNonce + 1
        tDelay = time.time()-tStart
        if(1/n)-tDelay > 0:
            time.sleep((1/n)-tDelay)

        #get Balance from A
        tStart = time.time()
        getBalance("A")
        iRate = iRate + 1
        tDelay = time.time()-tStart
        if(1/n)-tDelay > 0:
            time.sleep((1/n)-tDelay)
   
        if time.time()-tPeriode > 1.0:
            print('Requestrate: ', iRate)
            if maxRate == True:
                #write Rate into file
                with open(pathname, "a") as file:
                    file.write(str(iRate) + ' #req/sec \n')
                file.close()   
            tPeriode = time.time()
            iRate = 0
    else:
        break

print('Measurement finished')

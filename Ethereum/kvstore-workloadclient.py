import time
import os
import json

#Set Web3 Provider to connect to Ethereum-Network
from web3 import Web3
#connect to localnode
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:30311"))

#----------------Set Variables----------------
#Testsetrate (#requests/sec)
n = 6
#Node
node = 'localnode'
#Coinbase-Account
coinbasePrivateKey='private-key'
#Contract-Address
contractAddress='contract-Address'
#---------------------------------------------

#path to the folder of the abi-files
dir_path = ('contracts')
#get the abi from json-file
with open(str(os.path.join(dir_path,'kvstore_abi.json')),'r') as abi_definition:
    abi = json.load(abi_definition)

contract_adress = web3.toChecksumAddress(contractAddress)
# Create the contract instance with the deployed address
contract = web3.eth.contract(address = contract_adress, abi = abi)

iNonce = web3.eth.getTransactionCount(web3.eth.coinbase)
#Thread-Instances
sKey = node
sVal = node
iRate = 0
tBeginn = time.time()
tPeriode = time.time()

while True:
    if time.time()-tBeginn <  320:

        tDelay = time.time()
        #set-function: string Key, string Value
        transaction = contract.functions.set(sKey,sVal).buildTransaction(
                {
                    'nonce': iNonce,
                    'gas': 100000,
                    'gasPrice': web3.eth.gasPrice
                }
            )
        signed_txn = web3.eth.account.signTransaction(transaction,coinbasePrivateKey)
        #send Transaction
        web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        iRate = iRate + 1
        iNonce = iNonce + 1
        tDelay = time.time()-tDelay
        if(1/n)-tDelay > 0:
            time.sleep((1/n)-tDelay)

        #get-function: string Key
        tDelay = time.time()
        contract.functions.get(sKey).call()
        iRate = iRate + 1

        if time.time()-tPeriode > 1.0:
            print('Requestrate: ', iRate) 
            tPeriode = time.time()
            iRate = 0

        tDelay = time.time()-tDelay
        if(1/n)-tDelay > 0:
            time.sleep((1/n)-tDelay)
    else:
        break

print('Workload done')

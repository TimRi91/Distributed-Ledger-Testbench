import time
import os
import json
from web3 import Web3

#----------------Set Variables----------------
#Testsetrate (#requests/sec)
n = 6
#Node
node = 'localnode'
#Coinbase-Account
coinbasePrivateKey='private-key'
#Contract-Address
contractAddress= 'contract-Address'
#---------------------------------------------

#connect to node
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:30311", request_kwargs={'timeout': 60}))
#Contract
contract_adress = web3.toChecksumAddress(contractAddress)
#result-file
filename = 'KVstore_Latency_Testsetrate'+str(n)+'_'+str(time.strftime("%d-%m-%Y_%H-%M-%S"))+'.txt'
pathname = os.path.join('results', filename)    
   
#path to the folder of the abi-files
dir_path = ('contracts')
#get the abi from json-file
with open(str(os.path.join(dir_path,'kvstore_abi.json')),'r') as abi_definition:
    abi = json.load(abi_definition)

# Create the contract instance with the deployed address
contract = web3.eth.contract(address = contract_adress, abi = abi)
# Getting transaction-history
iNonce = web3.eth.getTransactionCount(web3.eth.coinbase)
#start-time of measurement periode
tBegin = time.time()

#write Operation
def setTrans(iNonce):
    print('send Set')
    #keyvalue and value for write operation
    sKey = node
    sVal = node
    #-------------------------------------------------------------------------------------
    #start-time for latency-periode
    tStart =  time.time()
    #set-function: string Key, string Value
    transaction = contract.functions.set(sKey,sVal).buildTransaction(
            {
                'nonce': iNonce,
                'gas': 100000,
                'gasPrice': web3.eth.gasPrice
            }
        )
    signed_txn = web3.eth.account.signTransaction(transaction, coinbasePrivateKey)
    #send Transaction
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    #wait until key and value are stored
    web3.eth.waitForTransactionReceipt(tx_hash)
    #end-time for latency-periode
    tEnd = time.time()
    #-------------------------------------------------------------------------------------
    #Calculate Latency between send_time and receive_time
    tResult = tEnd - tStart
    return tResult

#read Operation
def getCall():
    print('send Get')
    #keyvalue for read operation
    sKey = node
    #-------------------------------------------------------------------------------------
    #start-time for latency-periode
    tStart =  time.time()
    #get-function: string Key
    sValue = contract.functions.get(sKey).call()
    #end-time for latency-periode
    tEnd = time.time()
    #-------------------------------------------------------------------------------------
    #Calculate Latency between send_time and receive_time
    tResult = tEnd - tStart
    return tResult

while True:
    if time.time()-tBegin <  300:
        #measure latency for write-operation
        writeLatency = setTrans(iNonce)
        iNonce = iNonce + 1
        #print writeLatency to console
        print("Latency (write):",writeLatency, "Seconds")
        #measure latency for read-operation
        readLatency = getCall()
        #print readLatency to console
        print("Latency (read):",readLatency, "Seconds")
        #write Lantency-value into file
        with open(pathname, "a") as file:
            file.write(str(writeLatency) + ' (write)sec \n')
            file.write(str(readLatency) + ' (read)sec \n')
        file.close()    
    else:
        break

print('Measurement finished')

 

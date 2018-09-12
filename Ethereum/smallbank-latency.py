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
contractAddress = 'contract-address'
#---------------------------------------------

#connect to localnode
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:30311", request_kwargs={'timeout': 60}))

#result-file
filename = 'Smallbank_Latency_Testsetrate'+str(n)+'_'+str(time.strftime("%d-%m-%Y_%H-%M-%S"))+'.txt'
pathname = os.path.join('results', filename)    
   
#path to the folder of the abi-files
dir_path = ('contracts')
#get the abi from json-file
with open(str(os.path.join(dir_path,'smallbank_abi.json')),'r') as abi_definition:
    abi = json.load(abi_definition)
#Contract
contract_adress = web3.toChecksumAddress(contractAddress)
# Create the contract instance with the deployed address
contract = web3.eth.contract(address = contract_adress, abi = abi)


#write Operation
def updateBalance(iNonce, account, amount):

    #-------------------------------------------------------------------------------------
    #start-time for latency-periode
    tStart =  time.time()
    transaction = contract.functions.updateBalance(account,amount).buildTransaction(
            {
                'nonce': iNonce,
                'gas': 100000,
                'gasPrice': web3.eth.gasPrice
            }
        )
    signed_txn = web3.eth.account.signTransaction(transaction,coinbasePrivateKey)
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

#write Operation
def sendPayment(iNonce, sender, receiver, amount):

    #-------------------------------------------------------------------------------------
    #start-time for latency-periode
    tStart =  time.time()
    transaction = contract.functions.sendPayment(sender,receiver, amount).buildTransaction(
            {
                'nonce': iNonce,
                'gas': 100000,
                'gasPrice': web3.eth.gasPrice
            }
        )
    signed_txn = web3.eth.account.signTransaction(transaction,coinbasePrivateKey)
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
def getBalance(account):

    #-------------------------------------------------------------------------------------
    #start-time for latency-periode
    tStart =  time.time()
    #get-function: string Key
    sValue = contract.functions.getBalance(account).call()
    #end-time for latency-periode
    tEnd = time.time()
    #-------------------------------------------------------------------------------------
    #Calculate Latency between send_time and receive_time
    tResult = tEnd - tStart
    return tResult

# Getting transaction-history
iNonce = web3.eth.getTransactionCount(web3.eth.coinbase)
#start-time of measurement periode
tBegin = time.time()
iCounter = 0

#Assign Tokens to A
updateBalance(iNonce, "A", 300)
iNonce = iNonce + 1
#Assign Tokens to B
updateBalance(iNonce, "B", 300)
iNonce = iNonce + 1

while True:
    if time.time()-tBegin <  300:
        if iCounter % 2 == 0:
            #measure latency for write-operation
            writeLatency = sendPayment(iNonce, "A", "B", 10)
            iNonce = iNonce + 1
            #print writeLatency to console
            print("Latency (write):",writeLatency, "Seconds")
            #measure latency for read-operation
            readLatency = getBalance("B")
            #print readLatency to console
            print("Latency (read):",readLatency, "Seconds")
            #write Lantency-value into file
            with open(pathname, "a") as file:
                file.write(str(writeLatency) + ' (write)sec \n')
                file.write(str(readLatency) + ' (read)sec \n')
            file.close()  
        else:
            #measure latency for write-operation
            writeLatency = sendPayment(iNonce, "B", "A", 10)
            iNonce = iNonce + 1
            #print writeLatency to console
            print("Latency (write):",writeLatency, "Seconds")
            #measure latency for read-operation
            readLatency = getBalance("A")
            #print readLatency to console
            print("Latency (read):",readLatency, "Seconds")
            #write Lantency-value into file
            with open(pathname, "a") as file:
                file.write(str(writeLatency) + ' (write)sec \n')
                file.write(str(readLatency) + ' (read)sec \n')
            file.close()  
        iCounter = iCounter + 1
    else:
        break

print('Measurement finished')

 

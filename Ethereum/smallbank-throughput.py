import os
import time
from web3 import Web3

#----------------Set Variables----------------
#Testsetrate (#requests/sec)
n = 6
#Node
node = 'localnode'
#---------------------------------------------


#create .txt-file
filename = 'Smallbank_Throughput_Testset'+str(n)+'_'+str(time.strftime("%d-%m-%Y_%H-%M-%S"))+'.txt'
pathname = os.path.join('results', filename)
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:30311", request_kwargs={'timeout': 60}))
    
tBeginn=time.time()
while True:
    if time.time()-tBeginn <  300:
        iRate = 0

        iStart=web3.eth.blockNumber
        time.sleep(1.0 - ((time.time() - tBeginn) % 1.0))
        iResult = web3.eth.blockNumber - iStart
        
        for x in range(iResult):
            iRate = iRate + web3.eth.getBlockTransactionCount(iStart+x+1)
            
        print ('#tx/sec: ' + str(iRate))

        with open(pathname, "a") as file:
            file.write(str(iRate) + ' #tx/s \n')
        file.close()    
    else:
        break

print('Measurement finished')

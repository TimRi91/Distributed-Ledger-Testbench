"""
Testbench-Script for measuring Throughput of the NEO-Blockchain
Testcase: Smallbank

"""
import os
import threading
import time
from time import sleep

from logzero import logger
from twisted.internet import reactor, task

from neo.Implementations.Wallets.peewee.UserWallet import UserWallet
from neo.Prompt.Commands.Wallet import ImportToken
from neo.Wallets.utils import to_aes_key
from neo.contrib.smartcontract import SmartContract
from neo.Network.NodeLeader import NodeLeader
from neo.Core.Blockchain import Blockchain
from neo.Core.Block import Block
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Settings import settings
from neocore.Cryptography.Crypto import Crypto
from neocore.Fixed8 import Fixed8
from neo.Prompt.Commands.LoadSmartContract import LoadContract, GatherContractDetails, ImportContractAddr, ImportMultiSigContractAddr, generate_deploy_script
from neo.Prompt.Commands.Invoke import InvokeContract, TestInvokeContract, test_invoke
from twisted.internet import reactor, task

#-----------------------------------------------------
#Testsetrate (#requests/sec)
n = 6

# Setup the smart contract instance
smart_contract_addr = 'c30a188c203011720b4880d20cfe6d1bce3ba7f6'                        
wallet_path  = 'wallet.db3'
wallet_pass = 'wallepw'
#-----------------------------------------------------

class neoBench ():
    def __init__(self, walletpath, walletpw):
        self.walletpath = walletpath
        self.walletpw = walletpw
        self.Wallet = None
    
    def openWallet(self):
        """ open a Wallet. Needed for invoking contract methods """
        if not os.path.exists(self.walletpath):
            logger.info("Wallet file not found")
            return
        else:
            assert self.Wallet is None
            aespasswd = to_aes_key(self.walletpw)
            self.Wallet = UserWallet.Open(self.walletpath, aespasswd)
            print("Opened wallet at: ", self.walletpath)

            self.wallet_sh = self.Wallet.GetStandardAddress()
            self.wallet_addr = Crypto.ToAddress(self.wallet_sh)

            print('Wallet Sh', self.wallet_sh)
            print('Wallet Addr', self.wallet_addr)

            self.Wallet.Rebuild()

            print("Wallet is syncing...")
            while self.Wallet.IsSynced is False:
                self._walletdb_loop = task.LoopingCall(self.Wallet.ProcessBlocks)
                self._walletdb_loop.start(1)
                print(self.Wallet._current_height,"/",Blockchain.Default().Height)

            logger.info("Wallet %s opened", self.walletpath)

    def invokeMethod(self, args):
        """  Invoke a method of the Smart Contract """
        
        if self.Wallet.IsSynced is False:
            raise Exception("Wallet is not synced.")

        tx, fee, results, num_ops = TestInvokeContract(self.Wallet, args)
        if not tx: 
            raise Exception("TestInvokeContract failed")

        logger.info("TestInvokeContract done, calling InvokeContract now...")
        #tStart = time.time()
        fee = Fixed8.Zero()
        sent_tx = InvokeContract(self.Wallet, tx, fee)

        if sent_tx:
            logger.info("InvokeContract success, transaction underway: %s" %sent_tx.Hash.ToString())

def custom_background_code():
    """
    This function is run in a daemonized thread, which means it can be instantly killed at any
    moment, whenever the main thread quits. If you need more safety, don't use a  daemonized
    thread and handle exiting this thread in another way (eg. with signals and events).
    """
    while Blockchain.Default().HeaderHeight - Blockchain.Default().Height > 2:
        print("\rBlockchain: {}/{}".format(Blockchain.Default().Height, Blockchain.Default().HeaderHeight), end='')
        sleep(1)

    #results in .txt-file
    filename = 'KVstore_Throughput_Testset'+str(n)+'_'+str(time.strftime("%d-%m-%Y_%H-%M-%S"))+'.txt'
    pathname = os.path.join('results', filename)


    #provision Testbench
    nb = neoBench(wallet_path, wallet_pass)
    nb.openWallet()
    
    tBeginn=time.time()
    while True:
        if time.time()-tBeginn <  300:
            iThroughput = 0

            #capture confirmed blocks per second
            iStart=Blockchain.Default().Height
            time.sleep(1.0 - ((time.time() - tBeginn) % 1.0))
            iResult = Blockchain.Default().Height - iStart

            #Get total amount of transactions in confirmed blocks
            if iResult != 0:
                for x in range(iResult):
                    block = Blockchain.Default().GetBlock(iStart+x+1)
                    iThroughput = iThroughput + len(block.FullTransactions)
            
            #print Throughput-value to console   
            print ('#tx/sec: ' + str(iThroughput))

            #write Throughput-value into file
            with open(pathname, "a") as file:
                file.write(str(iThroughput) + ' #tx/s \n')
            file.close()    
        else:
            break
    print('Measurement finished')

def main():
    # Use PrivateNet
    settings.setup_privnet()

    # Setup the blockchain
    blockchain = LevelDBBlockchain(settings.chain_leveldb_path)
    Blockchain.RegisterBlockchain(blockchain)
    dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
    dbloop.start(.1)
    NodeLeader.Instance().Start()

    # Disable smart contract events for external smart contracts
    settings.set_log_smart_contract_events(False)

    # Start a thread with custom code
    d = threading.Thread(target=custom_background_code)
    d.setDaemon(True)  # daemonizing the thread will kill it when the main thread is quit
    d.start()

    # Run all the things (blocking call)
    logger.info("Everything setup and running. Waiting for events...")
    reactor.run()
    logger.info("Shutting down.")


if __name__ == "__main__":
    main()

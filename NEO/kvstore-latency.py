"""
Testbench-Script for measuring Latency of the NEO-Blockchain
Testcase: YCSB

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
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Settings import settings
from neocore.Cryptography.Crypto import Crypto
from neo.Prompt.Commands.LoadSmartContract import LoadContract, GatherContractDetails, ImportContractAddr, ImportMultiSigContractAddr, generate_deploy_script
from neo.Prompt.Commands.Invoke import InvokeContract, TestInvokeContract, test_invoke
from twisted.internet import reactor, task

#Testsetrate (#requests/sec)
testset = 6

# Setup the smart contract instance
smart_contract_addr = 'a19b97b9fde577812722573eab5c0f1c635a588c'                        
wallet_path  = 'dltwallet.db3'
wallet_pass = 'password'

class neoBench:
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
                #sleep(1)
            return len(self.Wallet.GetTransactions())

    def invokeMethod(self, args):
        """  Invoke a method of the Smart Contract """
        
        if self.Wallet.IsSynced is False:
            raise Exception("Wallet is not synced.")

        tx, fee, results, num_ops = TestInvokeContract(self.Wallet, args)
        if not tx: 
            raise Exception("TestInvokeContract failed")

        logger.info("TestInvokeContract done, calling InvokeContract now...")
        tStart = time.time()
        sent_tx = InvokeContract(self.Wallet, tx, fee)

        if sent_tx:
            logger.info("InvokeContract success, transaction underway: %s" %sent_tx.Hash.ToString())

            found = self._wait_for_tx(sent_tx)
            if found:
                tResult = time.time() - tStart
                logger.info("transaction done")
                logger.info("Tx Latency: %s", tResult)

                #wait one additional block for the UTXO to be returned
                self.currentHeight = Blockchain.Default().HeaderHeight
                while True:
                    if self.Wallet.WalletHeight == self.currentHeight + 1:
                        break

                return tResult

    def _wait_for_tx(self, tx):
        """ Wait for tx to show up on blockchain """
        while True:
            _tx, height = Blockchain.Default().GetTransaction(tx.Hash.ToString())
            if height > -1:
                return True
            sleep(1)


def custom_background_code():
    """
    This function is run in a daemonized thread, which means it can be instantly killed at any
    moment, whenever the main thread quits. If you need more safety, don't use a  daemonized
    thread and handle exiting this thread in another way (eg. with signals and events).
    """
    while Blockchain.Default().HeaderHeight - Blockchain.Default().Height > 2:
        print("\rBlockchain: {}/{}".format(Blockchain.Default().Height, Blockchain.Default().HeaderHeight), end='')
        sleep(1)

    #result-file
    filename = 'KVstore_Latency_Testsetrate'+str(testset)+'_'+str(time.strftime("%d-%m-%Y_%H-%M-%S"))+'.txt'
    pathname = os.path.join('results', filename)  

    #Smart Contract provision
    nb = neoBench(wallet_path, wallet_pass)
    iNonce = nb.openWallet()
    iNonce = iNonce + 1

    tBegin = time.time()
    while True:
        if time.time()-tBegin <  300:
            #measure latency for write-operation
            writeLatency = nb.invokeMethod([smart_contract_addr, 0, ["1","Tim", iNonce]])
            iNonce = iNonce + 1
            #print writeLatency to console
            print("Latency (write):",writeLatency, "Seconds")
            #measure latency for read-operation
            readLatency = nb.invokeMethod([smart_contract_addr, 1, ["1", iNonce]])
            iNonce = iNonce + 1
            #print readLatency to console
            print("Latency (read):",readLatency, "Seconds")
            #write Lantency-value into file
            with open(pathname, "a") as file:
                 file.write(str(writeLatency) + ' (write)sec \n')
                 file.write(str(readLatency) + ' (read)sec \n')
            file.close()
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

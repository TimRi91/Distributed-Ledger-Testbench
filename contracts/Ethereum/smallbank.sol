pragma solidity ^0.4.0;

contract SmallBank {
       
    //accumulate interest on funds you’ve saved for future needs
    mapping(string=>uint) savingStore;
    //easy access to your money for your daily transactional needs
    mapping(string=>uint) checkingStore;

    function getBalance(string arg0) public constant returns (uint balance) {
        uint bal1 = savingStore[arg0];
        uint bal2 = checkingStore[arg0];
        
        balance = bal1 + bal2;
        return balance;
    }
    
    function updateBalance(string arg0, uint arg1) public {
        uint bal1 = checkingStore[arg0];
        uint bal2 = arg1;
        
        checkingStore[arg0] = bal1 + bal2;
    }
    
    function updateSaving(string arg0, uint arg1) public {
        uint bal1 = savingStore[arg0];
        uint bal2 = arg1;
        
        savingStore[arg0] = bal1 + bal2;
    }
    
    function sendPayment(string arg0, string arg1, uint arg2) public {
        uint bal1 = checkingStore[arg0];
        uint bal2 = checkingStore[arg1];
        uint amount = arg2;
        
        bal1 -= amount;
        bal2 += amount;
        
        checkingStore[arg0] = bal1;
        checkingStore[arg1] = bal2;
    }
}

from boa.interop.Neo.Storage import GetContext, Get, Put, Delete

def Main(method, *arr):
    context = GetContext()

    #updateBalance
    #arr[Account, amount]
    if method == 0:
        Put(context, arr[0], arr[1])
        return "BalanceUpdated"

    #getBalance
    #arr[Account]
    if method == 1:
        val = Get(context, arr[0])
        return val

    #sendPayment
    #arr[SenderAccount, ReceiverAccount, amount]
    if method == 2:
        bal1 = Get(context, arr[0])
        bal2 = Get(context, arr[1])
        amount = arr[2]
        bal1 -= amount
        bal2 += amount
        Put(context, arr[0], bal1)
        Put(context, arr[1], bal2)
        return "PaymentSend"

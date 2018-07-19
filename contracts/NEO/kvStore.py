from boa.interop.Neo.Storage import GetContext, Get, Put, Delete

def Main(method, *arr):
    context = GetContext()
    #method = 0: Set-Key-Value-Pair
    if method == 0:
        Put(context, arr[0], arr[1])
        return "Stored"
    #method = 1: Get-Value
    if method == 1:
        val = Get(context, arr[0])
        print(val)
        return val
    #method = 2: Delet-Key-Value-Pair
    if method == 2:
        val = Get(context, arr[0])
        Delete(context, arr[0])
        return "Deleted"

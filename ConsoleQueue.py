"""
ConsoleQueue.py

Required to get around tkInter 'main thread is not in mainloop errors

"""
Q=[]

def console_println(*args):
    global Q
    msg= "".join(map(str, args))
    Q.append(msg+"\n")

def console_print( *args):
    global Q
    msg = "".join(map(str, args))
    Q.append(msg)


def console_getEntries():
    global Q
    queued=Q
    Q=[]
    return queued






def tricky_loop(p):
    i = 0
    while True:
        if len(p) == 0:
            break
        else:
            if p[-1] == 0:
                p.pop() # assume pop is a constant time operation
            else:
                p[-1] = 0
        print i
        i = i + 1
    return 101

tricky_loop([1,2,3,4,5,6])

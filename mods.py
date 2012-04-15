p = [0,3,33]

def prc(pr):
    q = []
    while pr:
        q.append(pr.pop());
    while q:
        p.append(q.pop());

prc(p)
print p

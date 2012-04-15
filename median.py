def bigger(a,b):
    if a > b:
        return a
    else:
        return b
        
def biggest(a,b,c):
    return bigger(a,bigger(b,c))

def hhj(a,b,c):
    if a>=b:
        if a<=c:
            return a;
    if b>=a:
        if b<=c:
            return b;
    if c>=a:
        if c<=b:
            return c;
    if a>=c:
        if a<=b:
            return a;
    if b>=c:
        if b<=a:
            return b;
    if c>=b:
        if c<=a:
            return c;
    
print hhj(2,0,1)
    

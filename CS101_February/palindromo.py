def palin(str):
    if len(str) < 2:
        return True
    else:
        if str[0] == str[len(str)-1]:
            return palin( str[1:len(str)-1] )
        else:
            return False

print palin("abba");

def find_last(str1, strFn):
    pos = str1.find(strFn);
    val = pos
    while pos != -1 :
        pos = str1.find( strFn, pos+1);
        if pos != -1:
            val = pos
    return val;

print find_last('bbbbbb','a')

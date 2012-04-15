def find_last(str1, strFn):
    sec = str1.find(strFn);
    while sec != -1:
        prim = str1.find(strFn);
        sec = str1.find( strFn, prim+1);
    
    return sec;


print find_last('aaaa','a')

def table(n):
    i = 1;
    j = 1;
    while i<=n:
        while j<=n:
            print str(i) + "*" + str(j) + "=" + str(i*j)
            j = j + 1;
        i = i + 1;
        j = 1;

table(10)

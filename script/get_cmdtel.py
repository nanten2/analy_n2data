import numpy

def get_radec(path):
    f = open(path)
    d = f.readlines()
    f.close()
    dd = list(map(lambda x:x.split("#"), d))
    dd = numpy.array(dd)
    new_x = []
    new_y = []
    new_t = []
    ra1 = dd.T[0].astype(numpy.float64)
    ra2 = dd.T[1].astype(numpy.float64)
    dec1 = dd.T[2].astype(numpy.float64)
    dec2 = dd.T[3].astype(numpy.float64)
    time1 = dd.T[4].astype(numpy.float64)
    time2 = dd.T[5].astype(numpy.float64)
    for i,j,k,l,m,n in zip(ra1, ra2, dec1, dec2, time1, time2):
        if i == j and k == l:#onepoint
            new_x.append(i)
            new_y.append(k)
            new_t.append(m)
            pass
        else:#scan
            new_x.append(i)
            new_x.append(j)
            new_y.append(k)
            new_y.append(l)
            new_t.append(m)
            new_t.append(n)
    return new_x, new_y, new_t

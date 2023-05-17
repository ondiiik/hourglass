def dominates(v):
    a = abs(v[0]), abs(v[1]), abs(v[2])
    i = a.index(max(a))
    return i, 1 - 2 * (v[i] < 0)

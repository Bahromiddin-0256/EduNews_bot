def f(x): 
    return 2 * x + 1

def g(x): 
    return f(x // 2)

def h(x):   
    if x % 2 == 0: 
        return f(x + g(x))   
    else:   
        return f(x) - g(x)

def ct(x):
    print(h(x))
    print(h(x + 1))

print(ct(5))

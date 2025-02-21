_tables_initialized = False  # Private variable

gf_exp = [0] * 512
gf_log = [0] * 256

def init_tables(prim=0x11d):
    '''Precompute the logarithm and anti-log tables for faster computation later, using the provided primitive polynomial.'''
    # prim is the primitive (binary) polynomial. Since it's a polynomial in the binary sense,
    # it's only in fact a single galois field value between 0 and 255, and not a list of gf values.
    global gf_exp, gf_log
    global _tables_initialized
    gf_exp = [0] * 512 # anti-log (exponential) table
    gf_log = [0] * 256 # log table
    # For each possible value in the galois field 2^8, we will pre-compute the logarithm and anti-logarithm (exponential) of this value
    x = 1
    for i in range(0, 255):
        gf_exp[i] = x # compute anti-log for this value and store it in a table
        gf_log[x] = i # compute log at the same time
        x <<= 1

        if (x & (1 << 8)):
            x ^= prim
    # Optimization: double the size of the anti-log table so that we don't need to mod 255 to
    # stay inside the bounds (because we will mainly use this table for the multiplication of two GF numbers, no more).
    for i in range(255, 509):
        gf_exp[i] = gf_exp[i - 255]

    _tables_initialized = True
    return [gf_log, gf_exp]

def gf_add(x, y):
    return x ^ y

def gf_sub(x, y):
    return x ^ y # in binary galois field, subtraction is just the same as addition (since we mod 2)

def gf_mul(x,y):
    if x==0 or y==0:
        return 0
    if not _tables_initialized:
        init_tables()
    return gf_exp[gf_log[x] + gf_log[y]] # should be gf_exp[(gf_log[x]+gf_log[y])%255] if gf_exp wasn't oversized

def gf_div(x,y):
    if y==0:
        print(f"Slow down that's not allowed. We're in Number Theory not Calculus for God's sake.")
    if x==0:
        return 0
    return gf_exp[(gf_log[x] - gf_log[y]) % 255] # In python the remainder operator returns a non-negative int, in C you should add 255 before reducing.

def gf_pow(x, power):
    return gf_exp[(gf_log[x] * power) % 255]

def gf_inverse(x):
    return gf_exp[255 - gf_log[x]] # gf_inverse(x) == gf_div(1, x)


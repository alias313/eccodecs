gf_exp = [0] * 512
gf_log = [0] * 256

def gf_mult_noLUT(x, y, prim=0, field_charac_full=256, carryless=True):
    '''Galois Field integer multiplication using Russian Peasant Multiplication algorithm (faster than the standard multiplication + modular reduction).
    If prim is 0 and carryless=False, then the function produces the result for a standard integers multiplication (no carry-less arithmetics nor modular reduction).'''
    r = 0
    while y: # while y is above 0
        if y & 1: r = r ^ x if carryless else r + x # y is odd, then add the corresponding x to r (the sum of all x's corresponding to odd y's will give the final product). Note that since we're in GF(2), the addition is in fact an XOR (very important because in GF(2) the multiplication and additions are carry-less, thus it changes the result!).
        y = y >> 1 # equivalent to y // 2
        x = x << 1 # equivalent to x*2
        if prim > 0 and x & field_charac_full: x = x ^ prim # GF modulo: if x >= 256 then apply modular reduction using the primitive polynomial (we just subtract, but since the primitive number can be above 256 then we directly XOR).

    return r

def test_multiplicative_cycle(prim, generator):
    """
    Starting from 1, repeatedly multiply by the candidate generator using GF multiplication.
    Return the list of generated nonzero field elements.
    For a field defined by a primitive polynomial, if 'generator' is primitive then
    this should yield a cycle of 255 unique elements.
    """
    cycle = []
    current = 1
    for _ in range(255):  # There are 255 nonzero elements in GF(2^8)
        cycle.append(current)
        current = gf_mult_noLUT(current, generator, prim)
    return cycle


def find_best_generator(prim):
    """
    Try candidate generators from 2 to 255 (skipping 0 and 1) and return the one with the
    largest multiplicative cycle length.
    """
    best_gen = None
    best_cycle_len = 0
    for gen in range(2, 256):
        cycle = test_multiplicative_cycle(prim, gen)
        cycle_len = len(set(cycle))
        if cycle_len > best_cycle_len:
            best_cycle_len = cycle_len
            best_gen = gen
    return best_gen, best_cycle_len

def init_tables(prim=0x11d):
    '''Precompute the logarithm and anti-log tables for faster computation later, using the provided primitive polynomial.'''
    # prim is the primitive (binary) polynomial. Since it's a polynomial in the binary sense,
    # it's only in fact a single galois field value between 0 and 255, and not a list of gf values.
    global gf_exp, gf_log
    gf_exp = [0] * 512 # anti-log (exponential) table
    gf_log = [0] * 256 # log table

    gen, cycle_len = find_best_generator(prim)
    
    if (cycle_len != 255):
        print(f"{prim} is not a primitive polynomial for GF(2^8)")
        return

    # For each possible value in the galois field 2^8, we will pre-compute the logarithm and anti-logarithm (exponential) of this value
    x = 1
    for i in range(0, 255):
        gf_exp[i] = x # compute anti-log for this value and store it in a table
        gf_log[x] = i # compute log at the same time
        if gen == 2:
            x <<= 1
        else:
            x = gf_mult_noLUT(x, gen, prim) 

        if (x & (1 << 8)):
                x ^= prim
    # Optimization: double the size of the anti-log table so that we don't need to mod 255 to
    # stay inside the bounds (because we will mainly use this table for the multiplication of two GF numbers, no more).
    for i in range(255, 509):
        gf_exp[i] = gf_exp[i - 255]

    return [gf_log, gf_exp]

def gf_add(x, y):
    return x ^ y

def gf_sub(x, y):
    return x ^ y # in binary galois field, subtraction is just the same as addition (since we mod 2)

def gf_mul(x,y):
    if x==0 or y==0:
        return 0
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


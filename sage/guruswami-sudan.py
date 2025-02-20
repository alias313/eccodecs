from sage.all import *

F = GF(Integer(59))
n, k = Integer(40), Integer(12)
C = codes.GeneralizedReedSolomonCode(F.list()[:n], k)
D = codes.decoders.GRSBerlekampWelchDecoder(C)
print(D)

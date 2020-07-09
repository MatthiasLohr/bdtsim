# flake8: noqa
from ecdsa import SigningKey,SECP256k1
from hashlib import sha1

n  = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

def buildHashInt(x):
    h = sha1()
    h.update(x)
    return toInt(h.hexdigest())

def toInt(x):
    return int(x,16)
# modular multiplicative inverse (requires that n is prime)
def modinv(x, n=n):
    return pow(x, n-2, n)

# the two k candidates which aren't just negations of themselves
def k_candidates(s1, z1, s2, z2, n=n):
    z1_z2 = z1 - z2
    yield z1_z2 * modinv(s1 - s2, n) % n
    yield z1_z2 * modinv(s1 + s2, n) % n

# generates two tuples, each with (privkey, k_possibility_1, k_possibility_2)
def privkey_k_candidates(r, s1, z1, s2, z2, n=n):
    modinv_r = modinv(r, n)
    for k in k_candidates(s1, z1, s2, z2, n):
        yield (s1 * k - z1) * modinv_r % n,  k,  -k % n

sk = SigningKey.generate(curve=SECP256k1) #private key
vk = sk.verifying_key      #public key
print("public key x=",vk.pubkey.point.x())
print("public key y=",vk.pubkey.point.y())

print("private key number =",int(sk.to_string().hex(),16))

m1 = b"message"
m2 = b"arsch"
z1 = buildHashInt(m1)
z2 = buildHashInt(m2)

print("z1=",z1)
print("z2=",z2)
signature = sk.sign(m1,k=2,hashfunc=sha1)
r = toInt(signature[:32].hex())
s1 = toInt(signature[32:].hex())
print("r =",r)
print("s1=",s1)
assert vk.verify(signature, m1,hashfunc=sha1)
signature2 = sk.sign(m2,k=2,hashfunc=sha1)
s2 = toInt(signature2[32:].hex())
print("s2=",s2)
assert vk.verify(signature2, m2,hashfunc=sha1)

k = (z1 - z2) * modinv(s1 - s2) % n ; print('k = {:x}'.format(k))
print('privkey = {:x}'.format( (s1 * k - z1) * modinv(r) % n ))  # these two should
print('privkey = {:x}'.format( (s2 * k - z2) * modinv(r) % n ))  # be the same
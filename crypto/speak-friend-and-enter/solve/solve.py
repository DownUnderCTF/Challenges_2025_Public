
from pwn import * 
from Crypto.Hash import CMAC, SHA512
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Util.number import long_to_bytes, bytes_to_long, isPrime, inverse
from Crypto.Util.strxor import strxor
from binascii import hexlify, unhexlify
import random, json, string
import math 
import argparse


# From OSINT
NIST_SP_800_38B_AppD1 = unhexlify("2b7e151628aed2a6abf7158809cf4f3c")
# From server.py
server_cmac_publickey = unhexlify('9d4dfd27cb483aa0cf623e43ff3d3432')

#from cryptodome source
def _shift_bytes(bs, xor_lsb=0):
    num = (bytes_to_long(bs) << 1) ^ xor_lsb
    return long_to_bytes(num, len(bs))[-len(bs):]

def forge_mac(secret, target_mac, prefix):
	if len(prefix) %16 !=0:
		print("input len must be multiple of blocksize (16)")
		return None
	#calculate mac up to last block 
	mi = b'\x00'*16
	a = AES.new(secret, mode = AES.MODE_ECB)
	for i in range(0, len(prefix)//16):
		mi = a.encrypt(strxor(mi, prefix[i*16: (i+1)*16]))
		#print(i,mi)
	#calculate subkeys 
	k0 = a.encrypt(b'\x00'*16)
	C = 0x87
	if (k0[0]&0x80) == 0 : #msb(k0) == 0
		k1 = _shift_bytes(k0)
	else:
		k1 = _shift_bytes(k0, xor_lsb=C)
	if (k1[0]&0x80) == 0 :
		k2 = _shift_bytes(k1)
	else:
		k2 = _shift_bytes(k1,xor_lsb=C)

	#calculate last (fixup) block 
	dmac = a.decrypt(target_mac)
	mn = strxor(mi, dmac)
	mn = strxor(mn, k1)
	return prefix+mn


def factors_sieve(number, bound=10000):
  " Using primes in trial division "

  # Find primes up to sqrt(n)
  n=bound
  era =[1] * n
  primes=[]
  for p in range(2, n):
      if era[p]:
          primes.append(p)
          for i in range(p*p, n, p):
              era[i] = False

  # Trial division using primes
  divisors=[]
  x=number
  for i in primes:
      while x%i==0:
          x//=i
          divisors.append(i)
  if x!=1:
      divisors.append(x)    
  return divisors


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--remote', help='The host:port of the remote to connect to')
	args = parser.parse_args()

	if args.remote:
		p = remote(*args.remote.split(':'))
	else:
		p = process(["python3", "server.py"])


	count = 0
	found = False
	while not found: 
		newpub_prefix = b'\xff'*(16) + os.urandom((2048//8)-(16)-(16))
		new_pub = bytes_to_long(forge_mac(NIST_SP_800_38B_AppD1, server_cmac_publickey, newpub_prefix))
		f = factors_sieve(new_pub)
		if isPrime(f[-1]) and f[0] != 2 and (len(f) == len(set(f))): #dont want 2, dont want duplicates 
			log.success(f"FOUND! Jackpot: {f}")
			found = True
		count += 1
		log.info(count)


	e = 65537 
	d = inverse(e, math.prod([(p-1) for p in f]))

	#p = process(["python3", "server.py"])
	chal_str = p.readline()
	chal = chal_str.split(b':')[1].strip()
	p.readline()

	s = bytes_to_long(SHA512.new(chal).digest())
	sig = pow(s, d, new_pub)
	j = {'public_key' : new_pub, 'signature' : sig}
	p.sendline(json.dumps(j))
	flag = p.readline()

	if b'DUCTF' in flag:
		log.success(f"SUCCESS! {flag}")
		exit(0)
	else:
		log.error(f"ERROR - flag not found - got [{flag}]")
		exit(0)



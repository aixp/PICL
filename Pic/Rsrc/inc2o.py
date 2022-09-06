#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Alexander Shiryaev, 2019.05, 2022.09
#

import sys

def getKV (l):
	k, v = l.split('EQU')
	k = k.strip()
	assert 'H' in v
	v = v.split("'")[1]
	v = int(v, 16)
	return k, v

def load (fileName):
	fh = open(fileName, 'rb')
	banks = {}
	allSfrs = {}
	allBits = {}
	s = 0
	lineNo = 0
	vOld = None
	while True:
		l = fh.readline()
		if l == b'':
			break
		l = l.strip().decode('ascii')
		if s == 0:
			if l.startswith(';') and ('Bank' in l):
				cmtBank = int(l.split('Bank')[1].split('-')[0])
				s = 1
		elif s == 1:
			if 'EQU' in l:
				k, v = getKV(l)
				k0 = k.replace('_', '')
				bank = v // 128
				if vOld is not None:
					assert vOld <= v
				vOld = v
				if bank != cmtBank:
					print(lineNo, l, cmtBank, bank)
					assert False
				if bank in banks:
					d = banks[bank]
				else:
					d = {}
					banks[bank] = d
				assert k0 not in d
				q = [ k, v, {} ]
				d[k0] = q
				assert k0 not in allSfrs
				allSfrs[k0] = q
			elif l == '':
				pass
			elif l.startswith(';') and ('Bank' in l):
				cmtBank = int(l.split('Bank')[1].split('-')[0])
			elif l.startswith(';') and ('Bits' in l):
				cmtSfr = l[1:].split('Bits')[0].replace('-', '').strip()
				s = 2
			else:
				s = 3
		elif s == 2:
			if 'EQU' in l:
				k, v = getKV(l)
				k0 = k.replace('_', '')
				assert (v >= 0) and (v <= 7)
				bits = None
				for b, sfrs in banks.items():
					for sfr, q in sfrs.items():
						if q[0] == cmtSfr:
							bits = q[2]
				assert bits is not None
				assert k0 not in bits
				q = [ k, v ]
				if k0 in allBits:
					assert allBits[k0] == q
					bits[k0] = [ k, v, 1 ] # duplicate
				else:
					allBits[k0] = q
					bits[k0] = [ k, v, 0 ] # first occurence
			elif l == '':
				pass
			elif l.startswith(';') and ('Bits' in l):
				cmtSfr = l[1:].split('Bits')[0].replace('-', '').strip()
			else:
				s = 3
		lineNo += 1
	fh.close()
	return banks

def optimizeBits (sfr, bits):
	reject = []
	for k, v in bits.items():
		if k.endswith('0'):
			baseName = k[:-1]
			y = []
			for x in range(8):
				name = baseName + str(x)
				if name in bits.keys():
					if bits[name][1] == x:
						y.append(x)
					else:
						y = []
						break
			if (y == [0, 1, 2, 3]) or (y == [0, 1, 2, 3, 4]) or (y == [0, 1, 2, 3, 4, 5]) or (y == [0, 1, 2, 3, 4, 5, 6]) or (y == [0, 1, 2, 3, 4, 5, 6, 7]):
				for yy in y:
					name = baseName + str(yy)
					reject.append(name)
		elif k.endswith('8'):
			baseName = k[:-1]
			y = []
			for x in range(8):
				name = baseName + str(x + 8)
				if name in bits.keys():
					if bits[name][1] == x:
						y.append(x)
					else:
						y = []
						break
			if y == [0, 1, 2, 3, 4, 5, 6, 7]:
				for yy in y:
					name = baseName + str(yy + 8)
					reject.append(name)

	newBits = {}
	for k, v in bits.items():
		q = [ v[0], v[1], v[2] ]
		if k in reject:
			q[2] += 2 # rejected
		newBits[k] = q
	return newBits

def optimize (banks):
	r = {}
	for bank, sfrs in banks.items():
		d = {}
		r[bank] = d
		for sfr0, q in sfrs.items():
			sfr, addr, bits = q
			d[sfr0] = [ sfr, addr, optimizeBits(sfr, bits) ]
	return r

def formatBank (bank, sfrs):
	r = [ "(* Bank %s *)" % (bank,) ]
	rr = []
	for k, v in sfrs.items():
		rr.append( (k, v) )
	# rr.sort(key=lambda x: x[1][1])
	for k, v in rr:
		if v[0] != k:
			s2 = " (* %s *)" % (v[0],)
		else:
			s2 = ''
		r.append('	enter1("%s", var, setT, 0%XH);%s' % (k, v[1], s2))
		for k1, v1 in v[2].items():
			if v1[0] != k1:
				s2 = " (* %s *)" % (v1[0],)
			else:
				s2 = ''
			s = 'enter1("%s", con, intT, %s);%s' % (k1, v1[1], s2)
			if v1[2] == 0:
				pass
			elif v1[2] == 1:
				s = None
			else:
				# s = "(* " + s + " *)"
				s = None
			if s is not None:
				r.append('		' + s)
	return r

def format (banks):
	r = []
	bank = min(banks.keys())
	while bank <= max(banks.keys()):
		if bank in banks:
			r.extend(formatBank(bank, banks[bank]))
		bank += 1
	return '\n'.join(r)

def main ():
	data = load(sys.argv[1])
	data = optimize(data)
	s = format(data)
	print(s)

if __name__ == '__main__':
	main()

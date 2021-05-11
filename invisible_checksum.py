#!/usr/bin/python3

import numpy as np, cv2, sys, os
from random import randrange,seed
from time import time

# set seed so that the initial seeds for the pseudo-random generator
# will be hugely different between two successive calls even for very short interval of time
t=int(time()*1000)
seed(	((t & 0xff000000) >> 24) +
		((t & 0x00ff0000) >>  8) +
		((t & 0x0000ff00) <<  8) +
		((t & 0x000000ff) << 24)	)

def blockify(img):

	img_in_1d=img.flatten().astype(np.uint8)
	blocks_of_8=img_in_1d[:(img_in_1d.shape[0]//8)*8]
	return blocks_of_8.reshape((img_in_1d.shape[0]//8,8)),img_in_1d

def extract_56_bits(block):

	# block_64=block[::-1].astype(np.uint64)
	data=0

	for i,x in enumerate(block[::-1]):
		data|=(int(x)>>1)<<(7*i)

	return data

def get_watermark(blocks):

	data=[]
	for block in blocks:
		data.append(extract_56_bits(block))

	cheksum=int(np.sum(data))
	while(cheksum>=2**56):
		lhs=cheksum>>56
		rhs=cheksum & 2**56-1
		cheksum=lhs+rhs
	return cheksum

def random_without_repitition(max,n):

	rand_locs=[randrange(max) for i in range(n)]
	rand_locs=list(np.unique(rand_locs))
	n_=len(rand_locs)

	while n_!=n:

		x=[randrange(max) for i in range(n-n_)]
		rand_locs.extend(x)
		rand_locs=list(np.unique(rand_locs))
		n_=len(rand_locs)

	return list(np.random.permutation(rand_locs))

def apply_watermark(img_in_1d,w):

	x=img_in_1d.shape[0]//8*8
	random_locations=random_without_repitition(x,56)

	for i,loc in enumerate(random_locations):
		w_= w>>(55-i) & 1
		img_in_1d[loc]= (img_in_1d[loc]//2)*2 | w_

	return img_in_1d,random_locations

def watermark(img_file):

	img = cv2.cvtColor(cv2.imread(img_file),cv2.COLOR_BGR2RGB)
	blocks,img_in_1d=blockify(img)
	watermark=get_watermark(blocks)
	watermarked_img_in_1d,key=apply_watermark(img_in_1d,watermark)
	watermarked_image=watermarked_img_in_1d.reshape(img.shape)

	path=os.path.splitext(img_file)
	watermarked_file=f'{path[0]}-watermarked{path[1]}'
	cv2.imwrite(watermarked_file,cv2.cvtColor(watermarked_image,cv2.COLOR_RGB2BGR))
	print(f'watermarked image saved as {watermarked_file}')

	key_file=f'{path[0]}-watermarked.key'
	with open(key_file,'w') as w:
		w.write(f'{str(watermark)}\n')
		for loc in key[:-1]:
			w.write(f'{loc}\n')
		w.write(f'{key[-1]}')
	print(f'watermark and key saved as {key_file}')

	return watermarked_file,key_file

def extract_watermark_with_key(img_in_1d,key):

	w=0
	for i,loc in enumerate(key):
		w |= (img_in_1d[loc] & 1)<<(55-i) 
	return w

def check_watermark(img_file,key_file,threshold=0.8):

	with open(key_file) as w:
		key=w.readlines()
	key=[int(i) for i in key]
	w=key[0]
	key=key[1:]

	img = cv2.cvtColor(cv2.imread(img_file),cv2.COLOR_BGR2RGB)
	blocks,img_in_1d=blockify(img)
	w_=extract_watermark_with_key(img_in_1d,key)

	w=list(np.binary_repr(w,width=64))[-56:]
	w=np.array(w).astype(float)
	w=w-np.mean(w)
	wnorm=w @ w.T

	w_=list(np.binary_repr(w_,width=64))[-56:]
	w_=np.array(w_).astype(float)
	w_=w_-np.mean(w_)
	w_norm=w_ @ w_.T

	ncc=np.correlate(w,w_,'full')/(wnorm*w_norm)**0.5

	if ncc[55]>threshold:
		return True

	return False

if __name__ == '__main__':

	argc=len(sys.argv)

	if argc not in [2,3]:

		if argc == 1:
			print(f'{sys.argv[0]}: missing operands',file=sys.stderr)
		else:
			print(f'{sys.argv[0]}: too many operands',file=sys.stderr)

		print(f'correct usage:\n{sys.argv[0]} image\n\t> for watermarking (or)\n{sys.argv[0]} image key\n\t> for checking watermark',file=sys.stderr)
		sys.exit(1)

	elif(argc==2):

		watermark(sys.argv[1])

	else:

		if check_watermark(sys.argv[1],sys.argv[2]):
			print("the image is authentic")
		else:
			print("the image is not authentic")
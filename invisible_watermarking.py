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

def random_without_repitition(max,n):

	rand_locs=[randrange(max) for i in range(n)]
	rand_locs=list(np.unique(rand_locs))
	n_=len(rand_locs)

	while n_!=n:

		x=[randrange(max) for i in range(n-n_)]
		rand_locs.extend(x)
		rand_locs=list(np.unique(rand_locs))
		n_=len(rand_locs)

	# return rand_locs
	return list(np.random.permutation(rand_locs))

def watermark(img_file,wm_file):

	img = cv2.cvtColor(cv2.imread(img_file),cv2.COLOR_BGR2RGB)
	wm = cv2.imread(wm_file,0)

	height,width=img.shape[0],img.shape[1]
	wm_height,wm_width=wm.shape[0],wm.shape[1]
	if width*height<wm_height*wm_width:
		raise Exception("watermark size cannot be larger than the image size")

	random_locations=random_without_repitition(width*height,wm_height*wm_width)
	for i,loc in enumerate(random_locations):
		x,y=loc//width,loc%width
		x_wm,y_wm=i//wm_width,i%wm_width
		# img[x,y] = (img[x,y]//4)*4 + wm[x_wm,y_wm]//64
		img[x,y] = (img[x,y] & 0xfc) + (wm[x_wm,y_wm] >> 6)

	path=os.path.splitext(img_file)
	watermarked_file=f'{path[0]}-watermarked{path[1]}'
	cv2.imwrite(watermarked_file,cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
	print(f'watermarked image saved as {watermarked_file}')

	key_file=f'{path[0]}-watermark.key'
	with open(key_file,'w') as w:
		w.write(f'{wm.shape[0]} {wm.shape[1]}\n')
		for loc in random_locations[:-1]:
			w.write(f'{loc}\n')
		w.write(f'{random_locations[-1]}')
	print(f'watermark and key saved as {key_file}')

	return watermarked_file,key_file

def extract_watermark(img_file,key_file,threshold=0.8):

	img = cv2.imread(img_file)
	height,width=img.shape[0],img.shape[1]

	with open(key_file) as w:
		key=w.readlines()
	wm_height,wm_width=[int(i) for i in key[0].split()]
	key=key[1:]
	key=[int(i) for i in key]

	wm=np.empty((wm_height,wm_width,),dtype=int)

	for i,loc in enumerate(key):
		x,y=loc//width,loc%width
		x_wm,y_wm=i//wm_width,i%wm_width
		# wm[x_wm,y_wm] = img[x,y][0] - 4*(img[x,y][0]//4)
		wm[x_wm,y_wm] = (img[x,y][0]%4)

	wm*=64

	cv2.imwrite('static/extracted_watermark.png',wm)
	print('extracted watermarked image saved as extracted_watermark.png')

	return 'static/extracted_watermark.png'

if __name__ == '__main__':

	op=[]
	for i in sys.argv:
		if i[0] == '-':
			sys.argv.remove(i)
			op.append(i)

	argc=len(sys.argv)

	if argc!=3 or len(op)>1 or op[0] not in ['-w','-e']:

		print(f'{sys.argv[0]}: invalid usage',file=sys.stderr)
		print(f'correct usage:\n{sys.argv[0]} -w image watermark\n\t> for watermarking (or)\n{sys.argv[0]} -e image watermark-key\n\t> for extracting watermark',file=sys.stderr)
		sys.exit(1)

	elif op[0]=='-w':
		watermark(sys.argv[1],sys.argv[2])

	else:
		extract_watermark(sys.argv[1],sys.argv[2])
#!/usr/bin/python3

import os, cv2, numpy as np

def svd(matrix):

	u,s,v=np.linalg.svd(matrix)
	x=np.zeros(matrix.shape)
	np.fill_diagonal(x,s)
	return u,x,v

def watermark(image_file,watermark_file,scaling_factor=0.1):

	image=cv2.imread(image_file,0)
	watermark=cv2.imread(watermark_file,0)
	watermark_resized=cv2.resize(watermark, (image.shape[1],image.shape[0]), interpolation=cv2.INTER_LINEAR)

	u1,s1,v1=svd(image)
	temp=s1+scaling_factor*watermark_resized
	uw,sw,vw=svd(temp)
	watermarked_image= u1 @ sw @ v1

	path=os.path.splitext(image_file)
	watermarked_file=f'{path[0]}-watermarked{path[1]}'
	cv2.imwrite(watermarked_file,watermarked_image)
	print(f'watermarked image saved as {watermarked_file}')

	return watermarked_file

def extract_watermark(original_image_file,watermark_file,watermarked_image_file,scaling_factor=0.1):

	image=cv2.imread(original_image_file,0)
	watermark=cv2.imread(watermark_file,0)
	watermarked_image=cv2.imread(watermarked_image_file,0)
	watermark_resized=cv2.resize(watermark, (image.shape[1],image.shape[0]), interpolation=cv2.INTER_LINEAR)

	u1,s1,v1=svd(image)
	temp=s1+scaling_factor*watermark_resized
	uw,sw,vw=svd(temp)

	uw1,sw1,vw1=svd(watermarked_image)
	D=uw @ sw1 @ vw
	w=(D-s1)/scaling_factor
	
	path=os.path.splitext(original_image_file)
	extracted_watermark=f'{path[0]}-extracted_watermark{path[1]}'
	cv2.imwrite(extracted_watermark,w)
	print(f'extracted watermark saved as {extracted_watermark}')

	return extracted_watermark

if __name__ == '__main__':

	import sys

	argc=len(sys.argv)

	if argc not in [3,4]:

		print(f'{sys.argv[0]}: invalid usage',file=sys.stderr)
		print(f'correct usage:\n{sys.argv[0]} -w image watermark\n\t> for watermarking (or)\n{sys.argv[0]} -e original_image watermarked_image\n\t> for extracting watermark',file=sys.stderr)
		sys.exit(1)

	elif argc==3:
		watermark(sys.argv[1],sys.argv[2])

	else:
		extract_watermark(sys.argv[1],sys.argv[2],sys.argv[3])
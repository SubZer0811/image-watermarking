#!/usr/bin/python3

import os, cv2, pywt

def watermark(image_file,watermark_file,scaling_factor=0.01):

	image=cv2.imread(image_file,0)
	watermark=cv2.imread(watermark_file,0)
	watermark_resized=cv2.resize(watermark, (image.shape[1],image.shape[0]), interpolation=cv2.INTER_LINEAR)

	LL,( LH, HL, HH) = pywt.dwt2(image, 'haar')
	L_L,( L_H, H_L, H_H) = pywt.dwt2(watermark_resized, 'haar')
	g=LL+scaling_factor*L_L

	watermarked_image=pywt.idwt2((g,( LH, HL, HH)),'haar')

	path=os.path.splitext(image_file)
	watermarked_file=f'{path[0]}-watermarked{path[1]}'
	cv2.imwrite(watermarked_file,watermarked_image)
	print(f'watermarked image saved as {watermarked_file}')

	return watermarked_file

def extract_watermark(original_image_file,watermarked_image_file,scaling_factor=0.01):

	image=cv2.imread(original_image_file,0)
	watermarked_image=cv2.imread(watermarked_image_file,0)

	LL,( LH, HL, HH) = pywt.dwt2(image, 'haar')
	a,( b, c, d) = pywt.dwt2(watermarked_image, 'haar')
	w=(a-LL)/scaling_factor

	path=os.path.splitext(watermarked_image_file)
	extracted_watermark=f'{path[0]}-extracted_watermark{path[1]}'
	cv2.imwrite(extracted_watermark,w)
	print(f'extracted watermark saved as {extracted_watermark}')

	return extracted_watermark

if __name__ == '__main__':

	import sys

	op=[]
	for i in sys.argv:
		if i[0] == '-':
			sys.argv.remove(i)
			op.append(i)

	argc=len(sys.argv)

	if argc!=3 or len(op)>1 or op[0] not in ['-w','-e']:

		print(f'{sys.argv[0]}: invalid usage',file=sys.stderr)
		print(f'correct usage:\n{sys.argv[0]} -w image watermark\n\t> for watermarking (or)\n{sys.argv[0]} -e original_image watermarked_image\n\t> for extracting watermark',file=sys.stderr)
		sys.exit(1)

	elif op[0]=='-w':
		watermark(sys.argv[1],sys.argv[2])

	else:
		extract_watermark(sys.argv[1],sys.argv[2])
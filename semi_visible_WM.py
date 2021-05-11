import cv2

def semi_visible_WM(img, wm, alpha=0.5, pos='BR'):

	if pos == "BR":
		pos = [img.shape[0]-wm.shape[0], img.shape[1]-wm.shape[1]]
	if pos == "BL":
		pos = [img.shape[0]-wm.shape[0], 0]
	if pos == "TR":
		pos = [0, img.shape[1]-wm.shape[1]]
	if pos == "TL":
		pos = [0, 0]

	orig = img[pos[0]:wm.shape[0]+pos[0], pos[1]:wm.shape[1]+pos[1]]
	img[pos[0]:wm.shape[0]+pos[0], pos[1]:wm.shape[1]+pos[1]] = (1-alpha)*orig + alpha*wm

	return img

img = cv2.imread("Lenna.png")
wm = cv2.imread("watermark_T&J.jpg")

print(f'shape of img = {img.shape}')
print(f'shape of wm = {wm.shape}')
wm_img = semi_visible_WM(img, wm, pos='BR', alpha=0.5)

cv2.imshow("img", wm_img)
cv2.waitKey(0)
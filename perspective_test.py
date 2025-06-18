import cv2
import math
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread('images/raw_jpeg/desk78.jpeg')
rows, cols, ch = img.shape

# pts1 = np.float32([[3682,345], [457,349], [2448,2520],[493,2602]]) #out of order
pts1 = np.float32([[457,349], [3682,345],[2448,2520],[493,2602]]) #need these to be a rectangle lmao

# ratio=1.6
ratio = 334/449 # 449 by 334
deskH = math.sqrt((pts1[2][0]-pts1[1][0])**2 + (pts1[2][1]-pts1[1][1])**2)
deskW = ratio * deskH
pts2 = np.float32([
    [pts1[0][0], pts1[0][1]],
    [pts1[0][0]+deskW, pts1[0][1]],
    [pts1[0][0]+deskW, pts1[0][1]+deskH],
    [pts1[0][0], pts1[0][1]+deskH]
])

M = cv2.getPerspectiveTransform(pts1, pts2)

output_width = int(deskW + 500)
output_height = int(deskH + 500)
dst = cv2.warpPerspective(img, M, (output_width, output_height))

# Convert BGR to RGB for matplotlib
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
dst_rgb = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

plt.subplot(121), plt.imshow(img_rgb), plt.title('Input')
plt.subplot(122), plt.imshow(dst_rgb), plt.title('Output')
plt.show()

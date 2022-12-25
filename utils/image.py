# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

from math import sqrt
import numpy as np

# #################################################################
# Some functions about filter
# #################################################################

def medianfliter(img : np.ndarray, template_size : int) -> np.ndarray:
    """
        Median-fliter function | 中值滤波
        Args:
            img : np.ndarray # image to calculate
            template_size : int # template size , 3 or 5
        Returns:
            np.ndarray: median-fliter image
    """
    output = img
    if template_size == 3 :
        output1 = np.zeros(img.shape, np.uint8)
        # Complete the 9 surrounding squares and templates for bubble sorting
        for i in range(1, output.shape[0]-1):
            for j in range(1, output.shape[1]-1):
                value1 = [output[i-1][j-1], output[i-1][j], output[i-1][j+1], output[i][j-1], output[i][j], output[i][j+1], output[i+1][j-1], output[i+1][j], +output[i+1][j+1]]
                output1[i-1][j-1] = np.sort(value1)[4]
    elif template_size == 5:
        output1 = np.zeros(img.shape, np.uint8)
        # Complete 25 squares around to convolve with the template
        for i in range(2, output.shape[0]-2):
            for j in range(2, output.shape[1]-2):
                value1 = [output[i-2][j-2],output[i-2][j-1],output[i-2][j],output[i-2][j+1],output[i-2][j+2],output[i-1][j-2],output[i-1][j-1],output[i-1][j],output[i-1][j+1],\
                            output[i-1][j+2],output[i][j-2],output[i][j-1],output[i][j],output[i][j+1],output[i][j+2],output[i+1][j-2],output[i+1][j-1],output[i+1][j],output[i+1][j+1],\
                            output[i+1][j+2],output[i+2][j-2],output[i+2][j-1],output[i+2][j],output[i+2][j+1],output[i+2][j+2]]
                output1[i-2][j-2] = value1.sort()[12]
    else :
        print("Unknown template size , choose from 3 or 5")
    return output1

def meanflite(img : np.ndarray, template_size : int) -> np.ndarray:
    """
        Mean-flite function | 中值滤波
        Args:
            a : np.ndarray # image to calculate
            windowsize : int # window size, 3 or 5
        Returns:
            output : np.ndarray # image after mean filter process
    """
    output = img
    if template_size == 3:
        # Generate 3x3 templates
        window = np.ones((3, 3)) / 3 ** 2
        output1 = np.zeros(img.shape, np.uint8)
        # Complete the 9 surrounding squares and templates for bubble sorting
        for i in range(1, output.shape[0] - 1):
            for j in range(1, output.shape[1] - 1):
                value = (output[i - 1][j - 1] * window[0][0] + output[i - 1][j] * window[0][1] + output[i - 1][j + 1] *
                         window[0][2] + \
                         output[i][j - 1] * window[1][0] + output[i][j] * window[1][1] + output[i][j + 1] * window[1][
                             2] +\
                         output[i + 1][j - 1] * window[2][0] + output[i + 1][j] * window[2][1] + output[i + 1][j + 1] *
                         window[2][2])
                output1[i - 1][j - 1] = value
    elif template_size == 5:
        # Generate 5x5 templates
        window = np.ones((5, 5)) / 5 ** 2
        output1 = np.zeros(img.shape, np.uint8)
        # Complete 25 squares around to convolve with the template
        for i in range(2, output.shape[0] - 2):
            for j in range(2, output.shape[1] - 2):
                value = (output[i - 2][j - 2] * window[0][0] + output[i - 2][j - 1] * window[0][1] + output[i - 2][j] *
                         window[0][2] + output[i - 2][j + 1] * window[0][3] + output[i - 2][j + 2] * window[0][4] + \
                         output[i - 1][j - 2] * window[1][0] + output[i - 1][j - 1] * window[1][1] + output[i - 1][j] *
                         window[1][2] + output[i - 1][j + 1] * window[1][3] + output[i - 1][j + 2] * window[1][4] + \
                         output[i][j - 2] * window[2][0] + output[i][j - 1] * window[2][1] + output[i][j] * window[2][
                             2] + output[i][j + 1] * window[2][3] + output[i][j + 2] * window[2][4] + \
                         output[i + 1][j - 2] * window[3][0] + output[i + 1][j - 1] * window[3][1] + output[i + 1][j] *
                         window[3][2] + output[i + 1][j + 1] * window[3][3] + output[i + 1][j + 2] * window[3][4] + \
                         output[i + 2][j - 2] * window[4][0] + output[i + 2][j - 1] * window[4][1] + output[i + 2][j] *
                         window[4][2] + output[i + 2][j + 1] * window[4][3] + output[i + 2][j + 2] * window[4][4])
                output1[i - 2][j - 2] = value
    else:
        print("Invalid template size was given")
    return output1

def gaussianfilter(img : np.ndarray,sigma : float,kernel_size : int) -> np.ndarray:
    """
        Gaussian filter | 高斯滤波
        Args:
            img : np.ndarray # image to filter
            sigma : float # sigma of the Gaussian filter
            kernel_size : int # kernel size of the Gaussian filter
        Returns:
            np.ndarray # filtered image
        Examples:
            gaussianfilter(image,1.5,3)
    """
    h,w,c = img.shape
    # Zero padding | 零填充
    padding = kernel_size//2
    out = np.zeros((h + 2*padding,w + 2*padding,c),dtype=np.float)
    out[padding:padding+h,padding:padding+w] = img.copy().astype(np.float)
    # Define filter kernel | 定义滤波核
    kernel = np.zeros((kernel_size,kernel_size),dtype=np.float)
    
    for x in range(-padding,-padding+kernel_size):
        for y in range(-padding,-padding+kernel_size):
            kernel[y+padding,x+padding] = np.exp(-(x**2+y**2)/(2*(sigma**2)))
    kernel /= (sigma*np.sqrt(2*np.pi))
    kernel /= kernel.sum()
    
    # Convolution process | 卷积过程
    tmp = out.copy()
    for y in range(h):
        for x in range(w):
            for ci in range(c):
                out[padding+y,padding+x,ci] = np.sum(kernel*tmp[y:y+kernel_size,x:x+kernel_size,ci])
    
    return out[padding:padding+h,padding:padding+w].astype(np.uint8)

# #########################################################################
# Some functions about adding noise to image
# #########################################################################

from random import random,randint

def add_salt_pepper_noise(image : np.ndarray, threshold : float) -> np.ndarray:
    """
        Add salt and pepper noise to image
        Args:
            image: np.ndarray # image to add noise
            threshold: float # Salt noise threshold
        Returns:
            np.ndarray
    """
    output = np.zeros(image.shape, np.uint8)
    thres = 1 - threshold
    # Traverse the grayscale of the entire image | 遍历整个图片的灰度级
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Generate a random number between 0-1 | 生成一个随机0-1之间的随机数
            randomnum = random()
            # If the random number is greater than the salt noise threshold of 0.1, set the gray level value at this position to 0, that is, add salt noise
            if randomnum < threshold:  # 如果随机数大于盐噪声阈值0.1，则将此位置灰度级的值设为0，即添加盐噪声
                output[i][j] = 0
            # If the random number is greater than the pepper noise threshold of 1-0.1, set the output of the gray level at this position to 255, that is, add pepper noise
            elif randomnum > thres:  # 如果随机数大于胡椒噪声阈值1-0.1，则将此位置灰度级的输出设为255，即添加胡椒噪声
                output[i][j] = 255
            # If the random number is between the two, the gray level value at this position is equal to the gray level value of the original image
            else:  # 如果随机数处于两者之间，则此位置的灰度级的值等于原图的灰度级值
                output[i][j] = image[i][j]
    return output

def add_gaussian_noise(image : np.ndarray, mean : float, var : float) -> np.ndarray:
    """
        Add gaussian noise to image | 为图像添加高斯噪声
        Args:
            image: np.ndarray # image to add noise
            mean: float # mean value 均值
            var: float # variance value 方差
        Returns:
            np.ndarray # image with gaussian noise
    """
    image = np.array(image/255, dtype=float)
    noise = np.normal(mean, var ** 0.5, image.shape)
    output = image + noise
    output_handle = np.array([[[0]*3 for i in range(output.shape[1])] for i in range(output.shape[0])], dtype=float)
    if output.min() < 0:
        low_clip = -1.
    else:
        low_clip = 0.
    for i in range (output.shape[0]):
        for j in range (output.shape[1]):
            for k in range (output.shape[2]):
                if output[i][j][k] < low_clip:
                    output_handle[i][j][k] = low_clip
                elif output[i][j][k] > 1.0:
                    output_handle[i][j][k] = 1.0
                else:
                    output_handle[i][j][k] = output[i][j][k]
    output = np.uint8(output_handle*255)
    return output

def add_random_noise(image : np.ndarray,threshold : float) -> np.ndarray:
    """
        Add random noise to image | 为图像添加随机噪声
        Args:
            image: np.ndarray # image to add noise
            threshold: float # probability to add noise
        Returns:
            np.ndarray # image with random noise
    """
    output = image
    n = randint(1, 1000) + int(threshold*20000)
    for k in range(n-500):
        a = randint(0, 50)
        b = randint(0, 50)
        c = randint(0, 50)
        i = randint(0, image.shape[0]-1)
        j = randint(0, image.shape[1]-1)
        output[i][j][0] = 255-a
        output[i][j][1] = 255-b
        output[i][j][2] = 255-c
    for k in range(n):
        a = randint(0, 50)
        b = randint(0, 50)
        c = randint(0, 50)
        i = randint(0, image.shape[0]-1)
        j = randint(0, image.shape[1]-1)
        output[i][j][0] = a
        output[i][j][1] = b
        output[i][j][2] = c
    return output

# #################################################################
# Calculate the HFD
# #################################################################

def calc_hfd(image : np.ndarray,outer_diameter : int) -> float:
    """
        Calculate the HFD of an image | 计算图像HFD
        Args:
            image : np.ndarray # image to calculate
            outer_diameter : int # outer diameter of the circle
        Returns:
            float: HFD of the image
    """
    if outer_diameter is None:
        outer_diameter = 60
    output = image
    # Calculate the mean of the image
    # Meanfilter ?
    mean = np.mean(image)
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if image[x][y] < mean: 
                output[x][y] = 0
            else:
                output[x][y] -= mean
    
    out_radius = outer_diameter / 2

    center_x = int(output.shape[0] / 2)
    center_y = int(output.shape[1] / 2)

    _sum,sum_dist = 0,0

    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if pow(x - center_x,2) + pow(y - center_y,2) <= pow(out_radius,2):
                _sum += output[x][y]
                sum_dist = output[x][y] * sqrt(pow(x - center_x,2) + pow(y - center_y,2))
    if _sum != 0:
        return 2 * sum_dist / _sum
    return sqrt(2) * out_radius

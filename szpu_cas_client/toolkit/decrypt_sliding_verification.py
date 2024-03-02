import base64
import requests
import numpy as np
import cv2


class SlidingVerification:
    def base64_to_npimage(self, base64_str):
        # 将base64转换为图片
        image_raw = np.frombuffer(base64.b64decode(base64_str), dtype=np.uint8)
        npimage = cv2.imdecode(image_raw, cv2.IMREAD_COLOR)
        return npimage

    def getDiff(self, temp, small_image, mask):
        if small_image.shape != temp.shape:
            temp = cv2.resize(temp, (small_image.shape[1], small_image.shape[0]))
        diff = (temp - small_image)

        # 计算差值的和
        # 计算均值
        diff = diff * mask
        diff = np.sum(diff, axis=2)
        diff_mean = (temp - small_image * 0.75).mean()

        diff = diff - diff.mean()
        diff = np.abs(diff)
        diff_sum = np.var(diff)

        return diff, diff_sum, diff_mean

    def decrypt(self, small_image_base64, big_image_base64):
        small_image = self.base64_to_npimage(small_image_base64)
        big_image = self.base64_to_npimage(big_image_base64)
        # 获取小图坐标
        # 对小图的列进行求和
        small_id = np.sum(small_image, axis=2)
        small_id = np.sum(small_id, axis=1)
        # 获取从下往上数第一个非0的索引
        y1 = np.argmax(small_id[::-1] > 0)
        # 获取从上往下数第一个非0的索引
        y2 = np.argmax(small_id > 0)
        # 裁剪小图
        small_image = small_image[y2:-y1, :, :]
        big_image = big_image[y2:-y1, :, :]
        cv2.imwrite('big.png', big_image)
        # big = big_image.copy()
        # cv2.imwrite('small.png', small_image)
        mask = cv2.threshold(small_image, 0, 1, cv2.THRESH_BINARY)[1]
        # 对小图进行canny边缘提取
        # 调整小图亮度
        # 将小图转为浮点数
        small_image = small_image.astype(np.float32)
        # 将大图转为浮点数
        big_image = big_image.astype(np.float32)
        # 获取大图和小图的宽度
        small_width = small_image.shape[1]
        big_width = big_image.shape[1]
        result = []
        backup = []
        for x in range(big_width - small_width):
            # 截取大图的x到x+小图宽度的图像
            temp = big_image[:, x:x + small_width]
            # 计算差值
            diff, diff_sum, diff_mean = self.getDiff(temp, small_image, mask)
            result.append(diff_sum)
            backup.append(diff_mean)
        # 获取最小值的索引
        x = np.argmin(result)
        # 截取大图的x到x+小图宽度的图像
        res_image = big_image[:, x:x + small_width, :]
        diff, diff_sum, diff_mean = self.getDiff(res_image, small_image, mask)
        if diff_sum < 500:
            x = np.argmin(backup)
            res_image = big_image[:, x:x + small_width, :]
        # 保存结果
        cv2.imwrite('../../Result.png', res_image)
        return {'canvasLength': big_width, 'moveLength': x}


if __name__ == '__main__':
    url = 'https://authserver.szpt.edu.cn/authserver/common/openSliderCaptcha.htl'
    response = requests.get(url).json()
    small_image_base64 = response['smallImage']
    big_image_base64 = response['bigImage']

    result = main(small_image_base64, big_image_base64)
    print(result)

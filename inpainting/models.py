from django.db import models
import matplotlib.pyplot as plt
import PIL
from io import BytesIO
from django.core.files.base import ContentFile
import numpy as np 
import os
import cv2
from pathlib import Path
from TEST_JW.test import (
    easy_ocr_result,
    translate_texts,
    cut_image,
    mask_image,
    change_original,
    change_color,
    rewrite,
    change_bg_color,
)


class Image(models.Model):
    image = models.ImageField(upload_to='image/',blank=True, null=True)

    def save(self, *args, **kwargs):
        # 이미지 열기


        img_pil = PIL.Image.open(self.image).convert('RGB') # 4channel 들어올경우 -> 3channl 


        img_np = np.array(img_pil)

        # # 3차원으로 변경
        # img_np = cv2.imread(img_pil, cv2.IMREAD_COLOR)

        print('img_np shape', img_np.shape)
        bbox_list, text_list = easy_ocr_result(img_np)

        tranlated_texts = translate_texts(texts=text_list, type='naver')


        color_list=[]
        
        for bbox in bbox_list:
            img_cut = cut_image(img_np, bbox)

            color_list.append(change_color(img_cut))

            # mask = mask_image(img_cut)
            # masked_img = cv2.inpaint(img_cut, mask, 3, cv2.INPAINT_TELEA)
            print('img_cut shape',img_cut.shape)
            b,g,r = change_bg_color(img_cut)
            print(b.shape)
            img_cut[:,:,0] = b
            img_cut[:,:,1] = g
            img_cut[:,:,2] = r

            img_np = change_original(img_np, img_cut, bbox)

        print('color list',color_list)

        img_pil = PIL.Image.fromarray(img_np)
        # print('type',type(img_pil))
        img = rewrite(img_pil, tranlated_texts,bbox_list, color_list)

        # print(img)
        # print(type(img))
        #  convert back to pil image
        # im_pil = Image.fromarray(img)
        # plt.imshow(img)
        # plt.show()
        # 저장
        
        buffer = BytesIO()
        img.save(buffer, format='png')
        image_png = buffer.getvalue()

        self.image.save(str(self.image), ContentFile(image_png), save=False)

        super().save(*args,**kwargs)
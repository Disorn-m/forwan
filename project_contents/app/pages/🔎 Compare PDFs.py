import streamlit as st
import pdf2image
import cv2
from skimage.metrics import structural_similarity
import imutils
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
import logging

st.set_page_config(layout="wide")

st.header('🔎 Compare PDFs')
st.markdown("Compare and identify differences between versions of PDF drawings and documents. This code will generate a new PDF highlighting the differences in pink. This tool was prepared by Fabien Blanchais. For more information about the tool and utilisation, see https://github.com/mottmacdonaldglobal/")

uploaded_files = st.file_uploader("",accept_multiple_files=True)
button = st.button("Compare PDFs")

image_list=[]
if button and uploaded_files is not None:
    logging.info('starting processing')
    old = pdf2image.convert_from_bytes(uploaded_files[0].read())
    new = pdf2image.convert_from_bytes(uploaded_files[1].read())
    logging.info('files converted')
    for page_old, page_new in zip(old, new):
        
        imageA=np.array(page_old)
        imageB=np.array(page_new)
        logging.info('get array')
        
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        logging.info('cvtColor')

        (score, diff) = structural_similarity(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
        #st.write("Similarity between PDFs: {sim}%".format(sim=round(score*100,2)))

        thresh = cv2.threshold(diff, 0, 255,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for cnt in cnts:
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(imageA, (x, y), (x + w, y + h), (255, 0, 255), 24)
            cv2.rectangle(imageB, (x, y), (x + w, y + h), (255, 0, 255), 24)

        image = Image.fromarray(imageB, 'RGB')
        image_list.append(image)
    
    byte_io = BytesIO()
    image_list[0].save(byte_io, save_all=True, append_images=image_list[1:],format="pdf")
    st.download_button(label="Download Compared PDFs", data=byte_io.getvalue(), file_name="Compared PDFs.pdf", mime='application/octet-stream')
    for im in image_list:
        st.image(im, use_column_width=True)
        

    
    
        



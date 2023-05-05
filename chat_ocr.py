import cv2
import os
import pandas as pd
from PIL import Image
import io
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR, draw_ocr

cwd = os.getcwd()
# load chat detection models and functions
YOLO_chat_detection_model = YOLO(os.path.join(cwd, 'chat_dtc.pt'))  # load a custom model
PADDLE_text_detection_ocr = PaddleOCR(lang='en', use_angle_cls=False, use_gpu=True)


def decode_image(input):
    print("In decode image")
    print(input)
    new_blob = input.download_as_bytes()
    file_like_object = io.BytesIO(new_blob)
    og_img = Image.open(file_like_object)

    # Predict with the model
    YOLO_chat_detection_results = YOLO_chat_detection_model(og_img)  # predict on an image

    # load in the original image for future processing
    # og_img = cv2.imread(input)

    YOLO_chat_detection_results_df = pd.DataFrame()
    YOLO_chat_detection_label_list = []
    YOLO_chat_detection_x1_list = []
    YOLO_chat_detection_x2_list = []
    YOLO_chat_detection_y1_list = []
    YOLO_chat_detection_y2_list = []
    PADDLE_chat_raw_text_str_list = []

    for YOLO_chat_detection_result_index in range(len(YOLO_chat_detection_results[0])):
        # collect labels from our chat detection ie: 'sent', 'group', 'received'
        YOLO_chat_detection_x1, YOLO_chat_detection_y1, YOLO_chat_detection_x2, YOLO_chat_detection_y2 = \
        YOLO_chat_detection_results[0].boxes.xyxy[YOLO_chat_detection_result_index].cpu().numpy()
        print("In forloop 1")

        text_bubble_box_img = cv2.cvtColor(np.array(og_img.crop((YOLO_chat_detection_x1, YOLO_chat_detection_y1, YOLO_chat_detection_x2, YOLO_chat_detection_y2))), cv2.COLOR_RGB2BGR)
        print("Line 44")

        for YOLO_chat_detection_cls in YOLO_chat_detection_results[0][YOLO_chat_detection_result_index].boxes.cls:
            YOLO_chat_detection_label_list.append(YOLO_chat_detection_model.names[int(YOLO_chat_detection_cls)])

        PADDLE_extracted_chat_text = ' '.join(
            [PADDLE_output_tuple[0] for PADDLE_output_tuple in PADDLE_text_detection_ocr(text_bubble_box_img)[1]])
        print("50")

        YOLO_chat_detection_x1_list.append(YOLO_chat_detection_x1)
        YOLO_chat_detection_x2_list.append(YOLO_chat_detection_x2)
        YOLO_chat_detection_y1_list.append(YOLO_chat_detection_y1)
        YOLO_chat_detection_y2_list.append(YOLO_chat_detection_y2)
        PADDLE_chat_raw_text_str_list.append(PADDLE_extracted_chat_text)

    YOLO_chat_detection_results_df['label'] = YOLO_chat_detection_label_list
    YOLO_chat_detection_results_df['x1'] = YOLO_chat_detection_x1_list
    YOLO_chat_detection_results_df['x2'] = YOLO_chat_detection_x2_list
    YOLO_chat_detection_results_df['y1'] = YOLO_chat_detection_y1_list
    YOLO_chat_detection_results_df['y2'] = YOLO_chat_detection_y2_list
    YOLO_chat_detection_results_df['text'] = PADDLE_chat_raw_text_str_list
    YOLO_chat_detection_results_df = YOLO_chat_detection_results_df.sort_values(by='y2', ascending=True).reset_index(
        drop=True)

    group = ''
    messages_list = []
    previous_label = ''
    message_text = ''
    for YOLO_chat_detection_results_df_index in range(len(YOLO_chat_detection_results_df) - 1):
        YOLO_chat_detection_results_row = YOLO_chat_detection_results_df.iloc[YOLO_chat_detection_results_df_index]
        YOLO_chat_detection_results_row_ahead = YOLO_chat_detection_results_df.iloc[
            YOLO_chat_detection_results_df_index + 1]

        if YOLO_chat_detection_results_row['label'] == 'group':
            group = YOLO_chat_detection_results_row['text']

        if YOLO_chat_detection_results_row['label'] == 'sent':

            message_text = f"{message_text} {YOLO_chat_detection_results_row['text']}"
            if YOLO_chat_detection_results_row_ahead['label'] != 'sent':
                messages_list.append({"role": "assistant", "content": message_text})
                message_text = ''
        elif YOLO_chat_detection_results_row['label'] == 'received':

            message_text = f"{message_text} {YOLO_chat_detection_results_row['text']}"
            if YOLO_chat_detection_results_row_ahead['label'] != 'received':
                messages_list.append({"role": "user", "content": message_text})
                message_text = ''

    if YOLO_chat_detection_results_row_ahead['label'] == 'sent':
        message_text = f"{message_text} {YOLO_chat_detection_results_row_ahead['text']}"
        if YOLO_chat_detection_results_row['label'] != 'sent':
            messages_list.append({"role": "assistant", "content": message_text})
        else:
            messages_list.append({"role": "assistant", "content": message_text})
    elif YOLO_chat_detection_results_row_ahead['label'] == 'received':
        message_text = f"{message_text} {YOLO_chat_detection_results_row_ahead['text']}"
        if YOLO_chat_detection_results_row['label'] != 'received':
            messages_list.append({"role": "user", "content": message_text})
        else:
            messages_list.append({"role": "user", "content": message_text})

    print("End decode image")

    final_response = {'name': group, 'messages': messages_list}
    print(
        final_response)  # {'name': '<name of person you are talking to>', 'messages': [{'role': '<assistant or user>', 'content': '<what the entity texted about>'}]}

from paddleocr import PaddleOCR

paddle_ocr = PaddleOCR(lang="en", text_detection_model_name="PP-OCRv5_server_det",
                    text_recognition_model_name="PP-OCRv5_server_rec",
                    use_doc_orientation_classify=True,
                    use_doc_unwarping=True,
                    use_textline_orientation=True )

def read_paddle_output(ticket_upload):
    results = paddle_ocr.predict(ticket_upload)
    text = []

    for i in results:
        data = i.json
        texts = data['res']['rec_texts']

        for j in texts:
            text.append(j)

    return text
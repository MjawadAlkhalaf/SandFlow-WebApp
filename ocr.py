from paddleocr import PaddleOCR
import uuid


paddle_ocr = PaddleOCR(lang="en", text_detection_model_name="PP-OCRv5_server_det",
                    text_recognition_model_name="PP-OCRv5_server_rec",
                    use_doc_orientation_classify=True,
                    use_doc_unwarping=True,
                    use_textline_orientation=True )

def read_paddle_output(ticket_upload):
    results = paddle_ocr.predict(ticket_upload)
    final_text = []
    ocr_features = []

    for i in results:
        data = i.json

        texts = data['res']['rec_texts']
        scores = data['res']["rec_scores"]
        boxes = data['res']["rec_boxes"]


        for index , (text,score,box) in enumerate(zip(texts,scores,boxes)):

            final_text.append(text)

            ocr_features.append({

                "detected_text" : text,
                "confidence_score" : float(score),
                "box_location": box.tolist() if hasattr(box, "tolist") else list(box),
                "read_order": index
            }
            )


    return final_text, ocr_features

## extracting raw training fields
def writeRawTraining(ticket_text, ticket, ocr_features):


    newData = {'id' : uuid.uuid4().hex[:12],
                
                'raw_text' : ticket_text,
                'raw_carrier': ticket['carrier'],
                'raw_weight' : ticket['weight'],
                'raw_BOL' : ticket['bol'],
                'raw_truck': ticket['truck'],
                'raw_PO': ticket['po'],
                'raw_facility': ticket['facility'],

                'source' : ticket['source'],

                'Ticket_ocr_features': ocr_features
            }

    return newData
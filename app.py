from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request,Form, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import cv2
import numpy as np

from ocr import read_paddle_output
from ocr import writeRawTraining
from parser import cleanText, parseTicket, checkForInvalid
from processIMG import processJPEG
import fitz
import json
import csv
import io
from pydantic import BaseModel

import sys
from pathlib import Path
import pandas as pd

from matchcsv import match_xiq


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent


if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

train_raw_file = APP_DIR / "SandFlow_RawTrainingData.json"

def saveRawTraining(raw_ticket):

    if train_raw_file.exists():
        with open(train_raw_file, "r", encoding="utf-8") as file:
            training_data = json.load(file)
    else:
        training_data = []

    training_data.append(raw_ticket)

    with open(train_raw_file, "w", encoding="utf-8") as file:
        json.dump(training_data, file, indent=4)


app = FastAPI()


app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static"
)


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)



upload_path = Path("uploads")

upload_path.mkdir(exist_ok=True)

print("UPLOAD DIRECTORY:", upload_path.resolve())
app.mount(
    "/uploads",
    StaticFiles(directory=str(upload_path)),
    name="uploads"
)

#app.mount("/static", StaticFiles(directory="static"), name="static")
#app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

#templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/process-ticket")
async def process_ticket(file: UploadFile = File(...)):

    # Read uploaded file as bytes
    contents = await file.read()


    file_extension = Path(file.filename).suffix.lower()

    if file_extension == ".pdf":

        tickets = []

        doc = fitz.open(
            stream=contents,
            filetype="pdf"
        )

        for page_number, page in enumerate(doc, start=1):

            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5),
                colorspace=fitz.csRGB,
                alpha=False
            )

            img = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(
                pix.height,
                pix.width,
                3
            )

            img = cv2.cvtColor(
                img,
                cv2.COLOR_RGB2BGR
            )

            mod_img = processJPEG(img)

            ticket_text, ocr_features = read_paddle_output(mod_img)

            cleaned_text = cleanText(ticket_text)

            ticket = parseTicket(cleaned_text)

            if "null" in ticket["bol"] and "oxy" in cleaned_text:
                temp = [ticket_text[x] for x in range(0, 4) if ticket_text[x].isdigit()]

                if len(temp) > 0:
                    for i in temp:
                        if i.startswith("1"):
                            ticket["bol"] = i

            # Generate training record and UUID
            ticket["source"] = ""
            raw_ticket_train = writeRawTraining(cleaned_text, ticket, ocr_features)

            training_id = raw_ticket_train["id"]
            image_filename = f"{training_id}.png"
            image_path = upload_path / image_filename

            # Save this PDF page as a processed PNG image
            if not cv2.imwrite(str(image_path), mod_img):
                raise RuntimeError("Failed to save PDF page image")

            # Use the same image for preview and training
            ticket["source"] = f"/uploads/{image_filename}"
            raw_ticket_train["source"] = ticket["source"]

            saveRawTraining(raw_ticket_train)
            ticket["training_id"] = training_id

            invalid = checkForInvalid(ticket)
            

            
            tickets.append({
                "page": page_number,
                "ticket_text": ticket_text,
                "ticket": ticket,
                "invalid": invalid,
                "source_url": ticket["source"]
            })

        return {
            "filename": file.filename,
            "tickets": tickets
        }
    else:

        
        
        # Convert bytes into NumPy array
        image_array = np.frombuffer(contents, np.uint8)

        # Decode into OpenCV image
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        mod_img = processJPEG(img)

        #Read ocr output
        ticket_text, ocr_features = read_paddle_output(mod_img)

        cleaned_text = cleanText(ticket_text)

        ticket = parseTicket(cleaned_text)

        if "null" in ticket["bol"] and "oxy" in cleaned_text:
            
            temp = [ticket_text[x] for x in range(0, 4) if ticket_text[x].isdigit()]

            if len(temp) > 0:
                for i in temp:
                    if i.startswith("1"):
                        ticket["bol"] = i

        # Generate training record and UUID
        ticket["source"] = ""
        raw_ticket_train = writeRawTraining(cleaned_text, ticket, ocr_features)

        #ticket unique id generated and saved image name to match id
        training_id = raw_ticket_train["id"]
        image_filename = f"{training_id}.png"
        image_path = upload_path / image_filename

        # Save processed image
        if not cv2.imwrite(str(image_path), mod_img):
            raise RuntimeError("Failed to save ticket image")

        # Use the same image for preview and training
        ticket["source"] = f"/uploads/{image_filename}"
        raw_ticket_train["source"] = ticket["source"]

        #appending raw training json with ticket info
        saveRawTraining(raw_ticket_train)

        #setting ticket id to generated id
        ticket["training_id"] = training_id

        invalid = checkForInvalid(ticket)

        return {
            "filename": image_filename,
            "ticket_text": ticket_text,
            "ticket": ticket,
            "invalid": invalid,
            "source_url": ticket['source']
        }
class SaveTicketsRequest(BaseModel):

    pad_name: str
    tickets: list[dict] #tickets in table
    existing_tickets: list[dict] # tickets in jason

@app.post("/generate-csv")
def generate_csv(data: SaveTicketsRequest):

    #pulling pad name and data and existing tickets
    pad_name = data.pad_name.strip()
    tickets = data.tickets
    existing_data = data.existing_tickets

    if not isinstance(existing_data, list):
        existing_data = []

    if not pad_name:
        return {
            "success": False,
            "message": "Pad name is required."
        }


    bols = []
    #extracting bols from json list
    for ticket in existing_data:

        bol = ticket.get("BOL","").strip()

        if bol:
            bols.append(bol)

    tableTickets = {}

    #current Table tickets
    for index, ticket in enumerate(tickets, start=1):
        bol = str(ticket.get("bol", "")).strip()

        if not bol:
            continue
        tableTickets.setdefault(bol,[]).append(index)

    duplicates = []

    #Duplicates check in table
    for bol, row in tableTickets.items():

        if len(row) > 1:

            #logging duplicate bol and row number
            duplicates.append({"bol": bol, "rows": row, "type": "Current Table"})

    if duplicates:

        return {
            "success": False,
            "duplicates": duplicates
        }
    
    #Checking duplicates against jason file
    for bol, rows in tableTickets.items():

        if bol in bols:

            duplicates.append({
                "bol": bol,
                "rows": rows,
                "type": "JSON"
            })

    clean_tickets = []

    if duplicates:
        return {
                    "success": False,
                    "duplicates": duplicates
                }
    else:
        

        for ticket in tickets:

            clean_ticket = {
                "Silo": ticket.get("silo", ""),
                "Sand Type": ticket.get("sandType", ""),
                "Carrier": ticket.get("carrier", ""),
                "Weight": ticket.get("weight", ""),
                "BOL": ticket.get("bol", ""),
                "Truck": ticket.get("truck", ""),
                "PO": ticket.get("po", ""),
                "Date": ticket.get("date", ""),
                "Time": ticket.get("time", ""),
                "Facility": ticket.get("facility", "")
            }

            clean_tickets.append(clean_ticket)

        existing_data.extend(clean_tickets)

    csv_output = io.StringIO()

    fieldnames = [
        "Silo",
        "Sand Type",
        "Carrier",
        "Weight",
        "BOL",
        "Truck",
        "PO",
        "Date",
        "Time",
        "Facility"
    ]

    writer = csv.DictWriter(
        csv_output,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(existing_data)


    return {
        "success": True,
        "message": f"{len(clean_tickets)} tickets processed successfully.",
        "tickets": existing_data,
        "csv": csv_output.getvalue()
    }


#Matching entered tickets to xiq
@app.post("/match-xiq-csv")
async def match_xiq_export(xiq_export: UploadFile = File(...),currentTable: str = Form(...)):

    xiq_file = xiq_export.file

    table_data = json.loads(currentTable)
    table_df = pd.DataFrame(table_data)

    results = match_xiq(xiq_file,table_df)

    return results

@app.post("/send-verified-training")
async def send_verified_training(verTickets: list[dict] = Body(..., embed=True)):

    with open(train_raw_file, 'r', encoding='utf-8') as file:
        train_data = json.load(file)

    for verTicket  in verTickets:
        for rawTicket in train_data:
            
            if rawTicket['id'] == verTicket['training_id']:

                rawTicket['verified_bol'] = verTicket['bol']
                rawTicket['verified_weight'] = verTicket['weight']
                rawTicket['verified_po'] = verTicket['po']
                rawTicket['verified_truck'] = verTicket['truck']
                rawTicket['verified_carrier'] = verTicket['carrier']
                rawTicket['verified_facility'] = verTicket['facility']

                break
        

    with open(train_raw_file, "w", encoding="utf-8") as file:
            json.dump(train_data, file, indent=4)

    return {"success" : True}



if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
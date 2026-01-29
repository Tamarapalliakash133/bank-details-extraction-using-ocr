import os 
from dotenv import load_dotenv
load_dotenv()
from PIL import Image
import cv2
import pytesseract
from pydantic import BaseModel,Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openpyxl import Workbook

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model = "gpt-4.1-mini")


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def image_pre(image):
    img = Image.open(image)
    return img

images = image_pre("WhatsApp Image 2026-01-29 at 9.37.07 PM.jpeg")

text = pytesseract.image_to_string(images,lang = "eng")

class extract(BaseModel):
    accountholder_name:str = Field(description = "account holder name in the bank with any mr or miss ")
    account_number:int = Field(description = "account number in the bank")
    ifsc_code:str = Field(description = "IFSC code of the bank")
    bank_name:str = Field(description = "name of the bank")


temp = ChatPromptTemplate.from_messages([
    ("system","you are for to give the details"),
    ("user","{input}")
])

structure = model.with_structured_output(extract)

chain = temp | structure

res = chain.invoke({"input" : text})


load = Workbook()
sheet = load.active
sheet.title = "bank-excelsheet"

sheet.append(["Account-Holder","Account-Number","IFSC Code","Bank Name"])

sheet.append([res.accountholder_name,res.account_number,res.ifsc_code,res.bank_name])

load.save("bank_details.xlsx")
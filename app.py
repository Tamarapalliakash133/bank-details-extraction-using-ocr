from flask import Flask, request, render_template
from dotenv import load_dotenv
import os

from PIL import Image
import pytesseract

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from openpyxl import load_workbook


load_dotenv()


app = Flask(__name__)


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


model = ChatOpenAI(model="gpt-4.1-mini")


class Extract(BaseModel):
    accountholder_name: str = Field(description="Account holder name")
    account_number: int = Field(description="Account number")
    ifsc_code: str = Field(description="IFSC code")
    bank_name: str = Field(description="Bank name")


prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract bank details from the given text"),
    ("user", "{input}")
])
done = model.with_structured_output(Extract)
chain = prompt | done


@app.route("/", methods=["GET"])
def index():
    return render_template("akash.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["passbook"]

    
    image = Image.open(file)
    text = pytesseract.image_to_string(image, lang="eng")

  
    res = chain.invoke({"input": text})

    
    wb = load_workbook("bank_details.xlsx")
    sheet = wb.active



    sheet.append([
        res.accountholder_name,
        res.account_number,
        res.ifsc_code,
        res.bank_name
    ])

    wb.save("bank_details.xlsx")

    return render_template("thanks.html")


if __name__ == "__main__":
    app.run(debug=True)

import discord
from io import BytesIO, StringIO
from typing import List, Dict
import base64
from pdfminer.high_level import extract_text_to_fp, extract_pages
from pdfminer.layout import LAParams, LTTextContainer, LTImage
from PIL import Image
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    output_string = StringIO()
    laparams = LAParams()
    extract_text_to_fp(pdf_file, output_string, laparams=laparams, output_type='text', codec=None)
    return output_string.getvalue()

def extract_images_from_pdf(pdf_file: BytesIO) -> List[str]:
    images = []
    for page_layout in extract_pages(pdf_file):
        for element in page_layout:
            if isinstance(element, LTImage):
                try:
                    image = Image.open(BytesIO(element.stream.get_data()))
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    base64_encoded = base64.b64encode(img_byte_arr).decode('utf-8')
                    images.append(base64_encoded)
                except Exception as e:
                    logger.error(f"Error processing image: {e}")
    return images

def process_excel(file_bytes: bytes) -> str:
    try:
        df = pd.read_excel(BytesIO(file_bytes))
        return df.to_string(index=False)
    except Exception as e:
        logger.error(f"Error processing Excel file: {e}")
        return f"Error processing Excel file: {str(e)}"

async def process_file(file: discord.Attachment, user_id: str, storage) -> List[Dict[str, any]]:
    content = []
    file_bytes = await file.read()
   
    # store the attachment and get its ID
    attachment_id = await storage.store_attachment(user_id, file.filename, file_bytes)
   
    if file.filename.lower().endswith('.pdf'):
        file_io = BytesIO(file_bytes)
        text = extract_text_from_pdf(file_io)
        images = extract_images_from_pdf(BytesIO(file_bytes))  # create a new BytesIO object
        content.append({"type": "text", "text": f"PDF Content:\n{text}"})
        for image in images[:20]:  # limit to 20 images due to API constraints
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image}})
    elif file.filename.lower().endswith(('.xlsx', '.xls')):
        excel_content = process_excel(file_bytes)
        content.append({"type": "text", "text": f"Excel Content:\n{excel_content}"})
    elif file.content_type.startswith('image/'):
        base64_encoded = base64.b64encode(file_bytes).decode('utf-8')
        content.append({"type": "image", "source": {"type": "base64", "media_type": file.content_type, "data": base64_encoded}})
    else:
        try:
            text = file_bytes.decode('utf-8')
            content.append({"type": "text", "text": f"File Content:\n{text}"})
        except UnicodeDecodeError:
            # if we can't decode it as text, we'll treat it as binary data
            content.append({"type": "text", "text": f"Binary file: {file.filename}"})
   
    logger.debug(f"Processed file {file.filename} for user {user_id}")
    return content
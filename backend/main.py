from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfWriter, PdfReader
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Serve static files like PDFs, HTML, CSS, and JS
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Ensure output PDF is stored in a publicly accessible directory
OUTPUT_FOLDER = Path("frontend/static")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def get_index():
    return FileResponse("frontend/index.html")

@app.post("/convert/")
async def convert_images_to_pdf(files: list[UploadFile] = File(...)):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")
        
        pdf_writer = PdfWriter()

        # Process each file
        for file in files:
            logging.info(f"Processing file: {file.filename}")

            # Validate image format
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                logging.warning(f"Invalid file type: {file.filename}")
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a valid image format.")

            try:
                # Open and convert the image
                image = Image.open(file.file)
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # Convert image to PDF
                pdf_io = BytesIO()
                image.save(pdf_io, format='PDF')
                pdf_io.seek(0)
                pdf_writer.append_pages_from_reader(PdfReader(pdf_io))
            except Exception as e:
                logging.error(f"Failed to process image {file.filename}: {e}")
                raise HTTPException(status_code=400, detail=f"Error processing {file.filename}")

        # Save the generated PDF in the frontend/static/ folder
        output_path = OUTPUT_FOLDER / "output.pdf"
        with open(output_path, "wb") as pdf_file:
            pdf_writer.write(pdf_file)

        logging.info(f"PDF successfully created: {output_path}")
        return {"download_url": "/static/output.pdf"}

    except HTTPException as http_err:
        logging.error(f"HTTP Error: {http_err.detail}")
        raise http_err
    except Exception as e:
        logging.error(f"Unexpected Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to convert images. Please try again later.")

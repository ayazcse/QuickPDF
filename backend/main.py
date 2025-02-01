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

# Serve static files like HTML, CSS, JS
app.mount("/static", StaticFiles(directory="frontend"), name="static")

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

            # Check if the file is a valid image (JPEG, PNG, etc.)
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                logging.warning(f"Invalid file type: {file.filename}")
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a valid image format.")

            try:
                # Open the image using PIL
                image = Image.open(file.file)
            except Exception as e:
                logging.error(f"Failed to open image {file.filename}: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to open image {file.filename}. Please check the file format.")

            # Convert the image to RGB if it’s not in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert image to PDF and add to the PDF writer
            pdf_io = BytesIO()
            image.save(pdf_io, format='PDF')
            pdf_io.seek(0)
            pdf_writer.append_pages_from_reader(PdfReader(pdf_io))

        # Ensure the "backend" directory exists (case-sensitive folder name)
        output_dir = Path("backend")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save the generated PDF
        output_path = output_dir / "output.pdf"
        with open(output_path, "wb") as pdf_file:
            pdf_writer.write(pdf_file)

        logging.info(f"PDF successfully created: {output_path}")
        return FileResponse(output_path, media_type='application/pdf', filename="output.pdf")

    except HTTPException as http_err:
        logging.error(f"HTTP Error: {http_err.detail}")
        raise http_err
    except Exception as e:
        logging.error(f"Error during conversion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to convert images. Please try again later.")

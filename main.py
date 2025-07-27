from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import subprocess
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.pgm")
            output_path = os.path.join(tmpdir, "output.svg")

            # Open image and convert to grayscale + PGM format for potrace
            image = Image.open(await file.read()).convert("L")
            image.save(input_path, format="PPM")  # PPM/PGM are supported formats for potrace

            # Run potrace CLI to generate SVG
            subprocess.run(["potrace", "-s", "-o", output_path, input_path], check=True)

            # Read and return SVG content
            with open(output_path, "r") as f:
                svg_data = f.read()

        return svg_data

    except Exception as e:
        return {"error": str(e)}

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import potrace
import numpy as np
import io

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("L")  # Grayscale
        bw = image.point(lambda x: 0 if x < 128 else 1, '1')  # Binarize
        bitmap = potrace.Bitmap(np.array(bw))
        path = bitmap.trace()

        svg_output = io.StringIO()
        svg_output.write('<?xml version="1.0" standalone="no"?>\n')
        svg_output.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"\n')
        svg_output.write('"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n')
        svg_output.write(f'<svg width="{image.width}" height="{image.height}" xmlns="http://www.w3.org/2000/svg" version="1.0">\n')

        for curve in path:
            svg_output.write('<path d="')
            start = curve.start_point
            svg_output.write(f'M {start[0]} {start[1]} ')
            for segment in curve:
                if segment.is_corner:
                    c = segment.c
                    svg_output.write(f'L {c[1][0]} {c[1][1]} ')
                else:
                    c = segment.c
                    svg_output.write(f'C {c[0][0]} {c[0][1]}, {c[1][0]} {c[1][1]}, {c[2][0]} {c[2][1]} ')
            svg_output.write('" fill="black" />\n')

        svg_output.write('</svg>\n')
        return svg_output.getvalue()
    except Exception as e:
        return {"error": str(e)}
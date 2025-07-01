from fastapi import FastAPI, File, UploadFile, Header
from fastapi.responses import JSONResponse, FileResponse
import os, uuid
import whisper

app = FastAPI()
model = whisper.load_model("base")
API_KEY = "rishaply123"

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...), authorization: str = Header(None)):
    if authorization != API_KEY:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    os.makedirs("uploads", exist_ok=True)
    name = f"{uuid.uuid4().hex}_{file.filename}"
    path = f"uploads/{name}"
    with open(path, "wb") as f:
        f.write(await file.read())

    result = model.transcribe(path)
    txt_file = f"{path}.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    os.system(f"whisper {path} --model base --output_format vtt --output_dir uploads")
    os.remove(path)

    return {
        "message": "Transcription complete.",
        "text": f"/download/txt/{os.path.basename(txt_file)}",
        "vtt": f"/download/vtt/{os.path.basename(path)}.vtt"
    }

@app.get("/download/txt/{filename}")
def txt(filename: str):
    return FileResponse(f"uploads/{filename}", media_type="text/plain")

@app.get("/download/vtt/{filename}")
def vtt(filename: str):
    return FileResponse(f"uploads/{filename}", media_type="text/vtt")
  

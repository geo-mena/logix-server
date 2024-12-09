from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.log_processor import process_log_file
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Log Processor Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-log/")
async def process_log(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        content = await file.read()
        decoded_content = content.decode('utf-8')
        
        # Procesar el contenido
        result = process_log_file(decoded_content)
        if not result:
            return {
                "success": True,
                "data": {},
                "message": "No data was found to process in the log file"
            }
        
        return {
            "success": True,
            "data": result
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
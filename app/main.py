from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.analyze_terminals import extract_date_from_header
from app.services.analyze_terminals import analyze_terminals_dates
from app.services.log_processor import process_log_file
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler() 
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Log Processor Service",
    description="Servicio para procesar archivos de log y analizar terminales",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta para procesar un archivo de log
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

# Ruta para analizar terminales
@app.post("/analyze-terminals/")
async def analyze_terminals(file: UploadFile = File(...)):
    try:
        content = await file.read()
        decoded_content = content.decode('utf-8')
        reference_date = extract_date_from_header(decoded_content)
        
        # Analizar el contenido
        results = analyze_terminals_dates(decoded_content)
        
        return {
            "success": True,
            "data": {
                "counts": results,
                "details": {
                    "date_analyzed": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "filename": file.filename
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ruta para verificar el estado de la aplicación
@app.get("/health")
async def health_check():
    return {"status": "ok"}
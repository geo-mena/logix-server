from datetime import datetime, timedelta
from typing import Dict
import re

# función para extraer la fecha del encabezado
def extract_date_from_header(content: str) -> datetime:
    """Extrae la fecha del encabezado del documento."""
    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 
              'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']

    lines = content.splitlines()
    for line in lines:
        # Buscar la línea que contiene la fecha
        if any(month in line for month in months):

            normalized_line = ' '.join(line.split())
            match = re.search(r'(\w+ \d{1,2}, \d{4})', normalized_line)

            if match:
                try:
                    date_str = ' '.join(match.group(1).split())
                    return datetime.strptime(match.group(1), '%B %d, %Y')
                except ValueError as e:
                    raise ValueError(f"Error parsing date from header: {e}")
    raise ValueError("No se encontró fecha en el encabezado del documento")

# función para analizar las terminales
def analyze_terminals_dates(content: str) -> Dict:
    counts = {
        "ANTERIORES A HOY": 0,
        "DEL DÍA DE MAÑANA": 0,
        "MISMO DÍA": 0
    }
    
    try:
        reference_date = extract_date_from_header(content)
        file_date = reference_date.strftime('%Y-%m-%d')
        today_str = reference_date.strftime('%y%m%d')
        tomorrow_str = (reference_date + timedelta(days=1)).strftime('%y%m%d')

        # Usar una lista para mantener un mejor control de las terminales
        terminals = []
        for line in content.splitlines():
            if not line.strip() or any(x in line for x in ['TERMINAL', '----', 'PAGINA']):
                continue

            try:
                # Normalizar espacios y tabulaciones
                line = ' '.join(line.split())
                
                # Verificar si es una línea válida
                if not re.search(r'\d{6}$', line.strip()):
                    continue

                # Procesar la línea según su tipo
                if '0A9\t' in line or '0A9 ' in line:
                    terminal = '0A9 001'
                    posteo = line.strip().split()[-1]
                elif 'IJQ-' in line:
                    parts = line.split()
                    terminal = parts[0]
                    posteo = parts[-1]
                else:
                    parts = line.split()
                    if len(parts) < 7:  # Verificar que tenga todos los campos necesarios
                        continue
                    terminal = parts[0]
                    posteo = parts[-1]

                if len(posteo) == 6 and posteo.isdigit():
                    terminals.append({
                        'terminal': terminal,
                        'posteo': posteo
                    })

            except Exception as e:
                continue

        # Clasificar terminales
        for term in terminals:
            posteo = term['posteo']
            if posteo == today_str:
                counts["MISMO DÍA"] += 1
            elif posteo == tomorrow_str:
                counts["DEL DÍA DE MAÑANA"] += 1
            else:
                counts["ANTERIORES A HOY"] += 1

        counts["TOTAL DE TERMINALES"] = len(terminals)

        return {
            "counts": counts,
            "file_date": file_date 
        }
    except Exception as e:
        raise ValueError(f"Error en el análisis: {str(e)}")

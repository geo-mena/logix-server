from datetime import datetime
from typing import Dict, Any
import re

def parse_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, '%H:%M:%S')

def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

def process_log_file(content: str) -> Dict[str, Any]:
    stations = {}
    lines = content.splitlines()
    
    for i in range(len(lines)):
        line = lines[i].strip()
        
        # Buscar líneas que contengan timestamp con el formato específico
        timestamp_match = re.match(r'^\d{2}-\d{1,2}-\d{2};(\d{2}:\d{2}:\d{2})', line)
        if timestamp_match:
            # Extraer timestamp
            timestamp = timestamp_match.group(1)
            
            # Buscar información de proceso en la siguiente línea
            if i + 1 < len(lines):
                process_line = lines[i + 1]
                process_match = re.search(r'FROM:\s+(P[1-9][A-Z]\^HISO\d+)', process_line)
                process = process_match.group(1) if process_match else ''
            
            # Buscar información de estación y estado en la línea siguiente
            if i + 2 < len(lines):
                station_line = lines[i + 2]
                station_match = re.search(r'STATION\s+(S[1-9][A-Z]H[A-Z]\d+T[1-9])\s+marked\s+(up|down)', station_line)
                
                if station_match:
                    station = station_match.group(1)
                    status = station_match.group(2)
                    
                    # Inicializar estación si no existe
                    if station not in stations:
                        stations[station] = {
                            "proceso": process,
                            "cantidad_caidas": 0,
                            "primera_caida": None,
                            "ultima_subida": None,
                            "tiempo_afectado": 0,
                            "current_down_time": None
                        }
                    
                    if status == 'down':
                        stations[station]['cantidad_caidas'] += 1
                        if stations[station]['primera_caida'] is None:
                            stations[station]['primera_caida'] = timestamp
                        stations[station]['current_down_time'] = timestamp
                    
                    elif status == 'up':
                        stations[station]['ultima_subida'] = timestamp
                        if stations[station]['current_down_time']:
                            down_time = parse_time(stations[station]['current_down_time'])
                            up_time = parse_time(timestamp)
                            diff = (up_time - down_time).total_seconds()
                            stations[station]['tiempo_afectado'] += int(diff)
    
    # Formatear el resultado final
    for station_data in stations.values():
        station_data['tiempo_afectado'] = format_duration(station_data['tiempo_afectado'])
        # Eliminar variable temporal
        if 'current_down_time' in station_data:
            del station_data['current_down_time']

    # Ordenar estaciones por cantidad de caídas
    stations = dict(sorted(
        stations.items(), 
        key=lambda item: item[1]['cantidad_caidas'], 
        reverse=True
    ))
    
    return stations
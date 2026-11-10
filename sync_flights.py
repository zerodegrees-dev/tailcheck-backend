import os
import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_incidents():
    print("Iniciando extracción de incidentes desde The Aviation Herald...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    incidents_added = 0
    
    try:
        response = requests.get("https://avherald.com/", headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos en los enlaces
            for a in soup.find_all('a'):
                text = a.get_text(separator=" ", strip=True)
                text = " ".join(text.split()) # Limpiamos dobles espacios
                
                if " at " in text and " on " in text:
                    # Cortamos por la coma para quitar el final (ej. ", hydraulic problems")
                    main_text = text.split(",", 1)[0].strip()
                    
                    try:
                        # Extraemos las 3 partes clave (Operador/Modelo, Lugar, Fecha)
                        match = re.search(r'^(.*?)\s+at\s+(.*?)\s+on\s+(.*)', main_text)
                        if match:
                            op_and_model = match.group(1).strip()
                            location = match.group(2).strip()
                            date = match.group(3).strip()
                            
                            # Separamos la aerolínea y el modelo (la última palabra antes del 'at')
                            parts = op_and_model.rsplit(" ", 1)
                            if len(parts) == 2:
                                operator, model = parts[0].strip(), parts[1].strip()
                                
                                data = {
                                    "incident_date": date,
                                    "aircraft_model": model,
                                    "operator": operator,
                                    "location": location
                                }
                                
                                supabase.table('aircraft_incidents').upsert(data).execute()
                                incidents_added += 1
                    except Exception as parse_err:
                        pass # Si una línea está mal escrita en la web, la ignoramos
        else:
            print(f"Error de conexión: {response.status_code}")
            
    except Exception as e:
        print(f"Fallo general en la extracción: {e}")

    print(f"Sincronización finalizada: {incidents_added} incidentes procesados y guardados.")

if __name__ == "__main__":
    fetch_incidents()

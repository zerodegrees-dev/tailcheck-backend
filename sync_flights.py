import os
import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_incidents():
    print("Iniciando pipeline de extracción de incidentes...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    incidents_added = 0
    
    # INTENTO 1: The Aviation Herald
    try:
        # Añadimos una cookie genérica por si activan banners de consentimiento
        response = requests.get("https://avherald.com/", headers=headers, cookies={'cookie_consent': '1'}, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a in soup.find_all('a'):
                # El separator=" " evita que las imágenes peguen las palabras
                text = a.get_text(separator=" ", strip=True)
                text = " ".join(text.split()) # Normaliza espacios dobles
                
                if ("Incident:" in text or "Crash:" in text) and " at " in text and " on " in text:
                    try:
                        # Extraemos mediante grupos Regex
                        match = re.search(r'(?:Incident|Crash):\s*(.*?)\s+at\s+(.*?)\s+on\s+([^,]+)', text)
                        if match:
                            op_and_model = match.group(1).strip()
                            location = match.group(2).strip()
                            date = match.group(3).strip()
                            
                            # Separamos aerolínea y modelo
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
                    except Exception:
                        pass
                        
    except Exception as e:
        print(f"Fallo en AvHerald: {e}")

    # INTENTO 2 (FALLBACK): AeroInside (Solo se ejecuta si AvHerald devuelve 0)
    if incidents_added == 0:
        print("AvHerald devolvió 0 incidentes. Ejecutando fallback con AeroInside...")
        try:
            response_ai = requests.get("https://www.aeroinside.com/", headers=headers, timeout=15)
            if response_ai.status_code == 200:
                soup_ai = BeautifulSoup(response_ai.text, 'html.parser')
                
                for h2 in soup_ai.find_all('h2'):
                    a = h2.find('a')
                    if a:
                        text = a.get_text(separator=" ", strip=True)
                        text = " ".join(text.split())
                        
                        if " at " in text and " on " in text:
                            try:
                                match = re.search(r'(.*?)\s+at\s+(.*?)\s+on\s+([^,]+)', text)
                                if match:
                                    op_and_model = match.group(1).strip()
                                    location = match.group(2).strip()
                                    date = match.group(3).strip()
                                    
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
                            except Exception:
                                pass
        except Exception as e:
            print(f"Fallo en AeroInside: {e}")

    print(f"Sincronización finalizada: {incidents_added} incidentes procesados y guardados.")

if __name__ == "__main__":
    fetch_incidents()

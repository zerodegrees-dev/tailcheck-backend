import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_incidents():
    print("Conectando con The Aviation Herald (alternativa sin bloqueos)...")
    
    # Cabecera estándar
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get("https://avherald.com/", headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Error web: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        incidents_added = 0
        
        # En AvHerald, los incidentes siempre son enlaces con una estructura fija.
        # Ejemplo: "Incident: Ryanair B738 at London on Oct 11th 2026, bird strike"
        for a in soup.find_all('a'):
            text = a.get_text(strip=True)
            
            if ":" in text and " at " in text and " on " in text:
                try:
                    # 1. Separamos el tipo de evento (Incident/Crash)
                    main_part = text.split(":", 1)[1].strip()
                    
                    # 2. Quitamos la descripción final que va tras la coma
                    event_info = main_part.split(",", 1)[0].strip()
                    
                    # 3. Extraemos las partes clave usando ' at ' y ' on '
                    if " at " in event_info and " on " in event_info:
                        op_and_model, rest = event_info.split(" at ", 1)
                        location, date = rest.split(" on ", 1)
                        
                        # 4. El modelo es la última palabra antes del 'at' (ej. B738, A320)
                        op_parts = op_and_model.strip().rsplit(" ", 1)
                        if len(op_parts) == 2:
                            operator = op_parts[0]
                            model = op_parts[1]
                            
                            data = {
                                "incident_date": date.strip(),
                                "aircraft_model": model.strip(),
                                "operator": operator.strip(),
                                "location": location.strip()
                            }
                            
                            # Upsert inserta si es nuevo, ignora si ya existe (gracias a UNIQUE)
                            supabase.table('aircraft_incidents').upsert(data).execute()
                            incidents_added += 1
                except Exception:
                    # Ignoramos si algún titular se sale de la norma o si la base de datos ya lo tiene
                    pass

        print(f"Sincronización finalizada: {incidents_added} incidentes procesados y guardados.")
        
    except Exception as e:
        print(f"Error fatal en la ejecución: {e}")

if __name__ == "__main__":
    fetch_incidents()

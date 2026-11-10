import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_incidents():
    print("Conectando con Aviation Safety Network...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # URL de la base de datos de incidentes (Wikibase)
    response = requests.get("https://aviation-safety.net/wikibase/", headers=headers)
    
    if response.status_code != 200:
        print(f"Error accediendo a la web: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    
    if not table:
        print("No se encontró la tabla de datos.")
        return

    rows = table.find_all('tr')[1:] # Saltamos la cabecera
    incidents_added = 0
    
    for row in rows[:30]: # Analizamos los 30 incidentes más recientes
        cols = row.find_all('td')
        if len(cols) >= 6:
            incident_date = cols[0].text.strip()
            model = cols[1].text.strip()
            operator = cols[3].text.strip()
            location = cols[5].text.strip()
            
            data = {
                "incident_date": incident_date,
                "aircraft_model": model,
                "operator": operator if operator else "Desconocido",
                "location": location
            }

            try:
                # Upsert evita duplicados gracias a la restricción UNIQUE que creamos en SQL
                supabase.table('aircraft_incidents').upsert(data).execute()
                incidents_added += 1
            except Exception as e:
                pass # Ignoramos duplicados o errores menores de inserción

    print(f"Sincronización finalizada: {incidents_added} incidentes procesados.")

if __name__ == "__main__":
    fetch_incidents()

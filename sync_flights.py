import os
import cloudscraper
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_incidents():
    print("Conectando con Aviation Safety Network...")
    # Usamos cloudscraper para simular un navegador real y evitar bloqueos de Cloudflare
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    try:
        response = scraper.get("https://aviation-safety.net/wikibase/")
        
        if response.status_code != 200:
            print(f"Error web: {response.status_code}. Posible bloqueo activo.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            print("No se encontró la tabla de datos. El firewall nos ha devuelto otra página.")
            return

        rows = table.find_all('tr')[1:]
        incidents_added = 0
        
        for row in rows[:30]:
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
                    supabase.table('aircraft_incidents').upsert(data).execute()
                    incidents_added += 1
                except Exception as db_err:
                    print(f"Error insertando en base de datos: {db_err}")

        print(f"Sincronización finalizada: {incidents_added} incidentes procesados.")
        
    except Exception as e:
        print(f"Error fatal en la ejecución: {e}")

if __name__ == "__main__":
    fetch_incidents()

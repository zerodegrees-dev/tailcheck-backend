import os
import datetime
from supabase import create_client, Client

# Conectar de forma segura usando las variables de GitHub
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_and_store_flights():
    print("Iniciando sincronización de vuelos...")
    today = datetime.date.today().isoformat()
    
    # Aquí irá la llamada a la API de aviación (ej. OpenSky / Flightradar)
    # Por ahora inyectamos un dato de prueba para confirmar que la conexión funciona
    mock_data = {
        "flight_number": "IB3110",
        "departure_date": today,
        "tail_number": "EC-NBE",
        "aircraft_model": "Airbus A320neo"
    }

    # Insertar o actualizar (upsert) en la base de datos
    response = supabase.table('plane_assignments').upsert(mock_data).execute()
    
    if response.data:
        print(f"Sincronización exitosa: {len(response.data)} registros actualizados.")
    else:
        print("No se actualizaron registros.")

if __name__ == "__main__":
    fetch_and_store_flights()

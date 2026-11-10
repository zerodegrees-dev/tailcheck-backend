import requests
from bs4 import BeautifulSoup

def diagnostico():
    print("=== INICIANDO DIAGNÓSTICO DE RED DESDE GITHUB ACTIONS ===")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Test AvHerald
    print("\n--- Test AvHerald ---")
    try:
        r = requests.get("https://avherald.com/", headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Buscamos cualquier enlace que parezca un incidente
            enlaces = [a.get_text(separator=" ", strip=True) for a in soup.find_all('a') if " at " in a.get_text()]
            print(f"Posibles incidentes encontrados: {len(enlaces)}")
            for e in enlaces[:5]: 
                print(f"-> {e}")
        else:
            print(f"Respuesta bloqueada. Cabeceras devueltas: {r.headers.get('Server')}")
    except Exception as e:
        print(f"Error de conexión: {e}")

    # Test AeroInside
    print("\n--- Test AeroInside ---")
    try:
        r = requests.get("https://www.aeroinside.com/", headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            titulos = [h2.get_text(separator=" ", strip=True) for h2 in soup.find_all('h2')]
            print(f"Titulares H2 encontrados: {len(titulos)}")
            for t in titulos[:5]: 
                print(f"-> {t}")
        else:
            print(f"Respuesta bloqueada. Cabeceras devueltas: {r.headers.get('Server')}")
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    diagnostico()

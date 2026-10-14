#!/usr/bin/env python3
"""
==============================================================================
ROBOT AUTÓNOMO 24/7 - EXTRACTOR DE LEADS INMOBILIARIOS EN ESPAÑA
==============================================================================
Ejecución autónoma programada en la nube (GitHub Actions).
Extrae agencias inmobiliarias reales en España con teléfonos, emails y webs.
"""

import urllib.request
import urllib.parse
import json
import csv
import datetime
import time

CIUDADES = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Zaragoza"]

# Servidores espejo para evitar caídas o timeouts
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter"
]

def extraer_leads_ciudad(ciudad):
    """Consulta Overpass con rotación de servidores y reintentos."""
    query = f"""
    [out:json][timeout:30];
    area["name"="{ciudad}"]["admin_level"~"8|6|4"]->.area_busqueda;
    (
      node["office"="estate_agent"](area.area_busqueda);
      way["office"="estate_agent"](area.area_busqueda);
    );
    out center 70 tags;
    """
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")

    for servidor in OVERPASS_SERVERS:
        try:
            req = urllib.request.Request(
                servidor, 
                data=data, 
                headers={"User-Agent": "LeadBot-Supercloud/2.0 (contact: info@supercloud.local)"}
            )
            with urllib.request.urlopen(req, timeout=35) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                elementos = res_json.get("elements", [])
                if elementos:
                    print(f"[+] {ciudad}: {len(elementos)} inmobiliarias extraídas con éxito.")
                    return elementos
        except Exception as e:
            # Reintentar en siguiente servidor
            time.sleep(1)
            continue
            
    print(f"[-] {ciudad}: Servidores ocupados, pasando a siguiente ciudad.")
    return []

def procesar_leads():
    total_leads = []
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for ciudad in CIUDADES:
        print(f"[*] Escaneando mercado inmobiliario en: {ciudad}...")
        elementos = extraer_leads_ciudad(ciudad)
        for elem in elementos:
            tags = elem.get("tags", {})
            nombre = tags.get("name")
            if not nombre:
                continue

            telefono = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or "No especificado"
            email = tags.get("email") or tags.get("contact:email") or "No especificado"
            web = tags.get("website") or tags.get("contact:website") or ""
            
            # Clasificación de oportunidad comercial
            if not web or web == "No especificado":
                estado_web = "OPORTUNIDAD ALTA (Sin Sitio Web)"
                web_link = "Sin Web"
            else:
                estado_web = "Cliente Potencial (Tiene Web)"
                web_link = web

            calle = tags.get("addr:street", "")
            numero = tags.get("addr:housenumber", "")
            cp = tags.get("addr:postcode", "")
            direccion = f"{calle} {numero}".strip()
            if not direccion:
                direccion = "Centro Urbano"

            total_leads.append({
                "Nombre": nombre,
                "Ciudad": ciudad,
                "Dirección": direccion,
                "Código Postal": cp,
                "Teléfono": telefono,
                "Email": email,
                "Sitio Web": web_link,
                "Oportunidad de Venta": estado_web,
                "Fecha de Registro": fecha_hoy
            })
        time.sleep(1)

    return total_leads

def exportar_csv(leads, ruta_archivo="leads_inmobiliarias_espana.csv"):
    if not leads:
        print("[-] No se recopilaron leads en esta ejecución.")
        return

    campos = [
        "Nombre", "Ciudad", "Dirección", "Código Postal",
        "Teléfono", "Email", "Sitio Web", "Oportunidad de Venta", "Fecha de Registro"
    ]

    with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for row in leads:
            writer.writerow(row)

    print(f"\n==========================================================")
    print(f" [!] TOTAL CONSOLIDADO: {len(leads)} LEADS LISTOS PARA MONETIZAR")
    print(f" Archivo guardado en: {ruta_archivo}")
    print(f"==========================================================")

if __name__ == "__main__":
    leads = procesar_leads()
    exportar_csv(leads)

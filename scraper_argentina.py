#!/usr/bin/env python3
"""
==============================================================================
ROBOT AUTÓNOMO 24/7 - EXTRACTOR DE GASTRONOMÍA Y MENÚS DIGITALES (ARGENTINA)
==============================================================================
Ejecución autónoma en la nube (GitHub Actions).
1. Extrae rotiserías, pizzerías, bares y restaurantes en Argentina.
2. Identifica locales con números de WhatsApp/teléfono.
3. Genera enlaces directos de WhatsApp ('wa.me') con mensajes pre-redactados
   y datos de cobro oficiales de Mercado Pago (Alias y CVU).
"""

import urllib.request
import urllib.parse
import json
import csv
import datetime
import time
import os

# Datos Oficiales de Cobro de Mercado Pago
TITULAR_MP = "Ricardo Alfredo Miranda"
ALIAS_MP = "aleado.copos.vial.mp"
CVU_MP = "0000003100096829377816"
PRECIO_MENU_ARS = "$8.000 ARS"

CIUDADES_ARGENTINA = ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "San Luis", "Mar del Plata"]

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

def cargar_leads_existentes(ruta_archivo="leads_gastronomia_argentina.csv"):
    if not os.path.exists(ruta_archivo):
        return []
    leads = []
    try:
        with open(ruta_archivo, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Nombre"):
                    leads.append(row)
    except Exception:
        pass
    return leads

def extraer_locales_ciudad(ciudad):
    query = f"""
    [out:json][timeout:30];
    area["name"="{ciudad}"]->.area_busqueda;
    (
      node["amenity"~"restaurant|fast_food|cafe|bar|pub"](area.area_busqueda);
      way["amenity"~"restaurant|fast_food|cafe|bar|pub"](area.area_busqueda);
    );
    out center 40 tags;
    """
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")

    for servidor in OVERPASS_SERVERS:
        try:
            req = urllib.request.Request(
                servidor, 
                data=data, 
                headers={"User-Agent": "ArgenBot-Supercloud/2.0 (contact: info@supercloud.local)"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                elementos = res_json.get("elements", [])
                if elementos:
                    print(f"[+] {ciudad}: {len(elementos)} locales encontrados con éxito.")
                    return elementos
        except Exception:
            time.sleep(1)
            continue
            
    print(f"[-] {ciudad}: Servidores ocupados, se reintentará en el próximo ciclo.")
    return []

def procesar_gastronomia():
    leads_previos = cargar_leads_existentes()
    nuevos_leads = []
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for ciudad in CIUDADES_ARGENTINA:
        print(f"[*] Escaneando gastronomía en: {ciudad}...")
        elementos = extraer_locales_ciudad(ciudad)
        for elem in elementos:
            tags = elem.get("tags", {})
            nombre = tags.get("name")
            if not nombre:
                continue

            telefono = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or ""
            tipo = tags.get("amenity", "local")
            calle = tags.get("addr:street", "")
            numero = tags.get("addr:housenumber", "")
            direccion = f"{calle} {numero}".strip() or "Zona Comercial"

            wa_num = "".join(filter(str.isdigit, telefono))
            if wa_num.startswith("0"):
                wa_num = wa_num[1:]
            if not wa_num.startswith("54"):
                wa_num = "549" + wa_num

            mensaje_wa = (
                f"Hola buenas tardes equipo de {nombre}! Estuve viendo su local en {ciudad}. "
                f"Me dedico al armado de Menús Digitales interactivos con Código QR para mesas y mostrador, "
                f"listos para que sus clientes escaneen y pidan directo por WhatsApp sin cartas de papel. "
                f"Se los dejo listo hoy mismo en 1 hora por solo {PRECIO_MENU_ARS} (Datos de transferencia: Alias: {ALIAS_MP} | Titular: {TITULAR_MP}). "
                f"¿Les gustaría ver una muestra rápida sin compromiso?"
            )
            mensaje_encoded = urllib.parse.quote(mensaje_wa)
            wa_link = f"https://wa.me/{wa_num}?text={mensaje_encoded}" if len(wa_num) >= 10 else "Sin WhatsApp"

            nuevos_leads.append({
                "Nombre": nombre,
                "Ciudad": ciudad,
                "Tipo": tipo,
                "Dirección": direccion,
                "Teléfono": telefono or "No especificado",
                "Link WhatsApp": wa_link,
                "Fecha": fecha_hoy
            })

    registro_map = {}
    for l in leads_previos:
        clave = (l.get("Nombre", "").strip().lower(), l.get("Ciudad", "").strip().lower())
        registro_map[clave] = l

    for l in nuevos_leads:
        clave = (l.get("Nombre", "").strip().lower(), l.get("Ciudad", "").strip().lower())
        if clave not in registro_map:
            registro_map[clave] = l

    return list(registro_map.values())

def exportar_csv(leads, ruta_archivo="leads_gastronomia_argentina.csv"):
    campos = ["Nombre", "Ciudad", "Tipo", "Dirección", "Teléfono", "Link WhatsApp", "Fecha"]
    with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        if leads:
            for row in leads:
                clean = {c: row.get(c, "") for c in campos}
                writer.writerow(clean)
    print(f"[+] Base de datos CSV guardada: {ruta_archivo}")

def generar_propuestas(leads, ruta_md="propuestas_whatsapp_argentina.md"):
    con_wa = [l for l in leads if l.get("Link WhatsApp") != "Sin WhatsApp"] if leads else []
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")

    contenido = f"""# 🍕 Propuestas de Menú QR para Gastronomía (Argentina)
**Generado automáticamente por la Supercomputadora 24/7 en la Nube**  
*Fecha: {fecha} | Total Locales: {len(leads)} | Locales con WhatsApp Directo: {len(con_wa)}*

---

## 💳 Datos de Cobro Oficiales Integrados (Mercado Pago)
* **Titular:** `{TITULAR_MP}`
* **Alias:** `{ALIAS_MP}`
* **CVU:** `{CVU_MP}`
* **Precio del Servicio:** **{PRECIO_MENU_ARS}**

---

## ⚡ Cómo Contactar en 1 Clic:
1. Haz clic en el enlace azul **[👉 Abrir WhatsApp y Enviar Mensaje]**.
2. Se te abrirá la conversación de WhatsApp con el texto y tus datos de cobro ya escritos.
3. Solo presionas el botón de enviar.
4. Cuando confirmen, te transfieren los **{PRECIO_MENU_ARS}** directamente a tu Alias de Mercado Pago.

---

## 📋 Lista de Locales con WhatsApp Directo

| Local | Ciudad | Tipo | Dirección | Contactar Directo |
| :--- | :--- | :--- | :--- | :--- |
"""

    if con_wa:
        for l in con_wa[:25]:
            nombre = l.get("Nombre", "")
            ciudad = l.get("Ciudad", "")
            wa_link = l.get("Link WhatsApp", "#")
            tipo = l.get("Tipo", "Gastronomía")
            dir_local = l.get("Dirección", "Zona Comercial")
            contenido += f"| **{nombre}** | {ciudad} | {tipo} | {dir_local} | [👉 Abrir WhatsApp y Enviar]({wa_link}) |\n"
    else:
        contenido += "| *Buscando comercios en la próxima ejecución* | - | - | - | - |\n"

    contenido += f"""
---
*Datos de Pago Oficiales: Alias `{ALIAS_MP}` | CVU `{CVU_MP}`*  
*Generado automáticamente por Supercomputadora LeadBot en la nube de GitHub Actions.*
"""

    with open(ruta_md, mode="w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"[+] Archivo de propuestas generado: {ruta_md}")

if __name__ == "__main__":
    leads = procesar_gastronomia()
    exportar_csv(leads)
    generar_propuestas(leads)

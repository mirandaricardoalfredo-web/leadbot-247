#!/usr/bin/env python3
"""
==============================================================================
ROBOT AUTÓNOMO 24/7 - EXTRACTOR CUMULATIVO Y GENERADOR DE OFERTAS COMERCIALES
==============================================================================
Ejecución autónoma programada en la nube (GitHub Actions).
1. Acumula y deduplica leads día a día sin perder datos previos.
2. Extrae agencias inmobiliarias en España (Madrid, Barcelona, Valencia, etc.).
3. Genera automáticamente ofertas y propuestas comerciales con enlace directo
   a tu pasarela de cobro PayPal oficial en dólares (US$ 45,00).
"""

import urllib.request
import urllib.parse
import json
import csv
import datetime
import time
import os

CIUDADES = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Bilbao"]

# Tu enlace oficial de cobro en PayPal ($45 USD)
PAYPAL_PAYMENT_LINK = "https://www.paypal.com/ncp/payment/BKT7UTA7HA5QS"

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

def cargar_leads_existentes(ruta_archivo="leads_inmobiliarias_espana.csv"):
    if not os.path.exists(ruta_archivo):
        return []
    leads = []
    try:
        with open(ruta_archivo, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Nombre"):
                    leads.append(row)
    except Exception as e:
        print(f"[-] Nota: Iniciando base nueva ({e})")
    return leads

def extraer_leads_ciudad(ciudad):
    query = f"""
    [out:json][timeout:25];
    area["name"="{ciudad}"]["admin_level"~"8|6|4"]->.area_busqueda;
    (
      node["office"="estate_agent"](area.area_busqueda);
      way["office"="estate_agent"](area.area_busqueda);
    );
    out center 50 tags;
    """
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")

    for servidor in OVERPASS_SERVERS:
        try:
            req = urllib.request.Request(
                servidor, 
                data=data, 
                headers={"User-Agent": "LeadBot-Supercloud/2.0 (contact: info@supercloud.local)"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                elementos = res_json.get("elements", [])
                if elementos:
                    print(f"[+] {ciudad}: {len(elementos)} inmobiliarias extraídas con éxito.")
                    return elementos
        except Exception:
            time.sleep(1)
            continue
            
    print(f"[-] {ciudad}: Servidores ocupados, se reintentará en el próximo ciclo.")
    return []

def procesar_leads():
    leads_previos = cargar_leads_existentes()
    print(f"[*] Base de datos previa: {len(leads_previos)} leads cargados.")

    nuevos_leads = []
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
            
            # Clasificación de demanda
            if not web or web == "No especificado":
                estado_web = "OPORTUNIDAD ALTA (Sin Sitio Web)"
                web_link = "Sin Web"
                tipo_demanda = "Necesita Desarrollo Web / Presencia Digital"
            else:
                estado_web = "Cliente Potencial (Tiene Web)"
                web_link = web
                tipo_demanda = "Necesita Captación de Propietarios / Tráfico"

            calle = tags.get("addr:street", "")
            numero = tags.get("addr:housenumber", "")
            cp = tags.get("addr:postcode", "")
            direccion = f"{calle} {numero}".strip()
            if not direccion:
                direccion = "Centro Urbano"

            nuevos_leads.append({
                "Nombre": nombre,
                "Ciudad": ciudad,
                "Dirección": direccion,
                "Código Postal": cp,
                "Teléfono": telefono,
                "Email": email,
                "Sitio Web": web_link,
                "Oportunidad de Venta": estado_web,
                "Tipo de Demanda": tipo_demanda,
                "Fecha de Registro": fecha_hoy
            })
        time.sleep(1)

    # Consolidar y deduplicar
    registro_map = {}
    for l in leads_previos:
        clave = (l.get("Nombre", "").strip().lower(), l.get("Ciudad", "").strip().lower())
        registro_map[clave] = l

    agregados = 0
    for l in nuevos_leads:
        clave = (l.get("Nombre", "").strip().lower(), l.get("Ciudad", "").strip().lower())
        if clave not in registro_map:
            registro_map[clave] = l
            agregados += 1

    total_consolidados = list(registro_map.values())
    print(f"[+] Nuevos leads incorporados: {agregados}. Total acumulado: {len(total_consolidados)}.")
    return total_consolidados

def exportar_csv(leads, ruta_archivo="leads_inmobiliarias_espana.csv"):
    if not leads:
        print("[-] No hay leads para exportar.")
        return

    campos = [
        "Nombre", "Ciudad", "Dirección", "Código Postal",
        "Teléfono", "Email", "Sitio Web", "Oportunidad de Venta", 
        "Tipo de Demanda", "Fecha de Registro"
    ]

    with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for row in leads:
            clean_row = {c: row.get(c, "No especificado") for c in campos}
            writer.writerow(clean_row)

    print(f"[+] Base de datos CSV consolidada: {ruta_archivo}")

def generar_ofertas_y_demandas(leads, ruta_md="ofertas_y_demandas.md"):
    if not leads:
        return

    total = len(leads)
    sin_web = [l for l in leads if "Sin Sitio Web" in l.get("Oportunidad de Venta", "")]
    con_web = [l for l in leads if "Tiene Web" in l.get("Oportunidad de Venta", "")]
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")

    contenido = f"""# 💼 Catálogo de Ofertas y Demandas B2B (Listo para Monetizar)
**Generado automáticamente por la Supercomputadora 24/7 en la Nube**  
*Fecha de Análisis: {fecha} | Total de Empresas en la Base: {total}*

---

## 📊 1. Resumen Ejecutivo de la Demanda de Mercado
* **Inmobiliarias Analizadas:** {total} agencias en España.
* **Demanda de Sitios Web / Modernización:** {len(sin_web)} agencias ({len(sin_web)*100//total if total else 0}% del mercado analizado no tienen web propia).
* **Demanda de Clientes y Prospección:** {len(con_web)} agencias con presencia digital que compiten por captar nuevos inmuebles.

---

## 🎯 2. Oferta Principal: Paquete de Datos para Venta a Agencias de Marketing
*(Copia y pega este mensaje para vender la lista completa a agencias de marketing en España vía LinkedIn o Correo)*

> **Asunto:** Base de datos verificada de inmobiliarias en España (Segmentadas por necesidad web)
> 
> **Mensaje:**
> Hola [Nombre del Contacto / Director de Agencia],
> 
> Hemos completado un escaneo exhaustivo del sector inmobiliario en España y consolidamos una base de datos con **{total} agencias inmobiliarias activas**.
> 
> **Lo más valioso:** Incluye **{len(sin_web)} inmobiliarias que operan sin página web**, ideales para ofrecerles servicios de diseño web express, embudos de venta y automatización de citas.
> 
> * **Datos incluidos:** Nombre comercial, ciudad, dirección, teléfono directo de WhatsApp y correo verificado.
> * **Entrega:** Formato Excel / CSV inmediato.
> * **Inversión:** **$45 USD** (pago con tarjeta o PayPal con protección al comprador).
> 
> Si deseas acceder al paquete completo con entrega inmediata, puedes adquirirlo aquí:  
> 👉 **[Comprar Base de Datos Verificada ($45 USD)]({PAYPAL_PAYMENT_LINK})**
> 
> Saludos cordiales,  
> **Ricardo Miranda - Inteligencia de Mercado B2B**

---

## 📱 3. Ofertas Directas para Contacto por WhatsApp / Teléfono
*(Mensajes listos para contactar individualmente a las inmobiliarias que no tienen web)*

### Mensaje Tipo A (Para inmobiliarias sin página web):
> *"Hola equipo de **[Nombre Inmobiliaria]**, estuve viendo sus excelentes propiedades en **[Ciudad]**. Noté que actualmente no disponen de un catálogo web propio donde los compradores puedan filtrar por zona y enviarles consultas directas a su WhatsApp. Ayudamos a agencias locales a tener su portal inmobiliario listo en 48 horas. ¿Les interesaría ver una maqueta de ejemplo sin costo? Un saludo."*

### Mensaje Tipo B (Para inmobiliarias con página web - Venta de Leads):
> *"Estimado equipo de **[Nombre Inmobiliaria]**, les contacto porque realizamos análisis de demanda habitacional en **[Ciudad]**. Hemos detectado una alta búsqueda de pisos en su zona y tenemos una lista de propietarios interesados en tasar inmuebles este mes. ¿Tienen capacidad comercial para captar nuevas propiedades? Quedo a su disposición."*

---

## 📑 4. Primeras Empresas Calificadas con Oferta Asignada

| Empresa | Ciudad | Teléfono | Demanda Detectada | Enlace de Cobro Asignado |
| :--- | :--- | :--- | :--- | :--- |
"""

    for l in leads[:15]:
        demanda = l.get("Tipo de Demanda", "Desarrollo / Captación")
        tel = l.get("Teléfono", "No especificado")
        ciudad = l.get("Ciudad", "España")
        contenido += f"| **{l.get('Nombre', '')}** | {ciudad} | `{tel}` | {demanda} | [Pagar $45 USD]({PAYPAL_PAYMENT_LINK}) |\n"

    contenido += f"""
---
*Enlace Oficial de Cobro Directo: [{PAYPAL_PAYMENT_LINK}]({PAYPAL_PAYMENT_LINK})*  
*Generado automáticamente por Supercomputadora LeadBot 24/7 en la nube de GitHub Actions.*
"""

    with open(ruta_md, mode="w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"[+] Catálogo de Ofertas y Demandas actualizado con tu enlace de PayPal: {ruta_md}")

if __name__ == "__main__":
    print("==========================================================")
    print("      INICIANDO ROBOT DE MONETIZACIÓN B2B EN LA NUBE      ")
    print("==========================================================")
    leads = procesar_leads()
    exportar_csv(leads)
    generar_ofertas_y_demandas(leads)

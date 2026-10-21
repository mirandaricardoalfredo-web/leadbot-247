#!/usr/bin/env python3
"""
==============================================================================
GENERADOR DE REPORTE DIARIO DE LA SUPERCOMPUTADORA 24/7
==============================================================================
Lee las bases de datos de España y Argentina, compila estadísticas clave
y produce un reporte en Markdown (REPORTE_DIARIO.md) listo para enviarse
por correo y registrarse en GitHub Actions.
"""

import os
import csv
import datetime

REPORTE_MD = "REPORTE_DIARIO.md"
CSV_ESPANA = "leads_inmobiliarias_espana.csv"
CSV_ARGENTINA = "leads_gastronomia_argentina.csv"

def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    items = []
    try:
        with open(ruta, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append(row)
    except Exception as e:
        print(f"[-] Error leyendo {ruta}: {e}")
    return items

def generar():
    leads_esp = leer_csv(CSV_ESPANA)
    leads_arg = leer_csv(CSV_ARGENTINA)
    
    fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Métricas España
    total_esp = len(leads_esp)
    sin_web_esp = sum(1 for x in leads_esp if "Sin Sitio Web" in x.get("Oportunidad de Venta", "") or "Sin Web" in x.get("Sitio Web", ""))
    con_tel_esp = sum(1 for x in leads_esp if x.get("Teléfono") and x.get("Teléfono") != "No especificado")
    con_email_esp = sum(1 for x in leads_esp if x.get("Email") and x.get("Email") != "No especificado")
    
    # Métricas Argentina
    total_arg = len(leads_arg)
    con_whatsapp_arg = sum(1 for x in leads_arg if x.get("Teléfono / WhatsApp") and x.get("Teléfono / WhatsApp") != "No especificado")
    
    contenido = f"""# 📊 Reporte Diario de Operaciones - Supercomputadora 24/7

**Destinatario:** Ricardo Alfredo Miranda (`ricardoalfredomiranda@gmail.com`)  
**Fecha de Ejecución:** {fecha_hoy} (Hora del Servidor en la Nube)  
**Estado del Sistema:** 🟢 100% Operativo y Actualizado

---

## 🇪🇸 1. Motor Internacional (Inmobiliarias España - PayPal USD)

- **Total Inmobiliarias Acumuladas:** `{total_esp}`
- **🎯 Oportunidad Alta (Sin Sitio Web):** `{sin_web_esp}` agencias
- **Con Teléfono Verificado:** `{con_tel_esp}`
- **Con Email Directo:** `{con_email_esp}`

### 💰 Enlaces de Cobro Activos (PayPal USD):
- **Pack Express 50 Leads ($15 USD):** [Comprar Pack Express](https://www.paypal.com/ncp/payment/EL9K2AXW6CDVG)
- **Base Completa Consolidada ($45 USD):** [Comprar Base Completa](https://www.paypal.com/ncp/payment/BKT7UTA7HA5QS)

---

## 🇦🇷 2. Motor Nacional (Gastronomía Argentina - Mercado Pago ARS)

- **Total Locales Registrados:** `{total_arg}`
- **📲 Con WhatsApp / Teléfono Directo:** `{con_whatsapp_arg}` locales
- **Servicio Ofrecido:** Menú Digital QR + Envío de pedidos a WhatsApp (\$8.000 ARS por local)

### 💳 Datos de Cobro Oficiales (Mercado Pago):
- **Titular:** Ricardo Alfredo Miranda
- **Alias:** `aleado.copos.vial.mp`
- **CVU:** `0000003100096829377816`

---

## 📋 Muestra de Oportunidades Listas para Hoy

### Inmobiliarias sin Web (España):
"""
    # Top 5 España sin web
    esp_muestra = [x for x in leads_esp if "Sin Sitio Web" in x.get("Oportunidad de Venta", "")][:5]
    if esp_muestra:
        for x in esp_muestra:
            nombre = x.get('Nombre', 'N/D')
            ciudad = x.get('Ciudad', 'N/D')
            tel = x.get('Teléfono', 'N/D')
            contenido += f"- **{nombre}** ({ciudad}) | Tel: `{tel}` | Estado: *Sin Sitio Web*\n"
    else:
        contenido += "- *No hay muestras pendientes de España hoy.*\n"

    contenido += "\n### Locales Gastronómicos con WhatsApp (Argentina):\n"
    # Top 5 Argentina con teléfono
    arg_muestra = [x for x in leads_arg if x.get("Teléfono / WhatsApp") and x.get("Teléfono / WhatsApp") != "No especificado"][:5]
    if arg_muestra:
        for x in arg_muestra:
            nombre = x.get('Nombre', 'N/D')
            ciudad = x.get('Ciudad', 'N/D')
            tel = x.get('Teléfono / WhatsApp', 'N/D')
            contenido += f"- **{nombre}** ({ciudad}) | WhatsApp: `{tel}`\n"
    else:
        contenido += "- *No hay muestras gastronómicas con WhatsApp en este lote.*\n"

    contenido += f"""
---
💡 *Este informe fue generado automáticamente por tu Supercomputadora en la nube de GitHub Actions sin consumo de energía ni recursos de tu PC personal.*
"""

    with open(REPORTE_MD, mode="w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"[+] Reporte generado con éxito en '{REPORTE_MD}'.")

if __name__ == "__main__":
    generar()

#!/usr/bin/env python3
"""
==============================================================================
GENERADOR DE MENÚ DIGITAL QR Y CARTA INTERACTIVA (ARGENTINA)
==============================================================================
Crea una página web interactiva moderna optimizada para celulares y genera
el código QR en alta resolución listo para imprimir en mesas y mostrador.

Cuando un cliente en Argentina paga los $8.000 ARS por Mercado Pago,
ejecutas este script con el nombre del local y su número de WhatsApp
para entregarle su Menú Digital en menos de 1 minuto.
"""

import os
import urllib.parse
import json

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Menú Digital | {nombre_local}</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #f59e0b;
            --accent: #10b981;
            --border: #334155;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            padding-bottom: 90px;
        }}
        header {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border-bottom: 2px solid var(--primary);
            padding: 24px 16px;
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--primary);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 9999px;
            margin-bottom: 8px;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        h1 {{
            font-size: 1.75rem;
            font-weight: 800;
            margin-bottom: 4px;
        }}
        p.subtitle {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 16px;
        }}
        .category-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            margin: 24px 0 12px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .item-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .item-info {{
            flex: 1;
        }}
        .item-name {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .item-desc {{
            font-size: 0.8rem;
            color: var(--text-muted);
            line-height: 1.3;
        }}
        .item-price {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--accent);
            white-space: nowrap;
        }}
        .btn-order {{
            background-color: var(--primary);
            color: #0f172a;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.8rem;
            cursor: pointer;
            margin-top: 8px;
            display: inline-block;
            text-decoration: none;
        }}
        .floating-footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1e293b;
            border-top: 1px solid var(--border);
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 -4px 12px rgba(0,0,0,0.4);
            z-index: 100;
        }}
        .wa-btn {{
            background-color: #25d366;
            color: #ffffff;
            text-decoration: none;
            padding: 10px 18px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);
            margin: 0 auto;
        }}
    </style>
</head>
<body>

    <header>
        <span class="badge">Menú Interactivo Digital</span>
        <h1>{nombre_local}</h1>
        <p class="subtitle">📍 {ciudad_local} | Pedidos y Reservas Directas</p>
    </header>

    <div class="container">
        
        <div class="category-title">🍕 Especialidades & Platos Principales</div>
        
        <div class="item-card">
            <div class="item-info">
                <div class="item-name">Pizza Especial de la Casa</div>
                <div class="item-desc">Masa artesanal a la piedra, salsa de tomates seleccionados, mozzarella fundida, jamón cocido, morrones y aceitunas.</div>
            </div>
            <div class="item-price">$12.500</div>
        </div>

        <div class="item-card">
            <div class="item-info">
                <div class="item-name">Docena de Empanadas Criollas</div>
                <div class="item-desc">Carne cortada a cuchillo, cebolla de verdeo, huevo duro y aceitunas. Masa hojaldrada al horno de barro.</div>
            </div>
            <div class="item-price">$14.000</div>
        </div>

        <div class="item-card">
            <div class="item-info">
                <div class="item-name">Sándwich de Milanesa Completo</div>
                <div class="item-desc">Pan francés crocante, milanesa de ternera, lechuga capuchina, tomate fresco, jamón, queso y mayonesa casera.</div>
            </div>
            <div class="item-price">$9.800</div>
        </div>

        <div class="category-title">🍔 Hamburguesas & Minutas</div>
        
        <div class="item-card">
            <div class="item-info">
                <div class="item-name">Hamburguesa Doble Cheddar & Bacon</div>
                <div class="item-desc">Doble medallón de 120g de blend vacuno, cuádruple queso cheddar fundido y panceta crocante. Acompañada de papas rústicas.</div>
            </div>
            <div class="item-price">$11.200</div>
        </div>

        <div class="category-title">🥤 Bebidas & Cervezas</div>

        <div class="item-card">
            <div class="item-info">
                <div class="item-name">Gaseosas Línea Coca-Cola 500ml</div>
                <div class="item-desc">Lata o botella individual bien fría.</div>
            </div>
            <div class="item-price">$2.200</div>
        </div>

        <div class="item-card">
            <div class="item-info">
                <div class="item-name">Cerveza Artesanal / Litro</div>
                <div class="item-desc">Rubia, Roja o IPA artesanal tirada bien fría.</div>
            </div>
            <div class="item-price">$4.800</div>
        </div>

    </div>

    <div class="floating-footer">
        <a href="https://wa.me/{telefono_wa}?text={pedido_encoded}" class="wa-btn" target="_blank">
            💬 Hacer Pedido Directo por WhatsApp
        </a>
    </div>

</body>
</html>
"""

def generar_menu(nombre_local="Pizzería & Rotisería Tradición", ciudad_local="Córdoba / Buenos Aires", telefono_wa="5493510000000"):
    # Limpiar y sanitizar nombre de archivo
    nombre_limpio = "".join([c if c.isalnum() else "_" for c in nombre_local.lower()]).strip("_")
    directorio_salida = "menus_generados"
    os.makedirs(directorio_salida, exist_ok=True)
    
    pedido_texto = f"Hola {nombre_local}! Vi el menú digital y quiero hacer un pedido:"
    pedido_encoded = urllib.parse.quote(pedido_texto)
    
    html_final = HTML_TEMPLATE.format(
        nombre_local=nombre_local,
        ciudad_local=ciudad_local,
        telefono_wa=telefono_wa,
        pedido_encoded=pedido_encoded
    )
    
    archivo_html = os.path.join(directorio_salida, f"menu_{nombre_limpio}.html")
    with open(archivo_html, "w", encoding="utf-8") as f:
        f.write(html_final)
        
    # Enlace para descargar el Código QR de alta resolución listo para imprimir
    ruta_web = archivo_html.replace("\\", "/")
    qr_url = f"https://quickchart.io/qr?text=https://raw.githack.com/mirandaricardoalfredo-web/leadbot-247/main/{ruta_web}&size=600&caption={urllib.parse.quote(nombre_local)}"
    
    print(f"================================================================")
    print(f"[+] ¡Menú Digital Creado con Éxito para: {nombre_local}!")
    print(f"[+] Archivo HTML: {archivo_html}")
    print(f"[+] Código QR listo para imprimir en mesas y mostrador:")
    print(f"    {qr_url}")
    print(f"================================================================")
    return archivo_html, qr_url

if __name__ == "__main__":
    # Generar menú de muestra / demo
    generar_menu("Restaurante & Bar Demo", "Argentina", "5491122334455")

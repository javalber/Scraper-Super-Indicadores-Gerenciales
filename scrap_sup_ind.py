import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import sys

# --- Configuración ---
URL = "https://www.superfinanciera.gov.co/publicaciones/10084493/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualindicadores-gerenciales-niif-10084493/"
GMAIL_USER = "javalber2@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
DESTINO = "jflor35@bancodebogota.com.co"

ARCHIVO_MESES = "ultimo_mes.txt"

# --- Funciones ---
def obtener_ultimo_mes():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    textos = []
    for a in soup.find_all("a"):
        txt = a.get_text(strip=True)
        if txt.lower().startswith("indicadores gerenciales"):
            textos.append(txt)

    if not textos:
        return None

    return textos[0]

def leer_ultimo_guardado():
    if not os.path.exists(ARCHIVO_MESES):
        return None
    with open(ARCHIVO_MESES, "r", encoding="utf-8") as f:
        return f.read().strip()

def guardar_mes(mes):
    with open(ARCHIVO_MESES, "w", encoding="utf-8") as f:
        f.write(mes)

def enviar_correo(nuevo_mes):
    asunto = f"Nuevo informe disponible: {nuevo_mes}"
    cuerpo = f"Se ha publicado un nuevo mes en Superfinanciera:\n\n{nuevo_mes}\n\n{URL}"

    msg = MIMEText(cuerpo)
    msg["Subject"] = asunto
    msg["From"] = GMAIL_USER
    msg["To"] = DESTINO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, DESTINO, msg.as_string())

# --- Lógica principal ---
ultimo_mes_actual = obtener_ultimo_mes()
ultimo_guardado = leer_ultimo_guardado()

if ultimo_mes_actual is None:
    print("No se pudo extraer ningún mes.")
    sys.exit(0)

if ultimo_guardado != ultimo_mes_actual:
    print(f"Detectado nuevo mes: {ultimo_mes_actual}")
    enviar_correo(ultimo_mes_actual)
    guardar_mes(ultimo_mes_actual)
    # indicar que hubo cambio
    sys.exit(1)
else:
    print("No hay nuevo mes.")
    sys.exit(0)


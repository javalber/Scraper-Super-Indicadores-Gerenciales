import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import sys
import re
import unicodedata

# --- Configuración ---
URL = "https://www.superfinanciera.gov.co/publicaciones/10084493/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualindicadores-gerenciales-niif-10084493/"
GMAIL_USER = "javalber2@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
DESTINO = "jflor35@bancodebogota.com.co"

ARCHIVO_MESES = "ultimo_mes.txt"

# --- Funciones ---
MESES_NUMERO = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.strip().casefold()


def extraer_periodo(texto):
    texto_normalizado = normalizar_texto(texto)

    if not texto_normalizado.startswith("indicadores gerenciales"):
        return None

    match = re.search(
        r"\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\b\D*(\d{4})",
        texto_normalizado,
    )
    if not match:
        return None

    mes = MESES_NUMERO[match.group(1)]
    anio = int(match.group(2))
    return anio, mes


def obtener_ultimo_mes():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    candidatos = []
    for a in soup.find_all("a"):
        txt = a.get_text(strip=True)
        periodo = extraer_periodo(txt)
        if periodo is not None:
            candidatos.append((periodo, txt))

    if not candidatos:
        return None

    # Escoge el periodo más reciente, sin depender del orden de los links en la página.
    return max(candidatos, key=lambda item: item[0])[1]

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

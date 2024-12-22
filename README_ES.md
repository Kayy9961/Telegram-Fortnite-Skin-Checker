# Verificador de Skins de Fortnite para Telegram

Un verificador de skins de Fortnite para Telegram escrito en Python.

[![Static Badge](https://img.shields.io/badge/English%F0%9F%87%BA%F0%9F%87%B8-grey?style=flat-square)](/README.md)
[![Static Badge](https://img.shields.io/badge/Spanish%F0%9F%87%AA%F0%9F%87%B8-grey?style=flat-square)](/README_ES.md)

![Python Logo](https://img.shields.io/badge/Language-Python-blue?logo=python&logoColor=white&style=flat)
![GitHub Repo stars](https://img.shields.io/github/stars/Kayy9961/Telegram-Fortnite-Skin-Checker-Source-Code?style=flat)
![GitHub forks](https://img.shields.io/github/forks/Kayy9961/Telegram-Fortnite-Skin-Checker-Source-Code?style=flat)

![photo_2024-07-25_21-55-14](https://github.com/user-attachments/assets/72980910-750e-4bd0-acc2-7b71de0523e5)

![image](https://github.com/user-attachments/assets/1ef4238d-d237-40e9-9c5d-0ca8b11b5beb)

## Características:

- Genera una imagen de todas las skins en la cuenta de Fortnite
- Verifica los V-Bucks y el rango
- Lanza Fortnite directamente desde una cuenta

### Instalación:

#### Requisitos Previos

- [Python 3.8](https://www.python.org/downloads/) o superior
- Clave de API del bot de Telegram

### Pasos

1. Clona el repositorio

```bash
git clone https://github.com/Kayy9961/Telegram-Fortnite-Skin-Checker-Source-Code.git
```

2. Navega al directorio del proyecto

```bash
git clone https://github.com/Kayy9961/Telegram-Fortnite-Skin-Checker-Source-Code.git
```

3. Instala los paquetes requeridos

```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar el Verificador de Skins de Fortnite en Telegram, sigue estos pasos:

1. Configura tu bot de Telegram obteniendo un token de [BotFather](https://t.me/botfather).

2. [Configura la bot con tu token:](https://github.com/Kayy9961/Telegram-Fortnite-Skin-Checker/blob/28598faa985b2e93563a65b8a090d2c2931669f8/bot.py#L1476)

```python
 TOKEN = "EL TOKEN DE TU BOT DE TELEGRAM"
```
3. [Coloque la URL de su Webhook de Discord:](https://github.com/Kayy9961/Telegram-Fortnite-Skin-Checker/blob/28598faa985b2e93563a65b8a090d2c2931669f8/bot.py#L1260)

```python
 URL Weebhook = "YOU WEBHOOK"
```
4. Inicia el bot

En Windows:

```bash
python bot.py
```

En MacOS/Linux:

```bash
python3 bot.py
```

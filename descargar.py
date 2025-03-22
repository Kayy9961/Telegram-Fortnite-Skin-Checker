import aiohttp
import asyncio
import os

if not os.path.exists('cache'):
    os.makedirs('cache')

def read_skin_ids(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

async def download_image(session, id):
    imgpath = f"./cache/{id}.png"
    if not os.path.exists(imgpath) or not os.path.isfile(imgpath):
        urls = [
            f"https://fortnite-api.com/images/cosmetics/br/{id}/icon.png",
            f"https://fortnite-api.com/images/cosmetics/br/{id}/smallicon.png"
        ]
        for url in urls:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(imgpath, "wb") as f:
                        f.write(await resp.read())
                    print(f"Imagen descargada: {imgpath}")
                    break
        else:
            with open(imgpath, "wb") as f:
                f.write(open("tbd.png", "rb").read())
            print(f"No se pudo descargar la imagen para {id}, usando imagen por defecto.")

async def main():
    skin_ids = read_skin_ids("skins.txt")
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, id) for id in skin_ids]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

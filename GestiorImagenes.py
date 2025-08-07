
import os
import pandas as pd
from typing import List, Dict
import requests

class GestorImagenes:
    def __init__(self):
        self.paths = [
            "/COVID-19_Radiography_Dataset/COVID.metadata.xlsx",
            "/COVID-19_Radiography_Dataset/Normal.metadata.xlsx",
            "/COVID-19_Radiography_Dataset/Lung_Opacity.metadata.xlsx",
            "/COVID-19_Radiography_Dataset/Viral Pneumonia.metadata.xlsx"
        ]
        self.diccionario = self.cargar_metadatos()

    def cargar_metadatos(self):
        diccionario = {}
        for path in self.paths:
            categoria = os.path.basename(path).replace(".metadata.xlsx", "")
            df = pd.read_excel(path)

            for _, row in df.iterrows():
                key = row["FILE NAME"]
                diccionario[key] = {
                    "file_name": row["FILE NAME"],
                    "format": row["FORMAT"],
                    "size": row["SIZE"],
                    "url": row["URL"],
                    "categoria": categoria,
                    "path": f"/content/covid_19/COVID-19_Radiography_Dataset/{categoria}/images/{row['FILE NAME']}.{row['FORMAT']}"
                }

        return diccionario

    def menu(self):
        while True:
            print("\n-----MENÚ-----")
            print("1. Visualizar metadatos")
            print("2. Agregar nueva imagen")
            print("3. Actualizar imagen")
            print("4. Eliminar Imagen")
            print("5. Salir")
            opcion = input("Elige una opción (1-5): ")

            if opcion == '1':
                visualizar_imagen(self.diccionario)
            elif opcion == '2':
                agregar_imagen(self.diccionario)
            elif opcion == '3':
                actualizar_imagen(self.diccionario)
            elif opcion == '4':
                eliminar_imagen(self.diccionario)
            elif opcion == '5':
                print("Hasta luego.")
                break
            else:
                print("Opción no válida. Intenta de nuevo.")


# ------------------ FUNCIONES ------------------

def visualizar_imagen(diccionario):
    nombre = input("Ingresa el nombre del archivo a visualizar (ej. COVID-1): ")
    if nombre in diccionario:
        print("\nMetadatos:")
        for k, v in diccionario[nombre].items():
            print(f"{k}: {v}")
    else:
        print("Archivo no encontrado.")


def agregar_imagen(diccionario):
    categoria = input("Nombre del categoria (ej. COVID): ")
    nombre = input("Nombre del archivo (ej. COVID-99): ")

    if nombre in diccionario:
        print("Ese nombre ya existe en el diccionario. No se agregó.")
        return

    formato = input("Formato (ej. PNG): ").lower()
    size = input("Tamaño (ej. 256*256): ")
    url = input("URL (ej. https://...): ")

    base_path = f"/content/covid_19/COVID-19_Radiography_Dataset/{categoria}"
    images_path = os.path.join(base_path, "images")
    path_imagen = os.path.join(images_path, f"{nombre}.{formato}")
    path_excel = os.path.join("/content/covid_19/COVID-19_Radiography_Dataset/", f"{categoria}.metadata.xlsx")

    os.makedirs(images_path, exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path_imagen, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Imagen descargada en: {path_imagen}")
        else:
            print("No se pudo descargar la imagen. Verifica la URL.")
            return
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
        return

    diccionario[nombre] = {
        "file_name": nombre,
        "format": formato,
        "size": size,
        "url": url,
        "categoria": categoria,
        "path": path_imagen
    }

    # Metadata
    if os.path.exists(path_excel):
        df = pd.read_excel(path_excel)
    else:
        df = pd.DataFrame(columns=["FILE NAME", "FORMAT", "SIZE", "URL"])

    nueva_fila = pd.DataFrame([{
        "FILE NAME": nombre,
        "FORMAT": formato.upper(),
        "SIZE": size,
        "URL": url
    }])

    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
    df_actualizado.to_excel(path_excel, index=False)

    print(f"Metadatos actualizados en: {path_excel}")


def actualizar_imagen(diccionario):
    nombre = input("Ingrese el nombre del archivo a actualizar: ")

    if nombre not in diccionario:
        print("Ese nombre no existe en el diccionario. No se puede actualizar.")
        return

    nuevo_formato = input("Nuevo formato (ej. PNG) o Enter para mantener actual: ").lower()
    nuevo_size = input("Nuevo tamaño (ej. 256*256) o Enter para mantener actual: ")
    nueva_url = input("Nueva URL o Enter para mantener actual: ")

    datos_actuales = diccionario[nombre]

    if nuevo_formato:
        datos_actuales["format"] = nuevo_formato
    if nuevo_size:
        datos_actuales["size"] = nuevo_size
    if nueva_url:
        try:
            response = requests.get(nueva_url, stream=True)
            if response.status_code == 200:
                categoria = datos_actuales["categoria"]
                base_path = f"/content/covid_19/COVID-19_Radiography_Dataset/{categoria}"
                images_path = os.path.join(base_path, "images")
                path_imagen = os.path.join(images_path, f"{nombre}.{datos_actuales['format']}")

                with open(path_imagen, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Nueva imagen descargada en: {path_imagen}")
                datos_actuales["url"] = nueva_url
            else:
                print("No se pudo descargar la nueva imagen.")
                return
        except Exception as e:
            print(f"Error al descargar la nueva imagen: {e}")
            return

    diccionario[nombre] = datos_actuales

    path_excel = os.path.join("/content/covid_19/COVID-19_Radiography_Dataset/", f"{datos_actuales['categoria']}.metadata.xlsx")
    if os.path.exists(path_excel):
        df = pd.read_excel(path_excel)
        df.loc[df['FILE NAME'] == nombre, 'FORMAT'] = datos_actuales["format"].upper()
        df.loc[df['FILE NAME'] == nombre, 'SIZE'] = datos_actuales["size"]
        df.loc[df['FILE NAME'] == nombre, 'URL'] = datos_actuales["url"]
        df.to_excel(path_excel, index=False)
        print(f"Metadatos actualizados en: {path_excel}")
    else:
        print("El archivo Excel no existe. No se pueden actualizar los metadatos.")


def eliminar_imagen(diccionario):
    nombre = input("Ingrese el nombre del archivo a eliminar: ")

    if nombre not in diccionario:
        print("Ese nombre no existe en el diccionario. No se puede eliminar.")
        return

    datos_actuales = diccionario[nombre]
    formato = datos_actuales['format'].lower()
    path_imagen = os.path.join(f"/content/covid_19/COVID-19_Radiography_Dataset/{datos_actuales['categoria']}/images", f"{nombre}.{formato}")
    print(path_imagen)
    try:
        if os.path.exists(path_imagen):
            os.remove(path_imagen)
            print(f"Imagen eliminada: {path_imagen}")
        else:
            print("El archivo de imagen no existe.")
    except Exception as e:
        print(f"Error al eliminar la imagen: {e}")
        return

    del diccionario[nombre]

    path_excel = os.path.join("/content/covid_19/COVID-19_Radiography_Dataset/", f"{datos_actuales['categoria']}.metadata.xlsx")
    if os.path.exists(path_excel):
        df = pd.read_excel(path_excel)
        df = df[df['FILE NAME'] != nombre]
        df.to_excel(path_excel, index=False)
        print(f"Metadatos eliminados del archivo Excel: {path_excel}")
    else:
        print("El archivo Excel no existe. No se pueden actualizar los metadatos.")
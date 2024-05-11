import json
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import pickle

# Configurar la API de YouTube
api_service_name = "youtube"
api_version = "v3"

# Descripción predeterminada para videos sin descripción
DEFAULT_DESCRIPTION = (
    "Relato de terror para helar la sangre. #horrorstories #terror #miedo "
    "#paranormal #creepypasta\n\n"
    "Musica de terror creative commons\n\n"
    "https://soundcloud.com/royaltyfreebackgroundmusic/sets/creative-commons-music-273\n\n"
    "Imágenes de IA y narración de IA."
)

def get_authenticated_service(client_secrets_file, scopes):
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    return build(api_service_name, api_version, credentials=credentials)

def actualizar_videos(client_secrets_file):
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Obtener la instancia autenticada de la API de YouTube
    try:
        youtube = pickle.load(open("youtube.pickle", "rb"))
    except (OSError, IOError) as e:
        youtube = get_authenticated_service(client_secrets_file, scopes)
        pickle.dump(youtube, open("youtube.pickle", "wb"))

    # Obtener la lista de videos del canal (incluyendo privados)
    playlist_id = "REDACTED_PLAYLIST_ID"  # ID de la lista de reproducción de subidas del canal

    next_page_token = None
    total_results = 0

    while True:
        videos_response = youtube.playlistItems().list(
            part="snippet,status",
            playlistId=playlist_id,
            maxResults=50,  # Máximo permitido por solicitud
            pageToken=next_page_token
        ).execute()

        # Actualizar títulos y descripciones de los videos
        for video_item in videos_response.get("items", []):
            if video_item["status"]["privacyStatus"] in ["public"]:
                continue

            video_id = video_item["snippet"]["resourceId"]["videoId"]
            video_title = video_item["snippet"]["title"]
            video_description = video_item["snippet"]["description"]

            if "portrait" not in video_title:
                continue

            total_results += 1

            # Realizar cambios en el título
            new_title = video_title.replace(" portrait", "")

            # Realizar cambios en la descripción al añadir la descripción del archivo correspondiente
            file_name = f"historias_terminadas/{new_title}.txt"
            if os.path.exists(file_name):
                with open(file_name, "r") as file:
                    new_description = file.read()
            else:
                new_description = ""
            new_description = new_description + "\n\n" + video_description
            if not video_description:
                # Si no hay descripción, usar la descripción predeterminada
                new_description = DEFAULT_DESCRIPTION
            current_snippet = video_item["snippet"]

            # Actualizar título y descripción en el snippet actual
            current_snippet["title"] = new_title
            current_snippet["description"] = new_description
            current_snippet["categoryId"] = "24"

            # Actualizar título y descripción
            request = youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": current_snippet
                }
            )
            request.execute()

        next_page_token = videos_response.get("nextPageToken")

        if not next_page_token:
            break  # Salir del bucle si no hay más páginas

    print(f"Total de videos actualizados: {total_results}")

if __name__ == "__main__":
    
    # Reemplazar 'RUTA_A_TU_JSON_DE_CREDENCIALES' con la ruta al archivo JSON de credenciales de OAuth2
    client_secrets_file = '../client_secret_oauth.json'

    actualizar_videos(client_secrets_file)

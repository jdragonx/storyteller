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

            video_id = video_item["snippet"]["resourceId"]["videoId"]

            # Fetch the full snippet object for the video
            video_response = youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()

            video = video_response.get("items", [])[0]
            current_snippet = video["snippet"]

            if (current_snippet["defaultAudioLanguage"] == "es" and current_snippet["defaultLanguage"] == "es"):
                continue

            print(f"Actualizando video: {current_snippet['title'], current_snippet['defaultAudioLanguage'], current_snippet['defaultLanguage']}")

            total_results += 1

            current_snippet["defaultLanguage"] = "es"  # Set default language to Spanish
            current_snippet["defaultAudioLanguage"] = "es"  # Set default audio language to Spanish

            # Actualizar
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

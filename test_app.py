import pytest
import os
import json
import time
import shutil
from datetime import datetime, timedelta, timezone
from app import create_app
from config import Config

# Configure l'application pour les tests
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Utilise un fichier JSON de test pour les liens partagés
    app.config['SHARED_LINKS_FILE'] = os.path.join(app.root_path, 'test_shared_links.json')
    
    # S'assure que le fichier de test est vide avant chaque test
    with open(app.config['SHARED_LINKS_FILE'], 'w') as f:
        json.dump({}, f)

    # Crée un dossier d'upload de test propre
    test_upload_folder = os.path.join(app.root_path, 'test_uploads')
    if os.path.exists(test_upload_folder):
        shutil.rmtree(test_upload_folder)
    os.makedirs(test_upload_folder)
    app.config['UPLOAD_FOLDER'] = test_upload_folder

    with app.test_client() as client:
        yield client

    # Nettoie le fichier de test et le dossier d'upload de test après chaque test
    os.remove(app.config['SHARED_LINKS_FILE'])
    shutil.rmtree(app.config['UPLOAD_FOLDER'])

# Mock pour time.time() pour contrôler l'expiration des liens
@pytest.fixture
def mock_time(monkeypatch):
    class MockDatetime:
        def __init__(self, initial_time):
            self._time = initial_time

        def time(self):
            return self._time

        def advance(self, seconds):
            self._time += seconds

    mock_dt = MockDatetime(time.time())
    monkeypatch.setattr(time, 'time', mock_dt.time)
    return mock_dt

# Tests d'authentification
def test_index_no_auth(client):
    rv = client.get('/')
    assert b"Mot de passe" in rv.data
    assert b"Morceaux disponibles" not in rv.data

def test_index_view_password(client):
    rv = client.post('/', data={'password': Config.VIEW_PASSWORD}, follow_redirects=True)
    assert b"Morceaux disponibles" in rv.data
    assert b"Mode éditeur activé" not in rv.data

def test_index_edit_password(client):
    rv = client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)
    assert b"Morceaux disponibles" in rv.data
    assert b"Mode éditeur activé" in rv.data

def test_index_wrong_password(client):
    rv = client.post('/', data={'password': 'wrong_password'}, follow_redirects=True)
    assert b"Mot de passe" in rv.data
    assert b"Morceaux disponibles" not in rv.data

# Tests d'expiration de lien
def test_link_expiration(client, mock_time):
    # Simule la connexion en mode éditeur pour créer un lien
    client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)

    # Crée un fichier temporaire pour le test
    test_filename = 'test_audio.mp3'
    test_filepath = os.path.join(Config.UPLOAD_FOLDER, test_filename)
    with open(test_filepath, 'w') as f:
        f.write('dummy audio content')

    # Crée un lien de partage
    rv = client.post(f'/create-share/{test_filename}', data={'link_name': 'Test Link'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Lien temporaire généré" in rv.data # "Lien temporaire généré"
    
    # Extrait le token du lien créé
    share_url_prefix = client.base_url.rstrip('/') + '/share/'
    share_url_start = rv.data.find(share_url_prefix.encode())
    share_url_end = rv.data.find(b'" class="input', share_url_start)
    share_url = rv.data[share_url_start:share_url_end].decode()
    token = share_url.replace(share_url_prefix, '')

    # Vérifie que le lien est accessible juste après sa création
    rv = client.get(f'/share/{token}')
    assert rv.status_code == 200
    assert b"shared.html" in rv.data # Vérifie que le template est rendu

    # Avance le temps de 49 heures (plus que 48 heures d'expiration)
    mock_time.advance(49 * 3600)

    # Vérifie que le lien est maintenant expiré
    rv = client.get(f'/share/{token}')
    assert rv.status_code == 404
    assert b"Lien expiré." in rv.data # "Lien expiré."

    # Nettoie le fichier temporaire
    os.remove(test_filepath)

# Tests de gestion des dossiers
def test_create_folder(client):
    client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)
    rv = client.post('/', data={'create_folder': 'NewFolder'}, follow_redirects=True)
    assert b"NewFolder" in rv.data
    assert os.path.isdir(os.path.join(Config.UPLOAD_FOLDER, 'NewFolder'))

def test_upload_to_folder(client):
    client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)
    client.post('/', data={'create_folder': 'UploadFolder'}, follow_redirects=True)

    # Navigue dans le dossier
    client.get('/UploadFolder', follow_redirects=True)

    # Upload un fichier dans le dossier
    test_filename = 'folder_audio.mp3'
    test_filepath = os.path.join(Config.UPLOAD_FOLDER, 'UploadFolder', test_filename)
    with open(test_filepath, 'w') as f:
        f.write('dummy folder audio content')
    
    with open(test_filepath, 'rb') as f_upload:
        rv = client.post('/UploadFolder', data={'file': (f_upload, test_filename)}, follow_redirects=True)
    
    assert b"folder_audio.mp3" in rv.data
    assert os.path.exists(test_filepath)

def test_share_folder(client):
    client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)
    client.post('/', data={'create_folder': 'SharedFolder'}, follow_redirects=True)

    # Crée un fichier dans le dossier partagé
    test_filename = 'shared_folder_audio.mp3'
    test_filepath = os.path.join(Config.UPLOAD_FOLDER, 'SharedFolder', test_filename)
    with open(test_filepath, 'w') as f:
        f.write('dummy shared folder audio content')

    rv = client.post('/create-share/SharedFolder', data={'link_name': 'My Shared Folder'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Lien temporaire généré" in rv.data # "Lien temporaire généré"

    # Extrait le token du lien créé
    share_url_prefix = client.base_url.rstrip('/') + '/share/'
    share_url_start = rv.data.find(share_url_prefix.encode())
    share_url_end = rv.data.find(b'" class="input', share_url_start)
    share_url = rv.data[share_url_start:share_url_end].decode()
    token = share_url.replace(share_url_prefix, '')

    # Accède au lien partagé du dossier
    rv = client.get(f'/share/{token}')
    assert rv.status_code == 200
    assert b"Contenu du dossier \"SharedFolder\"" in rv.data # "Contenu du dossier "SharedFolder""
    assert b"shared_folder_audio.mp3" in rv.data

def test_delete_empty_folder(client):
    client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)
    client.post('/', data={'create_folder': 'EmptyFolderToDelete'}, follow_redirects=True)

    # Vérifie que le dossier existe
    folder_path = os.path.join(Config.UPLOAD_FOLDER, 'EmptyFolderToDelete')
    assert os.path.isdir(folder_path)

    # Supprime le dossier
    rv = client.post('/', data={'delete_item': 'EmptyFolderToDelete'}, follow_redirects=True)
    assert rv.status_code == 200
    assert not os.path.exists(folder_path)

def test_delete_non_empty_folder_fails(client):
    client.post('/', data={'password': Config.EDIT_PASSWORD}, follow_redirects=True)
    client.post('/', data={'create_folder': 'NonEmptyFolder'}, follow_redirects=True)

    # Crée un fichier dans le dossier
    test_filename = 'file_in_non_empty_folder.mp3'
    test_filepath = os.path.join(Config.UPLOAD_FOLDER, 'NonEmptyFolder', test_filename)
    with open(test_filepath, 'w') as f:
        f.write('dummy content')

    # Tente de supprimer le dossier non vide
    rv = client.post('/', data={'delete_item': 'NonEmptyFolder'}, follow_redirects=True)
    assert rv.status_code == 200 # La suppression échoue mais la page se recharge
    assert os.path.isdir(os.path.join(Config.UPLOAD_FOLDER, 'NonEmptyFolder'))
    assert os.path.exists(test_filepath)
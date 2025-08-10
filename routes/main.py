# routes/main.py
import os
import json
import secrets
from flask import Blueprint, request, render_template, redirect, send_from_directory, session, abort, url_for
from datetime import datetime, timedelta, timezone
from config import Config

bp = Blueprint('main', __name__)

SHARED_LINKS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_links.json'))

# Fonctions pour gérer le fichier JSON des liens partagés
def read_shared_links():
    try:
        with open(SHARED_LINKS_FILE, 'r') as f:
            links = json.load(f)
            if not isinstance(links, dict):
                return {}
            return links
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_shared_links(links):
    with open(SHARED_LINKS_FILE, 'w') as f:
        json.dump(links, f, indent=4)

# Fonction utilitaire pour obtenir le chemin complet sécurisé
def get_full_path(relative_path):
    # S'assure que le chemin est bien à l'intérieur de UPLOAD_FOLDER
    full_path = os.path.abspath(os.path.join(Config.UPLOAD_FOLDER, relative_path))
    if not full_path.startswith(os.path.abspath(Config.UPLOAD_FOLDER)):
        abort(400, "Accès non autorisé au chemin.")
    return full_path

# Liste les fichiers et dossiers dans un chemin donné
def get_files_and_folders(current_path=''):
    base_dir = get_full_path(current_path)
    files = []
    folders = []
    if not os.path.exists(base_dir):
        return [], []
    
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isfile(item_path):
            if os.path.splitext(item.lower())[1] in Config.ALLOWED_EXTENSIONS:
                files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)
            
    # Tri par ordre alphabétique, dossiers en premier
    folders.sort()
    files.sort(key=lambda x: os.path.getmtime(os.path.join(base_dir, x)), reverse=True)
    
    return files, folders

# Routes principales
@bp.route('/', defaults={'current_path': ''}, methods=['GET', 'POST'])
@bp.route('/<path:current_path>', methods=['GET', 'POST'])
def index(current_path):
    authenticated = session.get('authenticated', False)
    editor_mode = session.get('editor_mode', False)

    if request.method == 'POST':
        # Logique de connexion
        pwd = request.form.get('password')
        if pwd == Config.VIEW_PASSWORD:
            session['authenticated'] = True
            session['editor_mode'] = False
            return redirect(url_for('main.index', current_path=current_path))
        elif pwd == Config.EDIT_PASSWORD:
            session['authenticated'] = True
            session['editor_mode'] = True
            return redirect(url_for('main.index', current_path=current_path))

        if not editor_mode:
            return redirect(url_for('main.index', current_path=current_path))

        # Logique de création de dossier
        if 'create_folder' in request.form:
            folder_name = request.form['create_folder']
            if folder_name:
                new_folder_path = get_full_path(os.path.join(current_path, folder_name))
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                except OSError as e:
                    print(f"Erreur lors de la création du dossier: {e}") # Log pour debug
            return redirect(url_for('main.index', current_path=current_path))

        # Logique de suppression de fichier/dossier
        if 'delete_item' in request.form:
            item_to_delete = request.form['delete_item']
            item_path = get_full_path(os.path.join(current_path, item_to_delete))
            if os.path.exists(item_path):
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        # Ne supprime que si le dossier est vide
                        if not os.listdir(item_path):
                            os.rmdir(item_path)
                        else:
                            # Gérer l'erreur si le dossier n'est pas vide
                            print(f"Impossible de supprimer le dossier non vide: {item_path}")
                except OSError as e:
                    print(f"Erreur lors de la suppression: {e}") # Log pour debug
            return redirect(url_for('main.index', current_path=current_path))

        # Logique d'upload de fichier
        if 'file' in request.files:
            f = request.files['file']
            if f and f.filename:
                # Vérifie l'extension si c'est un fichier audio
                if os.path.splitext(f.filename.lower())[1] in Config.ALLOWED_EXTENSIONS:
                    target_dir = get_full_path(current_path)
                    filepath = os.path.join(target_dir, f.filename)
                    counter = 1
                    name, ext = os.path.splitext(f.filename)
                    while os.path.exists(filepath):
                        filepath = os.path.join(target_dir, f"{name}_{counter}{ext}")
                        counter += 1
                    f.save(filepath)
                else:
                    print(f"Extension non autorisée pour le fichier: {f.filename}") # Log pour debug
            return redirect(url_for('main.index', current_path=current_path))
        
        # Logique de suppression de lien partagé
        if 'delete_link' in request.form:
            token_to_delete = request.form['delete_link']
            links = read_shared_links()
            if token_to_delete in links:
                links.pop(token_to_delete)
                write_shared_links(links)
            return redirect(url_for('main.index', current_path=current_path))

    if not authenticated:
        return render_template('index.html', authenticated=False, editor_mode=False, files=[], folders=[], current_path=current_path, shared_links=[])

    files, folders = get_files_and_folders(current_path)
    
    # Charger et préparer les liens partagés pour l'affichage
    raw_links = read_shared_links()
    shared_links_list = []
    for token, data in raw_links.items():
        # Assurez-vous que 'expiry_date' est toujours une chaîne ISO formatée
        expiry = datetime.fromisoformat(data['expiry_date'])
        is_expired = datetime.now(timezone.utc) > expiry
        shared_links_list.append({
            'token': token,
            'link_name': data.get('link_name', 'Lien sans nom'),
            'item_name': data.get('item_name', data.get('filename')), # Peut être un fichier ou un dossier
            'is_directory': data.get('is_directory', False),
            'expiry_date_str': expiry.strftime('%d/%m/%Y %H:%M'),
            'is_expired': is_expired,
            'url': request.url_root.rstrip('/') + f'/share/{token}'
        })

    return render_template('index.html', 
                           authenticated=True, 
                           editor_mode=editor_mode, 
                           files=files, 
                           folders=folders, 
                           current_path=current_path, 
                           shared_links=shared_links_list)

@bp.route('/uploads/<path:filename_or_path>')
def uploaded_file(filename_or_path):
    # S'assure que le chemin est bien à l'intérieur de UPLOAD_FOLDER
    full_path = get_full_path(filename_or_path)
    
    if os.path.isfile(full_path):
        # Extrait le répertoire et le nom de fichier pour send_from_directory
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)
    else:
        abort(404, "Fichier non trouvé.")

@bp.route('/create-share/<path:item_path>', methods=['GET', 'POST'])
def create_share_link(item_path):
    if not session.get('editor_mode'):
        return redirect(url_for('main.index'))
    
    full_item_path = get_full_path(item_path)
    if not os.path.exists(full_item_path):
        abort(404, "L'élément demandé n'existe pas.")

    is_directory = os.path.isdir(full_item_path)
    item_name = os.path.basename(item_path)

    if request.method == 'POST':
        links = read_shared_links()
        token = secrets.token_urlsafe(8)
        
        creation_time = datetime.now(timezone.utc)
        expiry_time = creation_time + timedelta(hours=48)

        links[token] = {
            'link_name': request.form.get('link_name', f'Partage de {item_name}'),
            'item_name': item_path, # Stocke le chemin relatif complet
            'is_directory': is_directory,
            'creation_date': creation_time.isoformat(),
            'expiry_date': expiry_time.isoformat()
        }
        write_shared_links(links)

        share_url = request.url_root.rstrip('/') + f'/share/{token}'
        
        return render_template(
            'share_created.html',
            share_url=share_url,
            filename=item_name, # Pour l'affichage, on utilise le nom de l'élément
            expiry_date=expiry_time.strftime('%d/%m/%Y à %H:%M:%S UTC')
        )

    return render_template('index.html', 
                           filename=item_name, 
                           authenticated=True, 
                           editor_mode=True, 
                           files=get_files_and_folders(current_path='')[0], # On ne passe pas les dossiers ici
                           folders=get_files_and_folders(current_path='')[1], # On ne passe pas les fichiers ici
                           current_path=current_path, 
                           shared_links=[], 
                           show_share_modal=True)


@bp.route('/share/<token>')
def shared_link(token):
    links = read_shared_links()
    link_data = links.get(token)

    if not link_data:
        abort(404, "Lien invalide.")

    expiry_date = datetime.fromisoformat(link_data['expiry_date'])

    if datetime.now(timezone.utc) > expiry_date:
        links.pop(token)
        write_shared_links(links)
        abort(404, "Lien expiré.")

    item_path = link_data['item_name']
    full_item_path = get_full_path(item_path)

    if link_data.get('is_directory', False):
        # Si c'est un dossier, lister son contenu
        files, folders = get_files_and_folders(item_path)
        # Préparer les URLs pour les fichiers dans le dossier partagé
        shared_files_info = []
        for f in files:
            shared_files_info.append({
                'name': f,
                'url': url_for('main.uploaded_file', filename_or_path=os.path.join(item_path, f), _external=True)
            })
        return render_template('shared.html', 
                               link_name=link_data['link_name'], 
                               is_directory=True, 
                               item_name=os.path.basename(item_path), 
                               files=shared_files_info, 
                               folders=folders) # Les sous-dossiers ne sont pas cliquables pour l'instant
    else:
        # Si c'est un fichier, le servir directement
        return render_template('shared.html', 
                               link_name=link_data['link_name'], 
                               is_directory=False, 
                               filename=os.path.basename(item_path), 
                               file_url=url_for('main.uploaded_file', filename_or_path=item_path, _external=True))

@bp.route('/logout')
def logout():
    session.pop('authenticated', None)
    session.pop('editor_mode', None)
    return redirect(url_for('main.index'))
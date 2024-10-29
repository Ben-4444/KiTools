######################################################  ##
###################### RESUME ##########################
########################################################

resume = "Serveur web avec répertoire temporaire de ploads prêt à l'emploi"
description = """WebPload est un outil de partage de fichiers qui permet de déployer rapidement un serveur web temporaire 
avec une interface graphique moderne et intuitive.
 
Il offre deux modes de serveur (PHP ou Python) et permet de partager des fichiers de manière organisée 
avec une arborescence claire et une fonction de recherche intégrée. Les fichiers peuvent être ajoutés 
de manière permanente ou temporaire pour la durée de la session.
 
Fonctionnalités principales :
- Interface web responsive avec thème sombre
- Support des serveurs PHP et Python
- Organisation automatique des fichiers par type
- Fonction de recherche en temps réel
- Gestion des fichiers permanents et temporaires
- Navigation intuitive dans l'arborescence
- Affichage du statut en temps réel
- Configuration du port personnalisable
- Interface TUI (Terminal User Interface) pour la gestion
 
L'outil est particulièrement utile pour partager rapidement des fichiers sur un réseau local
de manière organisée et sécurisée, avec une interface utilisateur moderne et facile à utiliser."""


########################################################
###################### IMPORTS ########################
########################################################    


import os
import socket
import subprocess
import shutil
from colorama import Fore, Style
import curses
import json
import signal

########################################################
###################### VARIABLES #######################
########################################################

#ip lan format ip
ip_lan = subprocess.check_output("ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'", shell=True).decode().strip()

#menu serveur php
index_php = """<?php if (php_sapi_name() === 'cli-server') {$url = parse_url($_SERVER['REQUEST_URI']); $file = $_SERVER['DOCUMENT_ROOT'] . $url['path']; if (is_file($file) && basename($file) !== 'index.php') {header('Content-Type: text/plain'); readfile($file); exit();}} ?><!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>WebPload</title><style>body{font-family:Arial,sans-serif;background:#121212;color:#e0e0e0;margin:0;padding:0;font-size:18px;}.container{max-width:1000px;margin:15px auto;background:#1e1e1e;padding:30px;border-radius:12px;box-shadow:0 6px 12px rgba(0,0,0,0.3);}h1{text-align:center;color:#bb86fc;font-size:50px;margin:10px 0 30px;}.breadcrumb{color:#888;margin-bottom:30px;font-size:20px;}.breadcrumb a{color:#00ccff;text-decoration:none;}.breadcrumb a:hover{color:#03dac6;}.search-container{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px;gap:15px;}input[type="text"]{flex:1;padding:10px;border-radius:8px;border:1px solid #333;background:#2c2c2c;color:#e0e0e0;font-size:18px;}ul{list-style:none;padding:0;}li{padding:12px;border-bottom:1px solid #333;font-size:20px;}li a{text-decoration:none;}li a.file{color:#ff9900;}li a.directory{color:#00ccff;font-weight:bold;}li a:hover{color:#03dac6;}.home-btn,.search-btn{padding:10px 20px;background:#bb86fc;color:#121212;border-radius:8px;font-weight:bold;font-size:20px;border:none;cursor:pointer;}.home-btn:hover,.search-btn:hover{background:#e9b8ff;}</style></head><body><div class="container"><h1>WebPload</h1><?php $baseDir=__DIR__; $currentDir=isset($_GET['dir'])?realpath($baseDir.DIRECTORY_SEPARATOR.$_GET['dir']):$baseDir; $searchQuery=isset($_GET['search'])?strtolower($_GET['search']):''; if(strpos($currentDir,$baseDir)!==0)$currentDir=$baseDir; $relativePath=str_replace($baseDir,'',$currentDir); $pathParts=explode(DIRECTORY_SEPARATOR,trim($relativePath,DIRECTORY_SEPARATOR)); echo '<div class="breadcrumb">'; $path=''; foreach($pathParts as $part){if($part){$path.=DIRECTORY_SEPARATOR.$part; echo' / <a href="?dir='.urlencode(ltrim($path,DIRECTORY_SEPARATOR)).'">'.htmlspecialchars($part).'</a>';}} echo'</div>'; echo '<form method="get" action="" class="search-container">'; echo '<input type="hidden" name="dir" value="'.htmlspecialchars(trim($relativePath,DIRECTORY_SEPARATOR)).'">'; echo '<a href="?" class="home-btn">Home</a>'; echo '<input type="text" name="search" placeholder="Pload..." value="'.htmlspecialchars($searchQuery).'">'; echo '<button type="submit" class="search-btn">Recherche</button>'; echo'</form>'; function listFiles($dir,$baseDir,$searchQuery){$files=scandir($dir);$dirs=[];$normalFiles=[];foreach($files as $file){if($file!="."&&$file!=".."){$path=$dir.DIRECTORY_SEPARATOR.$file;$relativePath=str_replace($baseDir.DIRECTORY_SEPARATOR,'',$path);if(is_dir($path)){$dirs[]=['name'=>$file,'path'=>$relativePath];}else{if($file!=='index.php'){$normalFiles[]=['name'=>$file,'path'=>$relativePath];}}}}usort($dirs,fn($a,$b)=>strcasecmp($a['name'],$b['name']));usort($normalFiles,fn($a,$b)=>strcasecmp($a['name'],$b['name']));foreach($dirs as $dir){echo"<li><a class='directory' href='?dir=".htmlspecialchars($dir['path'])."'>".htmlspecialchars($dir['name'])."</a></li>";}foreach($normalFiles as $file){if($searchQuery===''||strpos(strtolower($file['name']),$searchQuery)!==false){echo"<li><a class='file' href='".htmlspecialchars($file['path'])."' target='_blank'>".htmlspecialchars($file['name'])."</a></li>";}}} function searchFilesRecursive($dir,$baseDir,$searchQuery){$results=[];$iterator=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir));foreach($iterator as $file){if($file->isFile()&&$file->getFilename()!=='index.php'){$relativePath=str_replace($baseDir.DIRECTORY_SEPARATOR,'',$file->getPathname());if(strpos(strtolower($file->getFilename()),$searchQuery)!==false)$results[]=$relativePath;}}sort($results);foreach($results as $result){echo"<li><a class='file' href='".htmlspecialchars($result)."' target='_blank'>".htmlspecialchars($result)."</a></li>";}} echo'<ul>'; if($searchQuery){searchFilesRecursive($currentDir,$baseDir,$searchQuery);}else{listFiles($currentDir,$baseDir,$searchQuery);} echo'</ul>'; ?></div></body></html>"""

# Variable globale pour stocker les ploads temporaires
temp_ploads = []

########################################################
###################### Fonctions #####################
########################################################    

def load_ploads():
    json_path = os.path.join(os.path.dirname(__file__), 'ploads.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return data['ploads']
    except FileNotFoundError:
        return {}

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_server_status():
    server_active = False
    server_type = None
    server_port = None
    for proc in os.popen('ps aux'):
        if 'python -m http.server' in proc:
            server_active = True
            server_type = "python"
            server_port = proc.split('http.server')[-1].strip()
            break
        elif 'php -S 0.0.0.0:' in proc:
            server_active = True 
            server_type = "php"
            server_port = proc.split('0.0.0.0:')[-1].split()[0]
            break
    return server_active, server_type, server_port

def display_status(stdscr, server_active, server_type, server_port, port_free):
    # Effacer l'écran
    stdscr.clear()
    
    # Afficher le logo
    logo = """
_       __     __    ____  __                __
| |     / /__  / /_  / __ \/ /___  ____ _____/ /
| | /| / / _ \/ __ \/ /_/ / / __ \/ __ `/ __  / 
| |/ |/ /  __/ /_/ / ____/ / /_/ / /_/ / /_/ /  
|__/|__/\___/_.___/_/   /_/\____/\__,_/\__,_/   
                                                """
    
    stdscr.addstr(1, 0, logo, curses.A_BOLD)
    
    # Créer un tableau pour afficher les informations
    table_y = 8
    table_x = 2
    
    stdscr.addstr(table_y, table_x, "┌" + "─"*50 + "┐")
    
    # Ligne IP LAN ou URL
    stdscr.addstr(table_y+1, table_x, "│")
    if server_active:
        url = f"http://{ip_lan}"
        if server_port and server_port != "80":
            url += f":{server_port}"
        stdscr.addstr(table_y+1, table_x+2, f"URL: {url}")
    else:
        stdscr.addstr(table_y+1, table_x+2, f"IP LAN: {ip_lan}")
    stdscr.addstr(table_y+1, table_x+50, "│")
    
    # Ligne Port - seulement si utilisé par un autre service
    if not port_free and not server_active:
        stdscr.addstr(table_y+2, table_x, "│")
        # Obtenir le service qui utilise le port 80
        service = ""
        for proc in os.popen('lsof -i :80'):
            if 'LISTEN' in proc:
                service = proc.split()[0]
                break
        stdscr.addstr(table_y+2, table_x+2, f"Port {server_port if server_port else '80'}: USED by {service}", curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(table_y+2, table_x+50, "│")
        current_line = table_y+3
    else:
        current_line = table_y+2
    
    # Ligne Serveur Web
    stdscr.addstr(current_line, table_x, "│")
    server_status = f"ENABLED ({server_type} on port {server_port})" if server_active else "DISABLED"
    server_color = curses.A_BOLD | (curses.color_pair(1) if server_active else curses.color_pair(2))
    stdscr.addstr(current_line, table_x+2, f"Web Server: {server_status}", server_color)
    stdscr.addstr(current_line, table_x+50, "│")
    
    stdscr.addstr(current_line+1, table_x, "└" + "─"*50 + "┘")
    
    # Menu
    menu_y = current_line + 3
    stdscr.addstr(menu_y, table_x, "Options:", curses.A_BOLD)
    stdscr.addstr(menu_y+1, table_x+2, "1. Ouvrir/Fermer serveur web")
    stdscr.addstr(menu_y+2, table_x+2, "2. Ajouter un pload")
    stdscr.addstr(menu_y+3, table_x+2, "3. Quitter")
    
    stdscr.addstr(menu_y+6, table_x, "❯ ", curses.A_BOLD)
    stdscr.refresh()


def add_pload(stdscr, server_active):
    stdscr.clear()
    curses.echo()
    
    # Demander le type de pload
    while True:
        stdscr.addstr(2, 2, "Extention du pload: ")
        pload_type = stdscr.getstr().decode('utf-8').lower()
        if pload_type.strip():
            break
        stdscr.addstr(3, 2, "L'extention ne peut pas être vide!", curses.color_pair(2))
        stdscr.addstr(4, 2, "Reessayez dans 1 secondes", curses.color_pair(2))
        stdscr.refresh()
        curses.napms(1500)  # Pause de 1.5s
        stdscr.addstr(3, 2, " " * 50)  # Efface le message d'erreur
        stdscr.addstr(4, 2, " " * 50)  # Efface le message de réessai
    
    # Demander le nom du pload
    while True:
        stdscr.addstr(4, 2, "Nom du pload: ")
        pload_name = stdscr.getstr().decode('utf-8')
        if pload_name.strip():
            break
        stdscr.addstr(5, 2, "Le nom ne peut pas être vide!", curses.color_pair(2))
        stdscr.addstr(6, 2, "Reessayez dans 1 secondes", curses.color_pair(2))
        stdscr.refresh()
        curses.napms(1500)  # Pause de 1.5s
        stdscr.addstr(5, 2, " " * 50)  # Efface le message d'erreur
        stdscr.addstr(6, 2, " " * 50)  # Efface le message de réessai
    
    # Demander si le pload doit être permanent
    stdscr.addstr(6, 2, "Pload permanent ou temporaire pour la session ? (O/n): ")
    is_permanent = stdscr.getstr().decode('utf-8').lower() not in ['n', 'non', 'no']
    
    # Demander le chemin du fichier source
    stdscr.addstr(8, 2, "Chemin du fichier source: ")
    file_path = stdscr.getstr().decode('utf-8')
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Ajouter au fichier ploads.json si permanent
        if is_permanent:
            json_path = os.path.join(os.path.dirname(__file__), 'ploads.json')
            with open(json_path, 'r') as f:
                ploads_data = json.load(f)
            
            # Chercher le type de pload dans le JSON
            type_found = False
            for pload_group in ploads_data['ploads']:
                if pload_type in pload_group:
                    pload_group[pload_type].append({
                        "name": pload_name,
                        "content": content
                    })
                    type_found = True
                    break
            
            # Si le type n'existe pas, créer une nouvelle entrée
            if not type_found:
                ploads_data['ploads'].append({
                    pload_type: [{
                        "name": pload_name,
                        "content": content
                    }]
                })
            
            # Sauvegarder le JSON mis à jour
            with open(json_path, 'w') as f:
                json.dump(ploads_data, f, indent=4)
        else:
            # Si non permanent, stocker en mémoire si le serveur n'est pas actif
            if not server_active:
                temp_ploads.append({
                    "type": pload_type,
                    "name": pload_name,
                    "content": content
                })
        
        # Si serveur actif, copier dans le répertoire
        if server_active:
            pload_dir = os.path.dirname(__file__)+f'/ploads/{pload_type}'
            if not os.path.exists(pload_dir):
                os.makedirs(pload_dir)
            
            dest_path = f"{pload_dir}/{pload_name}.{pload_type}"
            shutil.copy2(file_path, dest_path)
            os.chmod(dest_path, 0o777)
            
        stdscr.addstr(10, 2, "Pload ajouté avec succès!", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(10, 2, f"Erreur: {str(e)}", curses.color_pair(2))
    
    stdscr.addstr(12, 2, "Appuyez sur une touche pour continuer...")
    stdscr.refresh()
    stdscr.getch()
    curses.noecho()


def main(stdscr):
    # Configuration des couleurs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    
    while True:
        # Vérifier l'état du système
        server_active, server_type, server_port = get_server_status()
        port_free = not is_port_in_use(int(server_port) if server_port else 80)
        
        # Afficher le statut
        display_status(stdscr, server_active, server_type, server_port, port_free)
        
        # Gérer les choix
        choice = stdscr.getch()
        
        if choice == ord('1'):
            if server_active:
                if server_type == "python":
                    os.system(f"pkill -f 'python -m http.server {server_port}'")
                else:
                    os.system(f"pkill -f 'php -S 0.0.0.0:{server_port}'")
                if os.path.exists(os.path.dirname(__file__)+'/ploads'):
                    shutil.rmtree(os.path.dirname(__file__)+'/ploads')
            else:
                port = 80
                if not port_free:
                    curses.echo()
                    stdscr.addstr(20, 2, "Port 80 utilisé. Nouveau port: ")
                    try:
                        port = int(stdscr.getstr().decode('utf-8'))
                        if port < 1 or port > 65535:
                            raise ValueError
                    except ValueError:
                        stdscr.addstr(20, 2, "Erreur: Port invalide. Doit être entre 1 et 65535", curses.color_pair(2))
                        stdscr.refresh()
                        stdscr.getch()
                        continue
                    curses.noecho()
                
                curses.echo()
                stdscr.addstr(21, 2, "Type de serveur (php/python) [php]: ")
                server_choice = stdscr.getstr().decode('utf-8').lower()
                curses.noecho()
                
                if server_choice not in ['python', 'py']:
                    server_choice = 'php'
                
                if not os.path.exists(os.path.dirname(__file__)+'/ploads'):
                    os.makedirs(os.path.dirname(__file__)+'/ploads')
                
                # Charger les ploads permanents
                ploads = load_ploads()
                for pload_group in ploads:
                    for pload_type, payloads in pload_group.items():
                        key_dir = os.path.dirname(__file__)+'/ploads/'+pload_type
                        if not os.path.exists(key_dir):
                            os.makedirs(key_dir)
                        
                        for payload in payloads:
                            file_path = key_dir+'/'+payload['name']+'.'+pload_type
                            if not os.path.exists(file_path):
                                with open(file_path, 'w') as f:
                                    f.write(payload['content'])
                                os.chmod(file_path, 0o777)
                
                # Charger les ploads temporaires
                for temp_pload in temp_ploads:
                    key_dir = os.path.dirname(__file__)+'/ploads/'+temp_pload['type']
                    if not os.path.exists(key_dir):
                        os.makedirs(key_dir)
                    file_path = key_dir+'/'+temp_pload['name']+'.'+temp_pload['type']
                    with open(file_path, 'w') as f:
                        f.write(temp_pload['content'])
                    os.chmod(file_path, 0o777)
                
                if server_choice == 'php':
                    with open(os.path.dirname(__file__)+'/ploads/index.php', 'w') as f:
                        f.write(index_php)
                    subprocess.Popen(['php', '-S', f'0.0.0.0:{port}', 'index.php'], 
                                  stdout=open('/dev/null', 'w'),
                                  stderr=open('/dev/null', 'w'),
                                  cwd=os.path.dirname(__file__)+'/ploads',
                                  start_new_session=True)
                else:
                    subprocess.Popen(['python', '-m', 'http.server', str(port)],
                                  stdout=open('/dev/null', 'w'),
                                  stderr=open('/dev/null', 'w'),
                                  cwd=os.path.dirname(__file__)+'/ploads',
                                  start_new_session=True)
                
                # Actualiser l'affichage après le lancement du serveur
                server_active, server_type, server_port = get_server_status()
                port_free = not is_port_in_use(int(server_port) if server_port else 80)
                display_status(stdscr, server_active, server_type, server_port, port_free)
        
        elif choice == ord('2'):
            add_pload(stdscr, server_active)
            
        elif choice == ord('3'):
            exit()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass

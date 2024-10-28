#!/usr/bin/env python3

import os
import sys
import cmd
import argparse
from colorama import init, Fore, Style, Back
import random
import subprocess

# Initialiser colorama
init()

# Ajouter le parsing des arguments
parser = argparse.ArgumentParser()
parser.add_argument('--b' + 'o'*2 + 'bs', action='store_true')
args = parser.parse_args()

def get_random_color():
    """Retourne une couleur aléatoire parmi les couleurs disponibles de colorama"""
    colors = [
        Fore.RED, Fore.GREEN, Fore.YELLOW,
        Fore.MAGENTA, Fore.WHITE, Fore.LIGHTMAGENTA_EX,
        Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX,
    ]
    return random.choice(colors)

def get_start():
    return f"""{get_random_color()}
                          _  ___ _____         _
                         | |/ (_)_   _|__  ___| |___
                         | ' <| | | |/ _ \/ _ \ (_-<
                         |_|\_\_| |_|\___/\___/_/__/{Style.RESET_ALL}

                                                    {Fore.GREEN}Bienvenue dans KiTools !{Style.RESET_ALL}
                                                    {Fore.GREEN}Un framework d'outils de pentest{Style.RESET_ALL}
                                                    {Fore.LIGHTYELLOW_EX}by ben4444{Style.RESET_ALL}
    """

def get_random_ascii_art():
    # Chemin vers le fichier ascii_art.txt dans le même répertoire
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ascii_file = os.path.join(current_dir, 'ascii_art.txt')
    
    try:
        with open(ascii_file, 'r') as f:
            # Lire tout le contenu
            content = f.read()
            
            # Séparer les différents ASCII arts (séparés par des lignes vides multiples)
            ascii_arts = content.split('\n\n\n')
            
            # Filtrer les ASCII arts vides et supprimer les espaces de fin
            ascii_arts = ['\n'.join(line.rstrip() for line in art.split('\n')) 
                         for art in ascii_arts if art.strip()]
            
            if getattr(args, 'b' + 'o'*2 + 'bs'):
                for art in ascii_arts:
                    if "⢠⣿⠇⠄⣷⡑⢶⣶⢿⣿⣿⣿⣽⣿⣿⣿⣶⣶⡐⣶⣿⠿⠛⣩" in art:
                        max_width = max(len(line) for line in art.split('\n'))
                        padding = (79 - max_width) // 2
                        colored_art = f"{get_random_color()}" + '\n'.join(' ' * padding + line for line in art.split('\n')) + f"{Style.RESET_ALL}"
                        return colored_art
            
            # Sinon, choisir un ASCII art aléatoire et le centrer
            if ascii_arts:
                art = random.choice(ascii_arts)
                # Calculer la largeur de l'ASCII art
                max_width = max(len(line) for line in art.split('\n'))
                # Centrer chaque ligne par rapport à 79 caractères (largeur de kitools)
                padding = (79 - max_width) // 2
                # Ajouter une couleur aléatoire à l'ASCII art
                colored_art = f"{get_random_color()}" + '\n'.join(' ' * padding + line for line in art.split('\n')) + f"{Style.RESET_ALL}"
                return colored_art
            else:
                return "Aucun ASCII art trouvé"
    except FileNotFoundError:
        return "Fichier ascii_art.txt non trouvé"
    except Exception as e:
        return f"Erreur lors de la lecture du fichier: {str(e)}"

def scanner_repertoire():
    """Scanne le répertoire courant pour trouver les fichiers Python"""
    modules_disponibles = []
    repertoire_courant = os.path.dirname(os.path.abspath(__file__))
    
    for fichier in os.listdir(repertoire_courant):
        if fichier.endswith('.py') and fichier != 'KiTools.py' and not fichier.startswith('__'):
            chemin_complet = os.path.join(repertoire_courant, fichier)
            try:
                # Lire le fichier pour extraire resume et description
                with open(chemin_complet, 'r') as f:
                    contenu = f.read()
                    resume = ""
                    description = ""
                    
                    # Chercher resume et description dans le contenu
                    if "resume = " in contenu:
                        resume = contenu.split("resume = ")[1].split("\n")[0].strip('"\' ')
                    if "description = " in contenu:
                        description = contenu.split("description = ")[1].split("\n\n")[0].strip('"\' ')
                        
                modules_disponibles.append((fichier, chemin_complet, resume, description))
            except Exception as e:
                print(f"{Fore.RED}[!] Erreur lors de la lecture du fichier {fichier}: {e}{Style.RESET_ALL}")
                continue
    
    return modules_disponibles

class KiToolsShell(cmd.Cmd):
    intro = None
    # Définition des couleurs du prompt
    user_color = Fore.LIGHTRED_EX
    kitools_color = Fore.LIGHTRED_EX 
    trait_color = Fore.LIGHTYELLOW_EX
    fleche_color = Fore.GREEN
    prompt = f"{trait_color}╭──({user_color}{os.getlogin()}{kitools_color} 💀 KiTools{trait_color})\n╰─{fleche_color}➤{Style.RESET_ALL} "
    
    def __init__(self):
        super().__init__()
        self.modules = scanner_repertoire()
        os.system('clear' if os.name == 'posix' else 'cls')
        print(get_random_ascii_art() + "\n" + get_start())
        self.afficher_menu()
        if os.getlogin() != "root":
            print(f"{Fore.RED}[!] Attention, vous n'êtes pas root ! Certaines options peuvent ne pas fonctionner{Style.RESET_ALL}")

    def completenames(self, text, *ignored):
        """Autocomplétion des commandes"""
        commandes = ['help', 'list', 'clear', 'exit']
        # Ajouter les noms des modules
        modules_noms = {}
        for nom_fichier, _, _, _ in self.modules:
            nom_lower = nom_fichier[:-3].lower()
            modules_noms[nom_lower] = nom_fichier[:-3]
            commandes.append(nom_lower)
            
        matches = [cmd for cmd in commandes if cmd.startswith(text.lower())]
        
        # Remplacer les noms de modules par leur version originale
        for i, match in enumerate(matches):
            if match in modules_noms:
                matches[i] = modules_noms[match]
                
        return matches
        
    def afficher_menu(self):
        """Affiche le menu des modules disponibles"""
        print(f"{Fore.CYAN}╔═══════════════════ Liste Modules ═══════════════════╗{Style.RESET_ALL}")
        for i, (nom_fichier, _, resume, _) in enumerate(self.modules, 1):
            nom = nom_fichier[:-3].ljust(20)
            print(f"{Fore.CYAN}║ {Style.RESET_ALL}[{Fore.LIGHTGREEN_EX}{str(i)}{Style.RESET_ALL}] {Fore.YELLOW}{nom}{Style.RESET_ALL} {resume if resume else ''}")
        print(f"{Fore.CYAN}║ {Style.RESET_ALL}[{Fore.RED}0/exit{Style.RESET_ALL}] Quitter")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"{Back.LIGHTBLACK_EX}{Fore.WHITE} INFO {Style.RESET_ALL} Tapez {Fore.GREEN}'help'{Style.RESET_ALL} pour plus d'informations\n")

    def do_help(self, arg):
        """Affiche l'aide pour un module spécifique ou l'aide générale"""
        if not arg or arg == "general":
            print(f"{Fore.LIGHTGREEN_EX}╔═════════════════════ Help ═════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} {Fore.GREEN}Commandes disponibles:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • <id>      : Lance le module correspondant")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • <nom>     : Lance le module par son nom")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • help <id>     : Affiche l'aide du module spécifié")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • help          : Affiche cette aide")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • list          : Rafraîchit la liste des modules")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • clear         : Nettoie l'écran")
            print(f"{Fore.LIGHTGREEN_EX}║{Style.RESET_ALL} • exit/0        : Quitte le programme")
            print(f"{Fore.LIGHTGREEN_EX}╚════════════════════════════════════════════╝{Style.RESET_ALL}")
            return

        try:
            module_num = int(arg)
            if 1 <= module_num <= len(self.modules):
                nom_fichier, _, _, description = self.modules[module_num-1]
                if description:
                    print(f"{Fore.MAGENTA}╔═══ Description Module : {nom_fichier[:-3]} ═══╗{Style.RESET_ALL}")
                    print(f"{Fore.MAGENTA}║{Style.RESET_ALL} {description.replace(chr(10), chr(10)+Fore.MAGENTA+'║ '+Style.RESET_ALL)}")
                    print(f"{Fore.MAGENTA}╚{'═' * (len(nom_fichier[:-3]) + 25)}╝{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[!] Pas de description disponible pour {Fore.YELLOW}{nom_fichier[:-3]}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] Erreur: Numero module invalide{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}[!] Erreur: Module '{arg}' introuvable, Tapez 'list' pour lister les modules existants{Style.RESET_ALL}")

    def do_list(self, arg):
        """Affiche la liste des modules"""
        self.afficher_menu()

    def do_clear(self, arg):
        """Nettoie l'écran"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(get_random_ascii_art() + "\n" + get_start())
        self.afficher_menu()

    def default(self, line):
        """Gère les commandes non reconnues"""
        try:
            if line == "0" or line.lower() == "exit":
                return self.do_exit("")
                
            # Essayer d'abord de convertir en nombre
            try:
                index = int(line) - 1
                if 0 <= index < len(self.modules):
                    self.lancer_module(index)
                else:
                    print(f"{Fore.RED}[!] Erreur: Numero module invalide{Style.RESET_ALL}")
            except ValueError:
                # Si ce n'est pas un nombre, chercher par nom
                nom_module = line.lower()
                module_trouve = False
                for index, (nom_fichier, _, _, _) in enumerate(self.modules):
                    if nom_fichier[:-3].lower() == nom_module:
                        self.lancer_module(index)
                        module_trouve = True
                        break
                if not module_trouve:
                    print(f"{Fore.RED}[!] Erreur: Commande '{line}' introuvable ! Tapez 'help' ou 'list' pour plus d'informations{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Erreur: {e}{Style.RESET_ALL}")

    def lancer_module(self, index):
        """Lance un module spécifique"""
        nom_fichier, chemin_complet, _, _ = self.modules[index]
        print(f"{Fore.GREEN}[+] Lancement de {Fore.YELLOW}{nom_fichier}{Fore.GREEN}...{Style.RESET_ALL}")
        print(f"{'─' * 50}\n")
        try:
            subprocess.run([sys.executable, chemin_complet])
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}[*] Module interrompu par l'utilisateur{Style.RESET_ALL}")
        print(f"\n{'─' * 25} Retour KiTools {'─' * 25}")

    def do_exit(self, arg):
        """Quitte le programme"""
        print(f"\n{Fore.YELLOW}[*] Merci d'avoir utilisé KiTools ! Au revoir !{Style.RESET_ALL}")
        return True

    def do_EOF(self, line):
        """Gère Ctrl+D"""
        print("")
        return True

    def emptyline(self):
        """Ne fait rien quand une ligne vide est entrée"""
        pass

def main():
    try:
        shell = KiToolsShell()
        while True:
            try:
                shell.cmdloop()
                break
            except KeyboardInterrupt:
                try:
                    print("\n" + f"{Fore.YELLOW}[?] Voulez-vous vraiment quitter ? (o/N) : {Style.RESET_ALL}", end='')
                    reponse = input().lower()
                    if reponse in ['o', 'oui', 'y', 'yes']:
                        print(f"\n{Fore.YELLOW}[*] Merci d'avoir utilisé KiTools ! Au revoir !{Style.RESET_ALL}")
                        break
                    continue
                except KeyboardInterrupt:
                    print("")
                    continue
    except Exception as e:
        print(f"\n{Fore.RED}[!] Erreur fatale: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

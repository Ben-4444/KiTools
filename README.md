# KiTools

![alt text](https://github.com/Ben-4444/KiTools/blob/main/modules/galerie/img.png)

## Installation 
git clone https://github.com/Ben-4444/KiTools.git<br>
cd KiTools<br>
./install.sh

## Usage
┌──(root㉿kali)-[~]<br>
└─# KiTools


## Description
KiTools est un outil en ligne de commande qui regroupe plusieurs modules pour automatiser des tâches courantes dans le domaine de la sécurité informatique et du développement.


### Modules existants :

#### SSRFmap
Module d'exploitation de vulnérabilité SSRF (Server-Side Request Forgery) permettant de :
- Détecter les ports ouverts sur un serveur cible via des requêtes HTTP
- Supporter les méthodes GET et POST avec gestion des cookies
- Effectuer des scans multi-thread avec barre de progression
- Sauvegarder la configuration

#### NMAPassist 
Assistant pour Nmap offrant :
- Interface interactive pour configurer les scans
- Support des principaux types de scan (TCP SYN/Connect, UDP, OS, services...)
- Gestion des scripts NSE
- Sauvegarde des configurations
- Affichage coloré des résultats

#### WebPload
Serveur web temporaire pour l'hébergement de payloads :
- Création automatique d'un serveur Python sur le port 80
- Génération de payloads prêts à l'emploi (webshells, reverse shells, XSS...)
- Gestion automatique des fichiers temporaires
- Nettoyage à la fermeture


##Galerie :

<table>
  <tr>
    <td> <img src="modules/galerie/img.png"  alt="1" width = 360px height = 640px ></td>

    <td><img src="img2.png" alt="2" width = 360px height = 640px></td>
   </tr> 
   <tr>
      <td><img src="modules/galerie/img.png" alt="3" width = 360px height = 640px></td>

      <td><img src="./Scshot/trip_end.png" align="right" alt="4" width = 360px height = 640px>
  </td>
  </tr>
</table>

### Améliorations à venir :
#### WebPload
- pload msfvenom with option
- option ajouter un pload temporaire manuelement 


### Modules à venir :

#### BruteForce Web
- Attaques par dictionnaire sur formulaires web
- Support de différents types d'authentification
- Gestion des sessions et cookies
- Détection automatique des champs

#### Auto Handler
- Auto Handler msf with option + pload msf in WebPload
- Auto Handler classique


#### Wifite
- lunch wifite with option

#### DDOS
- Scan port/services and select best target
- DDOS attack web
- DDOS attack ip/port

#### HYDRAssist
- like nmapassist but with hydra
import subprocess
import curses
import time
import re
from colorama import init, Fore, Style
import ipaddress
import os

# Initialiser colorama
init()

# ASCII art pour le titre
start = """
  _  _ __  __   _   ___            _    _   
 | \| |  \/  | /_\ | _ \__ _ _____(_)__| |_ 
 | .` | |\/| |/ _ \|  _/ _\ (_-<_-< (_-<  _|
 |_|\_|_|  |_/_/ \_\_| \__,_/__/__/_/__/\__|                                   
   nmap pour les noobs                   by ben4444
"""

resume = "Assistant interactif NMAP full options avec aide contextuelle"
description = """NMAPassist est un assistant interactif pour Nmap qui facilite la création et l'exécution de scans réseau.
Il propose une interface utilisateur en ligne de commande permettant de configurer facilement
les différentes options de Nmap comme le type de scan (furtif, TCP connect, UDP), la sélection
des ports, la détection de services et de systèmes d'exploitation, l'utilisation de scripts NSE, etc.
Le programme guide l'utilisateur à travers les différentes options avec des 
descriptions claires et une aide contextuelle détaillée.
Il permet également de sauvegarder les configurations et d'exporter les résultats dans différents formats.
Cet outil est particulièrement utile pour les débutants qui souhaitent utiliser Nmap sans 
avoir à mémoriser toutes les options en ligne de commande."""


# Configuration par défaut
CIBLE_DEFAULT = "192.168.1.28"
SCAN_FURTIF_DEFAULT = False
SCAN_TCP_CONNECT_DEFAULT = False
SCAN_UDP_DEFAULT = False
TOUS_LES_PORTS_DEFAULT = False
PORTS_SPECIFIQUES_DEFAULT = ""
SCAN_RAPIDE_DEFAULT = False
TOP_PORTS_DEFAULT = ""
SCAN_OS_DEFAULT = False
SCAN_SERVICES_DEFAULT = False
SCAN_AGRESSIF_DEFAULT = False
SCRIPTS_NSE_DEFAULT = False
SCRIPT_CHOISI_DEFAULT = ""
VERBOSITE_DEFAULT = False
MODE_DEBUG_DEFAULT = False
INTERFACE_RESEAU_DEFAULT = ""
TIMING_TEMPLATE_DEFAULT = ""
EXCLUDE_HOSTS_DEFAULT = ""
OUTPUT_DEFAULT = ""

def afficher_aide(id_aide):
    aides = {
        "scan_furtif": "Option Nmap -sS\nLe scan furtif (SYN scan) envoie des paquets SYN sans terminer la connexion TCP.\nIl utilise des paquets TCP SYN pour sonder les ports, attendant un SYN-ACK en réponse.\nSi un SYN-ACK est reçu, le port est considéré comme ouvert, et un RST est envoyé.\nCette méthode est moins détectable car elle ne complète pas la connexion TCP à 3 voies.\nElle est rapide et efficace, mais peut être bloquée par certains pare-feux stateful.\nhttps://nmap.org/book/synscan.html",
        "scan_tcp_connect": "Option Nmap -sT\nLe scan TCP connect établit une connexion complète avec chaque port cible.\nIl utilise l'appel système connect() pour initier une connexion TCP complète à 3 voies.\nCette méthode est plus lente car elle attend la fin de chaque connexion ou son timeout.\nElle est plus fiable et fonctionne quand l'utilisateur n'a pas les privilèges raw socket.\nCependant, elle est plus facilement détectable et loguée par les systèmes cibles.\nhttps://nmap.org/book/connect-scan.html",
        "scan_udp": "Option Nmap -sU\nLe scan UDP envoie des paquets UDP vides ou avec un payload spécifique aux ports.\nIl attend une réponse UDP ou un message ICMP 'port unreachable' pour déterminer l'état.\nLes ports sans réponse sont considérés ouverts|filtrés, nécessitant souvent une retransmission.\nCette méthode est plus lente que les scans TCP en raison des timeouts et retransmissions.\nElle est cruciale pour détecter les services UDP comme DNS, SNMP, et DHCP.\nhttps://nmap.org/book/udp-scan.html",
        "tous_les_ports": "Option Nmap -p-\nCette option scanne tous les 65535 ports TCP possibles sur la cible.\nElle est exhaustive mais prend considérablement plus de temps qu'un scan par défaut.\nNmap utilise diverses techniques d'optimisation pour accélérer ce processus intensif.\nCette méthode peut révéler des services sur des ports non standard ou malveillants.\nElle est utile pour l'audit de sécurité approfondi mais peut être perçue comme agressive.\nhttps://nmap.org/book/port-scanning-basics.html",
        "scan_rapide": "Option Nmap --top-ports\nCette option scanne uniquement les ports les plus couramment utilisés.\nNmap maintient une liste de ports fréquents basée sur des études de popularité.\nL'utilisateur peut spécifier le nombre de top ports à scanner (ex: --top-ports 100).\nCette méthode offre un bon compromis entre vitesse et couverture pour les scans rapides.\nElle est efficace pour la découverte initiale mais peut manquer des services moins courants.\nhttps://nmap.org/book/performance-port-selection.html",
        "systemes_exploitation": "Option Nmap -O\nCette option tente d'identifier le système d'exploitation de la cible.\nElle envoie une série de paquets TCP et UDP, analysant les réponses pour les empreintes OS.\nNmap compare ces réponses à sa base de données d'empreintes OS pour faire une estimation.\nLa précision dépend de facteurs comme les pare-feux et la mise à jour de la base de données.\nCette technique peut être affectée par la virtualisation et les configurations réseau atypiques.\nhttps://nmap.org/book/osdetect.html",
        "noms_services": "Option Nmap -sV\nCette option tente d'identifier les services et leurs versions sur les ports ouverts.\nElle envoie une série de sondes (bannières, requêtes) pour provoquer des réponses spécifiques.\nNmap analyse ces réponses et les compare à sa base de données de signatures de services.\nLa précision et la profondeur du scan peuvent être ajustées avec --version-intensity.\nCette méthode peut augmenter significativement la durée du scan mais fournit des infos cruciales.\nhttps://nmap.org/book/vscan.html",
        "scan_agressif": "Option Nmap -A\nCette option active plusieurs fonctionnalités avancées de Nmap simultanément.\nElle combine la détection d'OS (-O), la détection de version (-sV), le script scanning (-sC),\net le traceroute. Cette approche fournit un maximum d'informations sur la cible en un seul scan.\nElle est plus lente et plus facilement détectable, mais offre une vue complète de la cible.\nCette option est souvent utilisée pour l'audit de sécurité approfondi et la reconnaissance.\nhttps://nmap.org/book/man-briefoptions.html",
        "scripts_nse": "Option Nmap --script\nCette option active le Nmap Scripting Engine (NSE) pour des tests avancés.\nLe NSE permet d'exécuter des scripts Lua pour l'énumération, la détection de vulnérabilités,\net même l'exploitation. Les scripts peuvent être sélectionnés individuellement ou par catégories.\nIls peuvent interagir avec les services détectés pour obtenir des informations supplémentaires.\nL'utilisation de scripts peut considérablement augmenter la durée et l'impact du scan.\nhttps://nmap.org/book/nse.html",
        "verbosite": "Option Nmap -v\nCette option augmente le niveau de détail des informations affichées pendant le scan.\nElle peut être utilisée plusieurs fois (-vv, -vvv) pour des niveaux de verbosité croissants.\nElle affiche des informations en temps réel sur la progression, les ports trouvés, et plus.\nCette option est utile pour le débogage et pour comprendre le déroulement précis du scan.\nElle peut ralentir légèrement le scan en raison de l'augmentation des opérations d'E/S.\nhttps://nmap.org/book/output-formats-verbose-output.html",
        "mode_debug": "Option Nmap -d\nCette option active le mode debug, fournissant des informations très détaillées.\nElle peut être utilisée plusieurs fois (-dd, -ddd) pour des niveaux de debug plus profonds.\nElle affiche des informations techniques sur chaque paquet envoyé et reçu par Nmap.\nCe mode est principalement utilisé pour le dépannage et le développement de Nmap.\nIl peut considérablement ralentir le scan et produire une grande quantité de données de sortie.\nhttps://nmap.org/book/output-formats-debugging-output.html",
        "interface_reseau": "Option Nmap -e\nCette option permet de spécifier l'interface réseau à utiliser pour le scan.\nElle est utile sur les systèmes multi-homed ou pour forcer l'utilisation d'une interface.\nNmap utilisera l'adresse IP associée à cette interface comme adresse source du scan.\nCette option peut être combinée avec --source-ip pour un contrôle total de la source.\nElle est particulièrement utile pour le scanning à travers des VPNs ou interfaces spécifiques.\nhttps://nmap.org/book/man-interface.html",
        "timing_template": "Option Nmap -T\nCette option contrôle la vitesse et l'agressivité du scan via des templates prédéfinis.\nLes templates vont de T0 (très lent) à T5 (très agressif), T3 étant le défaut.\nIls ajustent automatiquement plusieurs paramètres comme les timeouts et la parallélisation.\nLes templates plus agressifs sont plus rapides mais peuvent être moins fiables ou détectables.\nCette option offre un moyen simple d'équilibrer vitesse, fiabilité et discrétion du scan.\nhttps://nmap.org/book/performance-timing-templates.html"
    }
    print(f"\nAide pour l'option '{id_aide}':\n{aides.get(id_aide, 'Aucune aide disponible pour cette option.')}\n")

def afficher_aide_script(id_aide):
    help_scripts = {
        "default": "Scripts par défaut de Nmap\nExécute les scripts considérés comme sûrs et non intrusifs.\nFournit des informations de base sur les services détectés.\nTemps d'exécution rapide et faible risque de perturbation.\nRecommandé pour un premier scan de reconnaissance.",
        "vuln": "Scripts de détection de vulnérabilités\nRecherche activement des vulnérabilités connues dans les services.\nPeut inclure des tests pour des failles comme Heartbleed, ShellShock, etc.\nPeut être intrusif et déclencher des alertes de sécurité.\nÀ utiliser avec précaution sur les systèmes de production.",
        "safe": "Scripts non intrusifs\nGarantis sans impact négatif sur les systèmes cibles.\nCollecte passive d'informations sans tentative d'exploitation.\nIdéal pour les scans de routine et l'inventaire réseau.\nPeut être utilisé sur des systèmes sensibles.",
        "discovery": "Scripts de découverte de services\nRecherche approfondie des services et de leurs configurations.\nInclut l'énumération DNS, SNMP, SMB et plus.\nPeut révéler des informations sur la topologie réseau.\nUtile pour la cartographie d'infrastructure.",
        "auth": "Scripts d'authentification\nTeste les mécanismes d'authentification des services.\nVérifie les configurations par défaut et faibles.\nPeut inclure des tests de connexion anonyme.\nNe tente pas de force brute des credentials.",
        "brute": "Scripts de force brute\nTente de deviner les credentials par force brute.\nSupporte de nombreux protocoles (SSH, FTP, HTTP, etc.).\nPeut consommer beaucoup de ressources et de temps.\nRisque de verrouillage de comptes.",
        "exploit": "Scripts d'exploitation\nTente d'exploiter des vulnérabilités connues.\nPeut inclure des exploits pour des CVEs spécifiques.\nTrès intrusif et potentiellement dangereux.\nÀ utiliser uniquement avec autorisation explicite.",
        "malware": "Scripts de détection de malware\nRecherche des signes d'infection malware.\nVérifie les backdoors et services compromis.\nAnalyse les configurations suspectes.\nUtile pour l'audit de sécurité.",
        "version": "Scripts d'identification de version\nDétection précise des versions de services.\nUtilise des techniques avancées de fingerprinting.\nPeut révéler des versions vulnérables.\nComplément à l'option -sV.",
        "http-enum": "Énumération des ressources HTTP\nRecherche de fichiers et répertoires web.\nDétecte les CMS et applications web courantes.\nPeut révéler du contenu sensible.\nRisque de surcharge du serveur web.",
        "ssl-enum-ciphers": "Analyse SSL/TLS\nÉvalue la configuration SSL/TLS.\nDétecte les chiffrements faibles ou obsolètes.\nVérifie la présence de vulnérabilités SSL/TLS.\nNon intrusif mais détaillé.",
        "smb-os-discovery": "Découverte OS via SMB\nIdentifie le système d'exploitation via SMB.\nCollecte des informations sur le domaine Windows.\nDétecte la version de Samba sur Linux.\nPeu intrusif mais informatif.",
        "dns-brute": "Force brute DNS\nTente de découvrir des sous-domaines.\nUtilise des listes de noms courants.\nPeut révéler des hôtes cachés.\nRisque de détection par les systèmes de monitoring.",
        "ftp-anon": "Test FTP anonyme\nVérifie l'accès FTP anonyme.\nListe les fichiers accessibles.\nTeste les permissions d'écriture.\nPeu intrusif mais important pour la sécurité.",
        "ssh-auth-methods": "Méthodes d'auth SSH\nÉnumère les méthodes d'authentification SSH.\nVérifie la configuration du serveur.\nDétecte les options de sécurité faibles.\nNon intrusif et informatif.",
        "mysql-enum": "Énumération MySQL\nTeste l'accès MySQL anonyme.\nCollecte les informations de version.\nVérifie les comptes par défaut.\nPeut déclencher des alertes de sécurité.",
        "snmp-info": "Information SNMP\nCollecte les données via SNMP.\nPeut révéler des informations système détaillées.\nTeste les community strings par défaut.\nRisque de divulgation d'informations sensibles.",
        "http-title": "Titres des pages web\nExtrait les titres des pages web.\nIdentifie les applications web.\nAide à la reconnaissance initiale.\nTotalement non intrusif.",
        "banner": "Récupération de bannières\nCollecte les bannières des services.\nIdentifie les versions de services.\nInformation passive mais utile.\nAucun impact sur les systèmes.",
        "http-headers": "Analyse des en-têtes HTTP\nExamine les en-têtes de réponse HTTP.\nDétecte les technologies web utilisées.\nVérifie les configurations de sécurité.\nTotalement non intrusif.",
        "http-methods": "Test des méthodes HTTP\nÉnumère les méthodes HTTP supportées.\nVérifie les méthodes dangereuses.\nIdentifie les configurations WebDAV.\nPeu intrusif mais informatif.",
        "http-robots.txt": "Analyse robots.txt\nExamine le fichier robots.txt.\nDécouvre les chemins cachés.\nIdentifie les zones restreintes.\nTotalement passif.",
        "http-sitemap-generator": "Génération sitemap\nCrée une carte du site web.\nDécouvre la structure des répertoires.\nIdentifie les fichiers accessibles.\nPeut être intensif.",
        "ssl-heartbleed": "Test Heartbleed\nVérifie la vulnérabilité Heartbleed.\nTest précis et ciblé.\nPeut perturber les systèmes vulnérables.\nImportant pour la sécurité SSL/TLS.",
        "sslv2": "Test SSLv2\nVérifie le support de SSLv2.\nIdentifie les chiffrements obsolètes.\nTest de protocole déprécié.\nNon intrusif mais important.",
        "tls-nextprotoneg": "Test Next Protocol Negotiation\nVérifie les protocoles supportés.\nAnalyse la négociation TLS.\nIdentifie les protocoles modernes.\nTest passif et sûr.",
        "http-userdir-enum": "Énumération utilisateurs web\nRecherche les répertoires utilisateurs.\nTeste les chemins communs.\nPeut révéler des comptes actifs.\nRisque de détection.",
        "ssl-poodle": "Test POODLE\nVérifie la vulnérabilité POODLE.\nAnalyse la configuration SSLv3.\nTest non intrusif.\nCritique pour la sécurité SSL.",
        "http-sql-injection": "Détection injection SQL\nRecherche les vulnérabilités SQL injection.\nTeste les paramètres web.\nPeut être très intrusif.\nNécessite autorisation explicite.",
        "http-wordpress-enum": "Énumération WordPress\nDétecte les installations WordPress.\nÉnumère plugins et thèmes.\nIdentifie les versions.\nPeut être détecté.",
        "http-shellshock": "Test Shellshock\nVérifie la vulnérabilité Shellshock.\nTest ciblé sur CGI.\nPeut être dangereux.\nRequiert prudence.",
        "smb-vuln-ms17-010": "Test EternalBlue\nVérifie la vulnérabilité MS17-010.\nTest SMB spécifique.\nCritique pour Windows.\nPeu intrusif.",
        "smtp-vuln-cve2010-4344": "Vulnérabilité SMTP\nTest exploit Exim SMTP.\nVérification spécifique.\nPeu intrusif.\nImportant pour serveurs mail.",
        "rdp-vuln-ms12-020": "Vulnérabilité RDP\nTest MS12-020.\nVérification DoS RDP.\nPeu intrusif.\nCritique pour Windows.",
        "http-csrf": "Détection CSRF\nRecherche vulnérabilités CSRF.\nAnalyse formulaires web.\nTest non intrusif.\nImportant pour sécurité web.",
        "http-dombased-xss": "XSS basé sur DOM\nDétecte XSS dans le DOM.\nAnalyse JavaScript.\nTest passif.\nSécurité applications web.",
        "http-phpself-xss": "XSS via PHP_SELF\nRecherche XSS dans PHP_SELF.\nTest spécifique PHP.\nPeu intrusif.\nVulnérabilité commune.",
        "http-stored-xss": "XSS persistant\nDétecte XSS stocké.\nTest formulaires.\nPeut être intrusif.\nNécessite autorisation.",
        "http-passwd": "Fichiers mot de passe\nRecherche fichiers sensibles.\nTest chemins communs.\nPeu intrusif.\nImportant pour sécurité.",
        "http-config-backup": "Backups configuration\nRecherche sauvegardes config.\nTest chemins standards.\nPeu intrusif.\nRisque divulgation.",
        "http-backup-finder": "Fichiers backup\nRecherche copies backup.\nTest extensions communes.\nPeu intrusif.\nRisque information.",
        "http-git": "Détection Git\nRecherche dépôts Git exposés.\nTest chemins standard.\nNon intrusif.\nRisque code source.",
        "http-webdav-scan": "Scan WebDAV\nTest configuration WebDAV.\nVérifie méthodes.\nPeu intrusif.\nRisques configuration.",
        "http-iis-webdav-vuln": "Vulnérabilités WebDAV IIS\nTest WebDAV sur IIS.\nRecherche vulnérabilités.\nPeu intrusif.\nServeurs Windows.",
        "http-vuln-cve2017-5638": "Apache Struts\nTest CVE-2017-5638.\nVulnérabilité Struts.\nPeut être dangereux.\nServeurs Java.",
        "http-vuln-cve2017-1001000": "Drupal Vulnérabilité\nTest Drupalgeddon.\nVulnérabilité critique.\nPeut être dangereux.\nSites Drupal.",
        "smb-double-pulsar-backdoor": "Backdoor DoublePulsar\nDétecte backdoor NSA.\nTest SMB spécifique.\nPeu intrusif.\nMalware Windows.",
        "ssl-dh-params": "Paramètres Diffie-Hellman\nAnalyse config DH.\nTest cryptographie.\nNon intrusif.\nSécurité SSL/TLS.",
        "ssl-known-key": "Clés SSL connues\nRecherche clés compromises.\nTest certificats.\nNon intrusif.\nSécurité SSL/TLS.",
        "sshv1": "Test SSHv1\nDétecte protocole obsolète.\nTest version SSH.\nNon intrusif.\nSécurité SSH.",
        "ftp-vsftpd-backdoor": "Backdoor vsftpd\nRecherche backdoor connue.\nTest version spécifique.\nPeu intrusif.\nServeurs FTP.",
        "ftp-proftpd-backdoor": "Backdoor ProFTPD\nRecherche backdoor connue.\nTest version spécifique.\nPeu intrusif.\nServeurs FTP.",
        "mysql-vuln-cve2012-2122": "Vulnérabilité MySQL\nTest CVE-2012-2122.\nBypass authentification.\nPeu intrusif.\nServeurs MySQL.",
        "ms-sql-info": "Information MSSQL\nCollecte info SQL Server.\nTest configuration.\nPeu intrusif.\nServeurs Windows.",
        "oracle-sid-brute": "Force brute SID Oracle\nRecherche SID valides.\nTest brutal.\nPeut être détecté.\nBases Oracle.",
        "redis-info": "Information Redis\nCollecte info Redis.\nTest configuration.\nPeu intrusif.\nServeurs Redis.",
        "mongodb-info": "Information MongoDB\nCollecte info MongoDB.\nTest configuration.\nPeu intrusif.\nBases MongoDB.",
        "cassandra-info": "Information Cassandra\nCollecte info Cassandra.\nTest configuration.\nPeu intrusif.\nBases Cassandra.",
        "memcached-info": "Information Memcached\nCollecte info Memcached.\nTest configuration.\nPeu intrusif.\nServeurs cache.",
        "telnet-encryption": "Chiffrement Telnet\nTest crypto Telnet.\nVérifie sécurité.\nNon intrusif.\nServeurs Telnet.",
        "vnc-info": "Information VNC\nCollecte info VNC.\nTest configuration.\nPeu intrusif.\nServeurs VNC.",
        "realvnc-auth-bypass": "Bypass auth RealVNC\nTest vulnérabilité auth.\nPeut être dangereux.\nServeurs RealVNC.\nNécessite prudence.",
        "dns-zone-transfer": "Transfert de zone DNS\nTente transfert de zone.\nTest configuration.\nPeu intrusif.\nServeurs DNS.",
        "dns-srv-enum": "Énumération SRV DNS\nRecherche enregistrements SRV.\nTest DNS standard.\nNon intrusif.\nInfrastructure DNS.",
        "dhcp-discover": "Découverte DHCP\nTest serveurs DHCP.\nCollecte configuration.\nPeu intrusif.\nRéseau local.",
        "broadcast-ping": "Ping broadcast\nTest réponse broadcast.\nScan réseau local.\nPeu intrusif.\nDécouverte hôtes.",
        "ipv6-multicast-mld-list": "Liste multicast IPv6\nÉnumère groupes multicast.\nTest IPv6.\nPeu intrusif.\nRéseau local.",
        "targets-ipv6-multicast-echo": "Echo multicast IPv6\nTest réponse multicast.\nScan IPv6.\nPeu intrusif.\nDécouverte hôtes.",
        "targets-ipv6-multicast-invalid-dst": "Test multicast IPv6 invalide\nTest gestion erreurs.\nScan IPv6.\nPeu intrusif.\nSécurité réseau.",
        "broadcast-dhcp-discover": "Découverte DHCP broadcast\nRecherche serveurs DHCP.\nTest réseau local.\nPeu intrusif.\nInfrastructure réseau.",
        "broadcast-dns-service-discovery": "Découverte services DNS\nRecherche services mDNS.\nScan réseau local.\nPeu intrusif.\nServices réseau.",
        "broadcast-dropbox-listener": "Écoute Dropbox\nDétecte clients Dropbox.\nScan réseau local.\nPeu intrusif.\nServices cloud.",
        "broadcast-eigrp-discovery": "Découverte EIGRP\nDétecte routeurs EIGRP.\nScan réseau local.\nPeu intrusif.\nInfrastructure Cisco.",
        "broadcast-igmp-discovery": "Découverte IGMP\nDétecte groupes multicast.\nScan réseau local.\nPeu intrusif.\nMulticast IP.",
        "broadcast-listener": "Écoute broadcast\nCapture trafic broadcast.\nAnalyse passive.\nNon intrusif.\nAnalyse réseau.",
        "broadcast-netbios-master-browser": "Master Browser NetBIOS\nDétecte serveurs Windows.\nScan réseau local.\nPeu intrusif.\nRéseau Windows.",
        "broadcast-novell-locate": "Localisation Novell\nDétecte serveurs Novell.\nScan réseau local.\nPeu intrusif.\nRéseau Novell.",
        "broadcast-pc-anywhere": "Détection PCAnywhere\nRecherche hôtes PCAnywhere.\nScan réseau local.\nPeu intrusif.\nAccès distant.",
        "broadcast-pim-discovery": "Découverte PIM\nDétecte routeurs multicast.\nScan réseau local.\nPeu intrusif.\nRoutage multicast.",
        "broadcast-pppoe-discover": "Découverte PPPoE\nRecherche serveurs PPPoE.\nScan réseau local.\nPeu intrusif.\nAccès Internet.",
        "broadcast-rip-discover": "Découverte RIP\nDétecte routeurs RIP.\nScan réseau local.\nPeu intrusif.\nRoutage IP.",
        "broadcast-ripng-discover": "Découverte RIPng\nDétecte routeurs RIPng.\nScan IPv6.\nPeu intrusif.\nRoutage IPv6.",
        "broadcast-sybase-asa-discover": "Découverte Sybase ASA\nDétecte serveurs Sybase.\nScan réseau local.\nPeu intrusif.\nBases Sybase.",
        "broadcast-tellstick-discover": "Découverte TellStick\nDétecte périphériques TellStick.\nScan réseau local.\nPeu intrusif.\nDomotique.",
        "broadcast-upnp-info": "Information UPnP\nCollecte info UPnP.\nScan réseau local.\nPeu intrusif.\nServices réseau.",
        "broadcast-versant-locate": "Localisation Versant\nDétecte bases Versant.\nScan réseau local.\nPeu intrusif.\nBases Versant.",
        "broadcast-wake-on-lan": "Wake-on-LAN\nEnvoi paquets WoL.\nRéveil machines.\nPeu intrusif.\nGestion réseau.",
        "broadcast-wdb-discover": "Découverte WDB\nDétecte debuggers WDB.\nScan réseau local.\nPeu intrusif.\nDéveloppement.",
        "broadcast-wsdd-discover": "Découverte WSDD\nDétecte services web.\nScan réseau local.\nPeu intrusif.\nServices Windows.",
        "broadcast-xdmcp-discover": "Découverte XDMCP\nDétecte serveurs X.\nScan réseau local.\nPeu intrusif.\nAccès graphique.",
        "citrix-enum-servers": "Énumération serveurs Citrix\nListe serveurs Citrix.\nTest infrastructure.\nPeu intrusif.\nEnvironnement Citrix.",
        "citrix-enum-apps": "Énumération apps Citrix\nListe applications publiées.\nTest infrastructure.\nPeu intrusif.\nEnvironnement Citrix.",
        "dns-blacklist": "Liste noire DNS\nVérifie présence RBL.\nTest réputation.\nNon intrusif.\nSécurité mail.",
        "dns-cache-snoop": "Snooping cache DNS\nTest cache DNS.\nPeut être détecté.\nServeurs DNS.\nNécessite prudence.",
        "dns-check-zone": "Vérification zone DNS\nTest configuration zone.\nPeu intrusif.\nServeurs DNS.\nAdministration DNS.",
        "dns-client-subnet-scan": "Scan sous-réseaux DNS\nTest extension EDNS.\nPeu intrusif.\nServeurs DNS.\nConfiguration DNS.",
        "dns-fuzz": "Fuzzing DNS\nTest robustesse DNS.\nPeut être dangereux.\nServeurs DNS.\nTest stress.",
        "dns-ip6-arpa-scan": "Scan DNS IPv6\nRecherche PTR IPv6.\nPeu intrusif.\nServeurs DNS.\nInfrastructure IPv6.",
        "dns-nsec-enum": "Énumération NSEC\nTest DNSSEC NSEC.\nPeu intrusif.\nServeurs DNS.\nSécurité DNS.",
        "dns-nsec3-enum": "Énumération NSEC3\nTest DNSSEC NSEC3.\nPeu intrusif.\nServeurs DNS.\nSécurité DNS.",
        "dns-nsid": "Identification serveur DNS\nCollecte NSID.\nNon intrusif.\nServeurs DNS.\nAdministration DNS.",
        "dns-random-srcport": "Test port source DNS\nVérifie randomisation.\nPeu intrusif.\nServeurs DNS.\nSécurité DNS.",
        "dns-random-txid": "Test TXID DNS\nVérifie randomisation.\nPeu intrusif.\nServeurs DNS.\nSécurité DNS.",
        "dns-recursion": "Test récursion DNS\nVérifie récursion.\nPeu intrusif.\nServeurs DNS.\nConfiguration DNS.",
        "dns-service-discovery": "Découverte services DNS\nRecherche services DNS.\nPeu intrusif.\nRéseau local.\nServices réseau.",
        "dns-update": "Mise à jour DNS\nTest update DNS.\nPeut être dangereux.\nServeurs DNS.\nConfiguration DNS.",
        "domcon-cmd": "Commande DomCon\nTest interface DomCon.\nPeu intrusif.\nServeurs jeux.\nAdministration serveur.",
        "domino-enum-users": "Énumération Domino\nListe utilisateurs Domino.\nPeu intrusif.\nServeurs Domino.\nSécurité Lotus.",
        "dpap-brute": "Force brute DPAP\nTest auth DPAP.\nPeut être détecté.\nServices Apple.\nPhotos iPhoto.",
        "drda-brute": "Force brute DRDA\nTest auth DB2.\nPeut être détecté.\nBases DB2.\nSécurité IBM.",
        "drda-info": "Information DRDA\nCollecte info DB2.\nPeu intrusif.\nBases DB2.\nConfiguration IBM.",
        "duplicates": "Détection doublons\nRecherche duplicatas.\nAnalyse passive.\nNon intrusif.\nAudit réseau.",
        "eap-info": "Information EAP\nCollecte info 802.1X.\nPeu intrusif.\nRéseau WiFi.\nSécurité sans fil.",
        "enip-info": "Information EtherNet/IP\nCollecte info EtherNet/IP.\nPeu intrusif.\nRéseau industriel.\nAutomatisation.",
        "epmd-info": "Information EPMD\nCollecte info Erlang.\nPeu intrusif.\nServeurs Erlang.\nConfiguration Erlang.",
        "eppc-enum-processes": "Énumération processus EPPC\nListe processus Mac.\nPeu intrusif.\nMachines Apple.\nAdministration Mac."
    }
    print(f"\nAide pour le script NSE:\n{help_scripts.get(id_aide, 'Aucune aide disponible pour ce script.')}\n")

def poser_question(question, id_aide, default_value):
    while True:
        reponse = input(Fore.CYAN + f"{question} (O/N/help) {(Fore.GREEN + '[O]' + Style.RESET_ALL if default_value else Fore.RED + '[N]' + Style.RESET_ALL)}" + Fore.CYAN + ": " + Style.RESET_ALL).lower()
        if reponse in ['o', 'oui', 'yes', 'y']:
            return True
        elif reponse in ['n', 'non', 'no']:
            return False
        elif reponse in ['help','h','aide','?']:
            afficher_aide(id_aide)
        elif reponse == '':
            return default_value
        else:
            print("Réponse non valide. Veuillez répondre par 'o' pour oui, 'n' pour non, ou 'help' pour l'aide.")

def choisir_script(default_script):
    scripts_communs = [
        "default", "vuln", "version", "safe", "discovery", "auth", "brute", "exploit", "malware",
        "http-enum", "http-methods", "http-robots.txt", "http-sitemap-generator", "http-userdir-enum",
        "ssl-heartbleed", "sslv2", "ssl-enum-ciphers", "smb-os-discovery", "tls-nextprotoneg", "dns-brute", "ftp-anon",
        "ssh-auth-methods", "mysql-enum", "snmp-info", "http-title", "banner",
        "http-headers", "ssl-poodle", "http-sql-injection", "http-wordpress-enum",
        "http-shellshock", "smb-vuln-ms17-010", "smtp-vuln-cve2010-4344", "rdp-vuln-ms12-020",
        "http-csrf", "http-dombased-xss", "http-phpself-xss", "http-stored-xss",
        "http-passwd", "http-config-backup", "http-backup-finder", "http-git",
        "http-webdav-scan", "http-iis-webdav-vuln", "http-vuln-cve2017-5638",
        "http-vuln-cve2017-1001000", "smb-double-pulsar-backdoor", "ssl-dh-params",
        "ssl-known-key", "sshv1", "ftp-vsftpd-backdoor", "ftp-proftpd-backdoor",
        "mysql-vuln-cve2012-2122", "ms-sql-info", "oracle-sid-brute", "redis-info",
        "mongodb-info", "cassandra-info", "memcached-info", "telnet-encryption",
        "vnc-info", "realvnc-auth-bypass", "dns-zone-transfer", "dns-srv-enum",
        "dhcp-discover", "broadcast-ping", "ipv6-multicast-mld-list", "targets-ipv6-multicast-echo",
        "targets-ipv6-multicast-invalid-dst", "broadcast-dhcp-discover", "broadcast-dns-service-discovery",
        "broadcast-dropbox-listener", "broadcast-eigrp-discovery", "broadcast-igmp-discovery",
        "broadcast-listener", "broadcast-netbios-master-browser", "broadcast-novell-locate",
        "broadcast-pc-anywhere", "broadcast-pim-discovery", "broadcast-pppoe-discover",
        "broadcast-rip-discover", "broadcast-ripng-discover", "broadcast-sybase-asa-discover",
        "broadcast-tellstick-discover", "broadcast-upnp-info", "broadcast-versant-locate",
        "broadcast-wake-on-lan", "broadcast-wdb-discover", "broadcast-wsdd-discover",
        "broadcast-xdmcp-discover", "citrix-enum-servers", "citrix-enum-apps",
        "dns-blacklist", "dns-cache-snoop", "dns-check-zone", "dns-client-subnet-scan",
        "dns-fuzz", "dns-ip6-arpa-scan", "dns-nsec-enum", "dns-nsec3-enum",
        "dns-nsid", "dns-random-srcport", "dns-random-txid", "dns-recursion",
        "dns-service-discovery", "dns-update", "domcon-cmd", "domino-enum-users",
        "dpap-brute", "drda-brute", "drda-info", "duplicates", "eap-info",
        "enip-info", "epmd-info", "eppc-enum-processes"
    ]
    print("-" * 80)
    print(f"{'Top des scripts du plus utilisé au moins utilisé'}")
    print("-" * 80)
    
    # Afficher les scripts en 3 colonnes
    num_scripts = len(scripts_communs)
    rows = (num_scripts + 2) // 3  # Arrondir au supérieur
    
    for row in range(rows):
        col1 = f"{row+1}. {scripts_communs[row]}" if row < num_scripts else ""
        col2 = f"{row+rows+1}. {scripts_communs[row+rows]}" if row+rows < num_scripts else ""
        col3 = f"{row+2*rows+1}. {scripts_communs[row+2*rows]}" if row+2*rows < num_scripts else ""
        
        print(f"{col1:<30} {col2:<40} {col3}")
    
    print("-" * 80)
    
    while True:
        choix = input(Fore.CYAN + f"Choisissez un script (numéro) ou entrez un nom personnalisé (help <script/numéro> pour aide) [{default_script}]: " + Style.RESET_ALL)
        
        # Vérifier si c'est une demande d'aide
        if choix.lower().startswith('help') or choix.lower().startswith('h') or choix.lower().startswith('?'):
            help_parts = choix.split()
            if len(help_parts) > 1:
                script_help = help_parts[1]
                # Si c'est un numéro, convertir en nom de script
                if script_help.isdigit() and 1 <= int(script_help) <= len(scripts_communs):
                    script_help = scripts_communs[int(script_help) - 1]
                afficher_aide_script(script_help)
            continue
            
        elif choix.isdigit() and 1 <= int(choix) <= len(scripts_communs):
            return scripts_communs[int(choix) - 1]
        elif choix:
            # Supprimer l'extension .nse si présente
            if choix.endswith('.nse'):
                choix = choix[:-4]
            
            # Vérifier si le script personnalisé existe
            script_path = f"/usr/share/nmap/scripts/{choix}.nse"
            if os.path.exists(script_path):
                return choix
            else:
                print(Fore.RED + f"Erreur: Le script {choix}.nse n'existe pas dans /usr/share/nmap/scripts/" + Style.RESET_ALL)
                continue
        elif choix == '':
            return default_script
        else:
            print("Choix non valide. Veuillez entrer un numéro, un nom de script, ou 'help <script/numéro>' pour l'aide.")

def verifier_cible(cible):
    # Vérifier le format d'adresse IP
    try:
        ipaddress.ip_address(cible)
        return True
    except ValueError:
        pass

    # Vérifier le format de plage d'adresses IP
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(,\d{1,3})+$', cible):
        return True

    # Vérifier le format de nom de domaine
    if re.match(r'^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$', cible):
        return True

    # Vérifier le format d'adresse réseau avec masque
    try:
        ipaddress.ip_network(cible, strict=False)
        return True
    except ValueError:
        pass

    return False

def construire_commande_nmap(cible, options):
    commande = ["nmap"]
    
    if options['scan_furtif']:
        commande.append("-sS")
    elif options['scan_tcp_connect']:
        commande.append("-sT")
    elif options['scan_udp']:
        commande.append("-sU")
    
    if options['scan_rapide']:
        commande.extend(["--top-ports", options['top_ports']])
    elif options['tous_les_ports']:
        commande.append("-p-")
    elif options['ports_specifiques']:
        commande.extend(["-p", options['ports_specifiques']])
    
    if options['scan_os']:
        commande.append("-O")
    
    if options['scan_services']:
        commande.append("-sV")
    
    if options['scan_agressif']:
        commande.append("-A")

    if options['scripts_nse']:
        commande.extend(["--script", options['script_choisi']])
    
    if options['verbosite']:
        commande.append("-v")
    
    if options['mode_debug']:
        commande.append("-d")
    
    if options['interface_reseau']:
        commande.extend(["-e", options['interface_reseau']])
    
    if options['timing_template']:
        commande.extend(["-T", options['timing_template']])

    # Ajouter l'option exclude_hosts seulement pour les adresses réseau ou noms de domaine
    try:
        ipaddress.ip_address(cible)
    except ValueError:
        if options['exclude_hosts']:
            commande.extend(["--exclude", options['exclude_hosts']])

    if options['output']:
        if options['output'].endswith('.xml'):
            commande.extend(["-oX", options['output']])
        else:
            commande.extend(["-oN", options['output']])
    
    commande.append(cible)
    
    return commande

def executer_nmap(stdscr, commande):
    debut_temps = time.time()
    curses.curs_set(0)
    stdscr.clear()
    
    # Initialisation des couleurs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # Créer une fenêtre pour le scrolling
    hauteur, largeur = stdscr.getmaxyx()
    pad = curses.newpad(1000, largeur - 1)  # Créer un pad avec une grande hauteur

    # Afficher l'ASCII art
    stdscr.attron(curses.color_pair(4))
    for i, line in enumerate(start.split('\n')):
        stdscr.addstr(i, 0, line)
    stdscr.attroff(curses.color_pair(4))

    # Afficher les informations dans l'en-tête
    start_y = len(start.split('\n')) + 1
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(start_y, 0, f"Commande: {' '.join(commande)}")
    stdscr.attroff(curses.color_pair(1))
    stdscr.addstr(start_y + 2, 0, "Résultats du scan:")
    stdscr.refresh()

    try:
        process = subprocess.Popen(commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        pad_y = 0
        output = []
        for line in process.stdout:
            pad.addstr(pad_y, 0, line.strip()[:largeur-1])
            pad_y += 1
            output.append(line.strip())
            
            # Scroll le pad si nécessaire
            if pad_y > hauteur - start_y - 10:
                pad.refresh(pad_y - (hauteur - start_y - 10), 0, start_y + 4, 0, hauteur - 6, largeur - 1)
            else:
                pad.refresh(0, 0, start_y + 4, 0, hauteur - 6, largeur - 1)
            
            stdscr.refresh()
        
        process.wait()
        
        fin_temps = time.time()
        temps_execution = fin_temps - debut_temps
        minutes = int(temps_execution // 60)
        secondes = int(temps_execution % 60)
        stdscr.addstr(hauteur - 5, 0, f"Scan terminé en {minutes} minutes et {secondes} secondes. Utilisez les flèches pour scroller, 'q' pour quitter.")
        stdscr.refresh()

        # Permettre le scrolling après la fin du scan
        current_line = 0
        while True:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == curses.KEY_UP and current_line > 0:
                current_line -= 1
            elif key == curses.KEY_DOWN and current_line < max(0, pad_y - (hauteur - start_y - 10)):
                current_line += 1
            pad.refresh(current_line, 0, start_y + 4, 0, hauteur - 6, largeur - 1)
        
        return output
    
    except KeyboardInterrupt:
        process.terminate()
        fin_temps = time.time()
        temps_execution = fin_temps - debut_temps
        minutes = int(temps_execution // 60)
        secondes = int(temps_execution % 60)
        stdscr.addstr(hauteur - 5, 0, f"Scan interrompu après {minutes} minutes et {secondes} secondes. Appuyez sur une touche pour quitter.")
        stdscr.refresh()
        stdscr.getch()
        return []

def sauvegarder_config(options):
    with open(__file__, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith('CIBLE_DEFAULT'):
            lines[i] = f'CIBLE_DEFAULT = "{options["cible"]}"\n'
        elif line.startswith('SCAN_FURTIF_DEFAULT'):
            lines[i] = f'SCAN_FURTIF_DEFAULT = {options["scan_furtif"]}\n'
        elif line.startswith('SCAN_TCP_CONNECT_DEFAULT'):
            lines[i] = f'SCAN_TCP_CONNECT_DEFAULT = {options["scan_tcp_connect"]}\n'
        elif line.startswith('SCAN_UDP_DEFAULT'):
            lines[i] = f'SCAN_UDP_DEFAULT = {options["scan_udp"]}\n'
        elif line.startswith('TOUS_LES_PORTS_DEFAULT'):
            lines[i] = f'TOUS_LES_PORTS_DEFAULT = {options["tous_les_ports"]}\n'
        elif line.startswith('PORTS_SPECIFIQUES_DEFAULT'):
            lines[i] = f'PORTS_SPECIFIQUES_DEFAULT = "{options["ports_specifiques"]}"\n'
        elif line.startswith('SCAN_RAPIDE_DEFAULT'):
            lines[i] = f'SCAN_RAPIDE_DEFAULT = {options["scan_rapide"]}\n'
        elif line.startswith('TOP_PORTS_DEFAULT'):
            lines[i] = f'TOP_PORTS_DEFAULT = "{options["top_ports"]}"\n'
        elif line.startswith('SCAN_OS_DEFAULT'):
            lines[i] = f'SCAN_OS_DEFAULT = {options["scan_os"]}\n'
        elif line.startswith('SCAN_SERVICES_DEFAULT'):
            lines[i] = f'SCAN_SERVICES_DEFAULT = {options["scan_services"]}\n'
        elif line.startswith('SCAN_AGRESSIF_DEFAULT'):
            lines[i] = f'SCAN_AGRESSIF_DEFAULT = {options["scan_agressif"]}\n'
        elif line.startswith('SCRIPTS_NSE_DEFAULT'):
            lines[i] = f'SCRIPTS_NSE_DEFAULT = {options["scripts_nse"]}\n'
        elif line.startswith('SCRIPT_CHOISI_DEFAULT'):
            lines[i] = f'SCRIPT_CHOISI_DEFAULT = "{options["script_choisi"]}"\n'
        elif line.startswith('VERBOSITE_DEFAULT'):
            lines[i] = f'VERBOSITE_DEFAULT = {options["verbosite"]}\n'
        elif line.startswith('MODE_DEBUG_DEFAULT'):
            lines[i] = f'MODE_DEBUG_DEFAULT = {options["mode_debug"]}\n'
        elif line.startswith('INTERFACE_RESEAU_DEFAULT'):
            lines[i] = f'INTERFACE_RESEAU_DEFAULT = "{options["interface_reseau"]}"\n'
        elif line.startswith('TIMING_TEMPLATE_DEFAULT'):
            lines[i] = f'TIMING_TEMPLATE_DEFAULT = "{options["timing_template"]}"\n'
        elif line.startswith('EXCLUDE_HOSTS_DEFAULT'):
            lines[i] = f'EXCLUDE_HOSTS_DEFAULT = "{options["exclude_hosts"]}"\n'
        elif line.startswith('OUTPUT_DEFAULT'):
            if options["output"] == "":
                lines[i] = 'OUTPUT_DEFAULT = ""\n'
            else:
                lines[i] = f'OUTPUT_DEFAULT = "{options["output"]}"\n'

    with open(__file__, 'w') as file:
        file.writelines(lines)


def demander_config():
    options = {
        "cible": CIBLE_DEFAULT,
        "scan_furtif": SCAN_FURTIF_DEFAULT,
        "scan_tcp_connect": SCAN_TCP_CONNECT_DEFAULT, 
        "scan_udp": SCAN_UDP_DEFAULT,
        "tous_les_ports": TOUS_LES_PORTS_DEFAULT,
        "ports_specifiques": PORTS_SPECIFIQUES_DEFAULT,
        "scan_rapide": SCAN_RAPIDE_DEFAULT,
        "top_ports": TOP_PORTS_DEFAULT,
        "scan_os": SCAN_OS_DEFAULT,
        "scan_services": SCAN_SERVICES_DEFAULT,
        "scan_agressif": SCAN_AGRESSIF_DEFAULT,
        "scripts_nse": SCRIPTS_NSE_DEFAULT,
        "script_choisi": SCRIPT_CHOISI_DEFAULT,
        "verbosite": VERBOSITE_DEFAULT,
        "mode_debug": MODE_DEBUG_DEFAULT,
        "interface_reseau": INTERFACE_RESEAU_DEFAULT,
        "timing_template": TIMING_TEMPLATE_DEFAULT,
        "exclude_hosts": EXCLUDE_HOSTS_DEFAULT,
        "output": OUTPUT_DEFAULT
    }

    print("Config par défaut :")
    print(Fore.CYAN + "-" * 100 + Style.RESET_ALL)

    # Trier les options
    items = list(options.items())
    
    # Séparer la cible et trier le reste des options
    cible = next(item for item in items if item[0] == "cible")
    autres_items = [item for item in items if item[0] != "cible"]
    
    # Trier les autres items - True/non-vide d'abord
    def tri_priorite(item):
        if isinstance(item[1], bool):
            return (0 if item[1] else 1, item[0])
        else:
            return (0 if item[1] else 1, item[0])
            
    autres_items.sort(key=tri_priorite)
    
    # Recombiner avec la cible en premier
    items = [cible] + autres_items
    
    num_items = len(items)
    rows = (num_items + 2) // 3

    # Afficher les options en 3 colonnes
    for row in range(rows):
        def format_value(key, value):
            display_key = key.replace("_", " ")
            if key == "cible":
                return f"{display_key}: {Fore.YELLOW}{value}{Style.RESET_ALL}"
            elif isinstance(value, bool):
                if not value:
                    return f"{Fore.LIGHTBLACK_EX}{display_key}: {value}{Style.RESET_ALL}"
                else:
                    return f"{display_key}: {Fore.GREEN}{value}{Style.RESET_ALL}"
            else:
                if not value:
                    return f"{Fore.LIGHTBLACK_EX}{display_key}: False{Style.RESET_ALL}"
                else:
                    return f"{display_key}: {Fore.GREEN}{value}{Style.RESET_ALL}"
        
        # Calculer la longueur réelle sans les codes ANSI
        def strip_ansi(text):
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            return ansi_escape.sub('', text)
            
        col1 = format_value(items[row][0], items[row][1]) if row < num_items else ""
        col2 = format_value(items[row+rows][0], items[row+rows][1]) if row+rows < num_items else ""
        col3 = format_value(items[row+2*rows][0], items[row+2*rows][1]) if row+2*rows < num_items else ""
        
        # Calculer les largeurs réelles
        width1 = len(strip_ansi(col1))
        width2 = len(strip_ansi(col2))
        
        # Ajouter des espaces pour aligner
        padding1 = " " * (39 - width1) if width1 < 39 else " "
        padding2 = " " * (39 - width2) if width2 < 39 else " "
        
        print(f"{col1}{padding1}{col2}{padding2}{col3}")
    
    print(Fore.CYAN + "-" * 100 + Style.RESET_ALL)

    # Construire et afficher la commande nmap
    commande = f"nmap "
    if options["scan_furtif"]:
        commande += "-sS "
    if options["scan_tcp_connect"]:
        commande += "-sT "
    if options["scan_udp"]:
        commande += "-sU "
    if options["scan_rapide"]:
        commande += f"--top-ports {options['top_ports']} "
    elif options["tous_les_ports"]:
        commande += "-p- "
    elif options["ports_specifiques"]:
        commande += f"-p {options['ports_specifiques']} "
    if options["scan_os"]:
        commande += "-O "
    if options["scan_services"]:
        commande += "-sV "
    if options["scan_agressif"]:
        commande += "-A "
    if options["scripts_nse"]:
        commande += f"--script={options['script_choisi']} "
    if options["verbosite"]:
        commande += "-v "
    if options["mode_debug"]:
        commande += "-d "
    if options["interface_reseau"]:
        commande += f"-e {options['interface_reseau']} "
    if options["timing_template"]:
        commande += f"-T {options['timing_template']} "
    if options["exclude_hosts"]:
        commande += f"--exclude {options['exclude_hosts']} "
    if options["output"]:
        ext = options["output"].split(".")[-1]
        commande += f"-o{ext} {options['output']} "
    commande += options["cible"]

    print(f"Commande actuelle: {Fore.LIGHTCYAN_EX}{commande}{Style.RESET_ALL}\n")

    if input("Utiliser la config par defaut ? (O/n) :").lower() != "n":
        return options

    while True:
        options["cible"] = input(Fore.CYAN + "Entrez une IP, une plage d'IP, un nom de domaine ou une adresse réseau/masque : [" + Fore.YELLOW + Style.BRIGHT + f"{CIBLE_DEFAULT}" + Style.NORMAL + Fore.CYAN + "]: " + Style.RESET_ALL) or CIBLE_DEFAULT
        if verifier_cible(options["cible"]):
            break
        else:
            print(Fore.RED + "Format de cible invalide. Veuillez réessayer." + Style.RESET_ALL)

    # Demander les hôtes à exclure seulement si la cible n'est pas une adresse IP unique
    try:
        ipaddress.ip_address(options["cible"])
        options["exclude_hosts"] = ""
    except ValueError:
        options["exclude_hosts"] = input(Fore.CYAN + f"Entrez les hôtes à exclure (séparés par des virgules) [{EXCLUDE_HOSTS_DEFAULT}]: " + Style.RESET_ALL) or EXCLUDE_HOSTS_DEFAULT

    options["scan_furtif"] = poser_question("Voulez-vous effectuer un scan furtif (SYN scan) ?", "scan_furtif", SCAN_FURTIF_DEFAULT)
    if not options["scan_furtif"]:
        options["scan_tcp_connect"] = poser_question("Voulez-vous effectuer un scan TCP connect ?", "scan_tcp_connect", SCAN_TCP_CONNECT_DEFAULT)
    if not options["scan_furtif"] and not options["scan_tcp_connect"]:
        options["scan_udp"] = poser_question("Voulez-vous effectuer un scan UDP ?", "scan_udp", SCAN_UDP_DEFAULT)

    options["scan_rapide"] = poser_question("Voulez-vous effectuer un scan rapide ?", "scan_rapide", SCAN_RAPIDE_DEFAULT)
    if options["scan_rapide"]:
        while True:
            options["top_ports"] = input(Fore.CYAN + f"Entrez le nombre de ports les plus courants à scanner (ex: 100) [{TOP_PORTS_DEFAULT}]: " + Style.RESET_ALL) or TOP_PORTS_DEFAULT
            if options["top_ports"].isdigit():
                break
            print(Fore.RED + "Veuillez entrer un nombre valide." + Style.RESET_ALL)
        options["ports_specifiques"] = ""  # Écraser ports_specifiques si scan_rapide est true
    if not options["scan_rapide"]:
        options["top_ports"] = ""
        options["tous_les_ports"] = poser_question("Voulez-vous scanner tous les ports ?", "tous_les_ports", TOUS_LES_PORTS_DEFAULT)
        if not options["tous_les_ports"]:
            options["ports_specifiques"] = input(Fore.CYAN + f"Entrez les ports à scanner (ex: 80-443,8080) ou laissez vide pour les ports par défaut [{PORTS_SPECIFIQUES_DEFAULT}]: " + Style.RESET_ALL) or PORTS_SPECIFIQUES_DEFAULT

    options["scan_os"] = poser_question("Voulez-vous scanner les systèmes d'exploitation ?", "systemes_exploitation", SCAN_OS_DEFAULT)
    options["scan_services"] = poser_question("Voulez-vous scanner les noms de services ?", "noms_services", SCAN_SERVICES_DEFAULT)
    options["scan_agressif"] = poser_question("Voulez-vous effectuer un scan agressif ?", "scan_agressif", SCAN_AGRESSIF_DEFAULT)
    options["scripts_nse"] = poser_question("Voulez-vous utiliser des scripts NSE ?", "scripts_nse", SCRIPTS_NSE_DEFAULT)
    if options["scripts_nse"]:
        options["script_choisi"] = choisir_script(SCRIPT_CHOISI_DEFAULT)
        if options["script_choisi"] == "":
            options["scripts_nse"] = False
    else:
        options["script_choisi"] = ""

    options["verbosite"] = poser_question("Voulez-vous augmenter le niveau de verbosité ?", "verbosite", VERBOSITE_DEFAULT)
    options["mode_debug"] = poser_question("Voulez-vous activer le mode debug ?", "mode_debug", MODE_DEBUG_DEFAULT)
    while True:
        options["interface_reseau"] = input(Fore.CYAN + f"Entrez le nom de l'interface réseau (vide par défaut) ou help : " + Style.RESET_ALL) or INTERFACE_RESEAU_DEFAULT
        if options["interface_reseau"] in ['help','h','aide','?']:
            afficher_aide("timing_template")
            continue
        else :
            break
        
    while True:
        options["timing_template"] = input(Fore.CYAN + f"Entrez le niveau de timing (0-5 / 3 par defaut) ou help : " + Style.RESET_ALL) or "3"
        if options["timing_template"] in ['help','h','aide','?']:
            afficher_aide("timing_template")
            continue
        if options["timing_template"].isdigit() and 0 <= int(options["timing_template"]) <= 5:
            if options["timing_template"] == "3":
                options["timing_template"] = ""
            break
        print(Fore.RED + "Le niveau de timing doit être un nombre entre 0 et 5." + Style.RESET_ALL)

    output_file = input(Fore.CYAN + "Entrez le nom du fichier de sortie en extension .txt ou .xml (laissez vide pour ne pas sauvegarder) : " + Style.RESET_ALL)
    if output_file:
        if output_file.endswith('.txt') or output_file.endswith('.xml'):
            options["output"] = output_file
        else:
            print(Fore.RED + "Extension de fichier non valide. Aucun fichier de sortie ne sera créé." + Style.RESET_ALL)
            options["output"] = ""
    else:
        options["output"] = ""

    sauvegarder_config(options)
    print(Fore.GREEN + "Configuration sauvegardée dans le code." + Style.RESET_ALL)

    return options

def main():
    try:
        options = demander_config()
        commande = construire_commande_nmap(options["cible"], options)
        print(Fore.GREEN + "Commande qui va être exécutée :" + Style.RESET_ALL, " ".join(commande))
        if poser_question("Voulez-vous exécuter cette commande ?", "execution_commande", True):
            resultat = curses.wrapper(executer_nmap, commande)
            print(Fore.GREEN + "Résultat du scan Nmap :" + Style.RESET_ALL)
            for ligne in resultat:
                print(ligne)
        else:
            print(Fore.RED + "Exécution annulée." + Style.RESET_ALL)
    
    except KeyboardInterrupt:
        print(Fore.RED + "\nExécution interrompue par l'utilisateur." + Style.RESET_ALL)

if __name__ == "__main__":
    main()

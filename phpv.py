#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path as path
import os
import subprocess
import time
import datetime
import json


#Version 1.2



class bcolors:
    HEADER      = '\033[95m'
    OKBLUE      = '\033[94m'
    OKGREEN     = '\033[92m'
    WARNING     = '\033[93m'
    FAIL        = '\033[91m'
    ENDC        = '\033[0m'
    BOLD        = '\033[1m'
    UNDERLINE   = '\033[4m'
 
cont            = 0
versionActual   = ""
indicePHP       = {}
index_module    = {}
mods_available  = {}
mods_enabled    = {}
restart         = False        
num_registro    = 0
msg_salida      = "Sin mensaje"
msg             = ""
msg_x           = "ERROR"
config_json     = ""

def leer_log_local():
    log = open("phpv.log","r")
    logs = log.read()    
    print str(logs)
    log.close
   
def escribir_log_local(tipo,reg):
    global num_registro
    fecha = datetime.datetime.now()
    log = open("phpv.log","a")
    log.write("\nNº["+ str(num_registro) +"]  ["+ str(fecha) + "]\t"+str(tipo)+"->[ "+str(reg)+" ]") 
    log.close()
    num_registro =  int(num_registro) + 1   

def leer_archivo(archivo):
    file = open(archivo,"r")
    texto = file.read()    
    print str(texto)
    file.close

def info_user():   
    user_name =  subprocess.check_output("whoami", shell=True)
    home_home =  subprocess.check_output("cd ~ && pwd", shell=True)
    return user_name

def reiniciar_apache():
    os.system("sudo service apache2 restart")
    escribir_log_local("EXEC ","reiniciar_apache()")
    restart = False

def leer_apache_conf():
    os.system("cat /etc/apache2/apache2.conf | grep -v '#' ")

def automargen(parte2, parte1):
    #part1 = "### "+ sub_menu['name']    
    len_parte1 = len(parte1)
    part_2 = parte2 - len_parte1
    espacios =  " "*part_2
    return espacios  

def cargar_config_json():
    with open('config.json') as file:
        config_json = json.load(file)
        return config_json        
        #for submenu in data['submenu']:
        #   print submenu["name"]
    
def mostrar_mensaje(new_msg, type=""):    
    global msg
    escribir_log_local("MSG ", str(new_msg))
    new_msg = str(new_msg)

    print "*"*35
    print "***" + new_msg.center(26,' ') +  automargen(1, new_msg.center(29,' ')) +"   ***"
    print "*"*35
    msg=""
    msg_salida=""
   
def comprobar_version_php_funcionando():
    global versionActual
    out = subprocess.check_output("php -v", shell=True)
    versionActual = out[4:7]
    escribir_log_local("   ACTION","comprobar_version_php_funcionando = php"+str(versionActual))
    return versionActual

def cambiar_version_php(ver):
    #version = "5.6"   
    global indicePHP
    global versionActual  
    global restart 
    ver = int(ver) - 1
    version = indicePHP[ver]
    try:
        escribir_log_local("FUNCTION","cambiar_version_php("+str(ver)+")")
        subprocess.check_output("sudo a2dismod php"+str(versionActual), shell=True)
        print  bcolors.OKGREEN +"OK -> " + bcolors.ENDC +"Desactivando modulo PHP " + str(versionActual)     
        time.sleep(.8)
        escribir_log_local("  ACCTION","Desactivando modulo PHP "+str(versionActual))
    
        subprocess.check_output("sudo a2enmod php"+version, shell=True)
        print bcolors.OKGREEN +"OK -> " +  bcolors.ENDC +"Activando modulo PHP " + version
        time.sleep(.8)   
        escribir_log_local("  ACCTION","Activando modulo PHP "+str(version))
        reiniciar_apache() 
        print bcolors.OKGREEN +"OK -> " +  bcolors.ENDC +"Reiniciando Apache "
        time.sleep(.8)

        subprocess.check_output("sudo update-alternatives --set php /usr/bin/php" + str(version), shell=True) 
        print bcolors.OKGREEN +"OK -> Version actual PHP-" + str(version)   +  bcolors.ENDC     
        escribir_log_local("  ACCTION","Update-alternatives "+str(version))
        time.sleep(1)
        reiniciar_apache()
        restart = False
        
        mostrar_menu()
        pass
    except:
        print "except"    
   
def listar_modulos_php():     
    escribir_log_local("FUNCTION","listar_modulos_php")
    global index_module
    global mods_available
    global mods_enabled
    global restart
    mods_available        = subprocess.check_output("ls /etc/apache2/mods-available", shell=True)
    mods_enabled          = subprocess.check_output("ls /etc/apache2/mods-enabled", shell=True)
    
    mods_available  =  mods_available.split('\n')
    mods_enabled    =  mods_enabled.split('\n')   
    index_cont      = 0
    for available in  mods_available:
        if (available):
            conti = 0
            if  available in mods_enabled:
                print "|" + str(index_cont) + "|"+bcolors.OKGREEN + available +  bcolors.ENDC   
                index_module[index_cont] = available  
                index_cont = index_cont +1
                # if index_cont%5==0:
                #     print "\n"       
            else:
                print "|" + str(index_cont) + "|"+bcolors.OKBLUE + available +  bcolors.ENDC
                index_module[index_cont] = available 
                index_cont = index_cont +1 
                # if index_cont%5==0:
                #     print "\n"     
   
    # Imprimimos menu
    apache_status()
    print "#"*35
    print "###      "+ bcolors.OKBLUE +"  PHP MODULES      "+  bcolors.ENDC +"    ###"  
    mod = raw_input("##   "+bcolors.OKBLUE + "        (q=Close)      "+bcolors.ENDC +"    ###\n"+"#"*35 +  "\nNumero de modulo -> ")             
            
    if (mod == "q"): 
        os.system("clear")                         
        mostrar_menu() 

    if (mod == "m"): 
        os.system("clear")                         
        sub_menu()

    if (mod == "y"):
        reiniciar_apache()      
        restart = False
        listar_modulos_php()
    else:
        mod = int(mod)
        cambiar_estado_modulo_php(mod)
        listar_modulos_php()  

def cambiar_estado_modulo_php(mod): 
    global index_module
    global mods_enabled
    global restart 

    mod = int(mod)
    module_name = str(index_module[mod])
    escribir_log_local("FUNCTION","cambiar_estado_modulo_php( "+str(module_name)+" )")
    if (module_name in mods_enabled):          
        module_name = module_name.replace(".conf", "")  
        module_name = module_name.replace(".load", "")  
        os.system("sudo a2dismod " + module_name) 
        restart = True  
        msg = bcolors.FAIL   +"Cambiado estado a Disabled -> " + str(module_name)   +  bcolors.ENDC + bcolors.OKBLUE +"\nIntroduce el numero de modulo:" +  bcolors.ENDC 
        mostrar_mensaje("ACCTION","Cambiado a DISABLE el modulo ("+str(module_name)+")")
        escribir_log_local("   ACCTION","Cambiado a DISABLE el modulo ("+str(module_name)+")")
        print msg
    else:       
        module_name = module_name.replace(".conf", "")  
        module_name = module_name.replace(".load", "")  
        os.system("sudo a2enmod " + module_name)
        restart = True
        msg = bcolors.OKGREEN +"Cambiado estado a Enabled -> " + str(module_name)   +  bcolors.ENDC + bcolors.OKBLUE +"\nIntroduce el numero de modulo:" +  bcolors.ENDC  
        escribir_log_local("   ACCTION","Cambiado a ENABLE el modulo ("+str(module_name)+")")
        print msg
    listar_modulos_php()
    
def apache_status():
    escribir_log_local("   MODULE","Cargado apache_status")
    global versionActual 
    if(restart):
        print "#"*35    
        print "#¡¡¡     "+ bcolors.FAIL   +"Restart Apache (y)" +  bcolors.ENDC +"    !!!!"
        print "#"*35
    
    else:        
        print "#"*35
        print "#---      "+ bcolors.OKGREEN +"Apache PHP "+versionActual+""+  bcolors.ENDC +"       ---#"
        print "#"*35

def instalar_phpv(): 
   
    global msg  
    #existe = open("~/script/phpv/phpv.py","r")
    if os.path.isfile("~/3_Script/phpv/phpv.py"):
        print "phpv ya esta instalado"
        mostrar_menu()
    else:      
        alias =  'echo \'alias phpv="cd ~/3_Script/phpv/ && python phpv.py"\''
        path  =  ">> ~/.bashrc"

        print  bcolors.OKGREEN +"OK -> " + bcolors.ENDC +"Creando carpeta ~/3_Script/phpv"
        os.system("cd ~ &&  mkdir 3_Script && cd 3_Script && mkdir phpv")    
        time.sleep(1) 

        os.system("wget -O ~/3_Script/phpv/config.json   https://github.com/ReosCli/phpv/raw/master/config.json")
        
        print  bcolors.OKGREEN +"OK -> " + bcolors.ENDC +"Copiando archivos a ~/3_Script/phpv"  
        os.system("cp phpv.py ~/3_Script/phpv" )      
        time.sleep(1)

        print  bcolors.OKGREEN +"OK -> " + bcolors.ENDC +"Creando alias phpv" 
        os.system(alias + path) 

        print  bcolors.OKGREEN +"OK -> Instalación completa " + bcolors.ENDC
        time.sleep(2)

        os.system("~/.bashrc")       
      
  
   
def menu_modulos_php():
    escribir_log_local("   MODULE","Cargado menu_modulos_php")
    global cont
    print "#"*35
    print "###           "+ bcolors.WARNING +"PHP MODS  "+  bcolors.ENDC +"        ###"
    print "###"+ bcolors.OKBLUE +" Options ->  "+  bcolors.ENDC +"|"+str(cont)+"|             ###"
    cont = int(cont) + 1     
    print "#"*35

def menu_versiones_php():    
    escribir_log_local("   MODULE","Cargado menu_versiones_php")
    global cont    
    global versionActual    
    versionsAvailable = subprocess.check_output("ls /etc/apache2/mods-available/php*.conf", shell=True)
    lines = versionsAvailable.split("\n")    
    install_version = []
    for line in lines:   
        ini = line.find("php")
        version = line[ini+3:ini+6]    
        install_version.append(version)
        
    print "#"*35
    print "###        "+ bcolors.WARNING +" CHANGE PHP   "+  bcolors.ENDC +"       ###"    
    for i in range(len(install_version)):
        if(install_version[i]):       
           
            if(versionActual == install_version[i]):
                print "### " + bcolors.OKGREEN + "UP--"+ install_version[i] +  bcolors.ENDC + automargen(25, "UP--"+ install_version[i])+"   ###" 
            else:                             
                indicePHP[cont]=install_version[i]
                print "### " + bcolors.OKBLUE + "Ver-"+install_version[i] +"  -> "+  bcolors.ENDC+"|"+  str(cont) + "|"+ automargen(23, "Ver-"+ str(cont) +"|   ###")+ "  ###"
                cont = cont + 1
    print "#"*35

def mostrar_menu():    
    global cont
    global restart  
    global msg
    global msg_salida 
    global config_json
    config_json = cargar_config_json()     
    cont = 1    

    os.system("clear")
    comprobar_version_php_funcionando()
    apache_status()
    menu_modulos_php()
    menu_versiones_php()   
  
   
    print "#"*35
    option = raw_input("###   "+bcolors.HEADER + "[m]=SubMenu | [q]=Salir"+bcolors.ENDC +"   ###\n"+"#"*35+"\nOpcion ->        ")   
      
    option = str(option)

    
    if option == "m":                     
        sub_menu()
    
    if option == "q":                     
        sys.exit()

    if option == "y":
        reiniciar_apache()
        mostrar_menu() 
                       
    if option == "1":  
        listar_modulos_php()    
    
    if option == "2":
        cambiar_version_php("3")  

    if option == "3":
        cambiar_version_php("4")    

    if option == "4":
        cambiar_version_php("5")

    if option == "5":
        cambiar_version_php("6")          
    
    else:
        mostrar_menu()
       

    if (option == "NULL"):
        print "null"
 
    escribir_log_local("MENU","Cargado Menu Principal")

def sub_menu():
    global msg
    global msg_salida
    global config_json 
    escribir_log_local("MENU","Cargado Sub Menu")   

    while(True):
        os.system("clear")
        apache_status()
        print "#"*35
        print "### "+ bcolors.BOLD   +"         INSTALAR" +  bcolors.ENDC +"           ###"
        print "#"*35
        
        for sub_menu in config_json['submenu']:     
            if sub_menu["visible"] == True:      
                #print str(sub_menu["group"])           
                print "### " + bcolors.OKBLUE  + sub_menu['name'] +  bcolors.ENDC + automargen(20, "### "+ sub_menu['name'])   + "  -> |"+  str(sub_menu['id']) + "|" + automargen(6, str(sub_menu['id']) + '|') +"###"
        
        if msg:   
            mostrar_mensaje(msg, type="")
        else:            
            mostrar_mensaje(msg_salida, type="")


        print "#"*35
        sub_option = raw_input("###   "+bcolors.HEADER + "[m]=SubMenu | [q]=Salir"+bcolors.ENDC +"   ###\n"+"#"*35+"\nOpcion ->        ")
        
        for opt in config_json['submenu']: 
                                        
            if str(opt["id"]) == str(sub_option):               
                action =  str(opt["action"])
                
                try:
                    if opt["type"] == "function":
                        escribir_log_local("EXEC", str(action))                    
                        #os.system(action) 
                        msg_salida =  subprocess.check_output(action, shell=True)
                        if msg_salida == "":
                            msg = str(opt["msg_ok"])                                                  
                    
                    if opt["type"] == "command":
                        escribir_log_local("EXEC ", str(action))                      
                        os.system(action)
                        msg_salida = eval(action) 
                        if msg_salida == "":
                            msg = str(opt["msg_ok"])                           

                except:
                    eval(action) 
                    #msg_salida = eval(action) 
 







if (len(sys.argv) > 1):
    param1 = sys.argv[1]
    if param1:
        if param1=="56":
            menu_versiones_php()
            comprobar_version_php_funcionando()
            time.sleep(1)
            cambiar_version_php(1)
            escribir_log_local("PARAM","Instalacion php5.6")
            exit()

        if param1=="70":
            menu_versiones_php()
            comprobar_version_php_funcionando()
            time.sleep(1)
            cambiar_version_php(2)
            exit()

        if param1=="72":
            menu_versiones_php()
            comprobar_version_php_funcionando()
            time.sleep(1)
            cambiar_version_php(3)
            exit()

        if param1=="73":
            menu_versiones_php()
            comprobar_version_php_funcionando()
            time.sleep(1)
            cambiar_version_php(4)
            exit()

        if param1=="y":
            reiniciar_apache()
            print "Apache reiniciado."
            time.sleep(1)            
            exit()

        if param1=="install":
            instalar_phpv()
            print "\n1- phpv se ha instaldo en la carpeta '~/3_Script/phpv/'\n2- Se ha creado un alias en '~/.bashrc'"
            print "3- Puedes acceder con phpv desde cualquier carpeta del sistema\n"
            time.sleep(1)            
            exit()

        if param1=="update":
            os.system("wget -O ~/3_Script/config.json   https://github.com/ReosCli/phpv/raw/master/config.json")
            os.system("wget -O ~/3_Script/phpv.py   https://github.com/ReosCli/phpv/raw/master/phpv.py")
            print "\n1- phpv se ha actualizado"           
            time.sleep(1)            
            exit()
       
else:
    # Iniciamos programa si no hay parametros
    mostrar_menu()



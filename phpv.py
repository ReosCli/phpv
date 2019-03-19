#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import time
import datetime
import json

class bcolors:
    HEADER      = '\033[95m'
    OKBLUE      = '\033[94m'
    OKGREEN     = '\033[92m'
    WARNING     = '\033[93m'
    FAIL        = '\033[91m'
    ENDC        = '\033[0m'
    BOLD        = '\033[1m'
    UNDERLINE   = '\033[4m'
 
cont            = 1
versionActual   = ""
indicePHP       = {}
index_module    = {}
mods_available  = {}
mods_enabled    = {}
restart         = False        
num_registro    = 0

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

def reiniciar_apache():
    os.system("sudo service apache2 restart")
    escribir_log_local("FUNCTION","reiniciar_apache()")
    restart = False

def leer_apache_conf():
    os.system("cat /etc/apache2/apache2.conf | grep -v '#' ")

def crear_path_phpv():
    os.system("echo 'alias phpv=\"cd ~/3_Script && python phpv.py\"'")

def cargar_config_json():
    with open('config.json') as file:
        config_json = json.load(file)
        return config_json        
        #for submenu in data['submenu']:
        #   print submenu["name"]

def mostrar_mensaje(result, msg=""):
    if msg:
        print msg
   
def comprobar_version_php_funcionando():
    global versionActual
    out = subprocess.check_output("php -v", shell=True)
    versionActual = out[4:7]
    escribir_log_local("   ACTION","comprobar_version_php_funcionando = php"+str(versionActual))
    return versionActual

def set_version_php(ver):
    #version = "5.6"   
    global indicePHP
    global versionActual  
    global restart 
    ver = int(ver) 
    version = indicePHP[ver]
    try:
        escribir_log_local("FUNCTION","set_version_php("+str(ver)+")")
        subprocess.check_output("sudo a2dismod php"+str(versionActual), shell=True)
        print  bcolors.OKGREEN +"OK -> " + bcolors.ENDC +"Desactivando modulo PHP " + str(versionActual)     
        time.sleep(1)
        escribir_log_local("  ACCTION","Desactivando modulo PHP "+str(versionActual))
    
        subprocess.check_output("sudo a2enmod php"+version, shell=True)
        print bcolors.OKGREEN +"OK -> " +  bcolors.ENDC +"Activando modulo PHP " + version
        time.sleep(1)   
        escribir_log_local("  ACCTION","Activando modulo PHP "+str(version))
        reiniciar_apache() 
        print bcolors.OKGREEN +"OK -> " +  bcolors.ENDC +"Reiniciando Apache "
        time.sleep(1)

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
   
    elif (mod == "y"):
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
    if(restart):    
        print "#¡¡¡     "+ bcolors.FAIL   +"Restart Apache (y)" +  bcolors.ENDC +"    !!!!"
    
    else:        
        print "#---         "+ bcolors.OKGREEN +"Apache OK" +  bcolors.ENDC +"         ---#"

def menu_informacion_sistema():
    escribir_log_local("   MODULE","Cargado menu_informacion_sistema")
    global versionActual      
    print "###################################"
    print "#############"+ bcolors.OKGREEN +"  PHP  " +  bcolors.ENDC +"###############"
    print "#############  "+ bcolors.OKGREEN +versionActual+  bcolors.ENDC +"  ###############"
    print "###################################"

def menu_reinicio():
    escribir_log_local("   MODULE","Cargado menu_reinicio")
    global cont   
    print "#"*35  
    print "###          "+ bcolors.WARNING +" RESTART "+  bcolors.ENDC +"          ###"
    print "###"+ bcolors.OKBLUE + " Apache    -> "+  bcolors.ENDC+bcolors.FAIL + str(cont)+bcolors.ENDC +"              ###"
    cont = int(cont) + 1    
    print "###"+ bcolors.OKBLUE + " PHP       -> "+  bcolors.ENDC+bcolors.FAIL + str(cont)+bcolors.ENDC +"              ###"
    cont = int(cont) + 1   
    print "###"+ bcolors.OKBLUE + " MYSQL     -> "+  bcolors.ENDC+bcolors.FAIL + str(cont)+bcolors.ENDC +"              ###"
    cont = int(cont) + 1   
    print "#"*35

def menu_log(): 
    escribir_log_local("   MODULE","Cargado menu_log")
    global cont
    print "#"*35
    print "###       "+ bcolors.WARNING +" APACHE LOG   "+  bcolors.ENDC +"        ###"
    print "###"+ bcolors.OKBLUE +" Error    -> "+  bcolors.ENDC +"|"+str(cont)+"|             ###"
    cont = int(cont) + 1 
    print "###"+ bcolors.OKBLUE +" Access   -> "+  bcolors.ENDC +"|"+str(cont)+"|             ###"
    cont = int(cont) + 1 
    print "###"+ bcolors.OKBLUE +" Hosts    -> "+  bcolors.ENDC +"|"+str(cont)+"|             ###"
    print "#"*35

def menu_modulos_php():
    escribir_log_local("   MODULE","Cargado menu_modulos_php")
    global cont
    cont = int(cont) + 1  
    print "#"*35
    print "###           "+ bcolors.WARNING +"PHP MODS  "+  bcolors.ENDC +"        ###"
    print "###"+ bcolors.OKBLUE +" Options ->  "+  bcolors.ENDC +"|"+str(cont)+"|             ###"
    cont = int(cont) + 1     
    print "#"*35

def automargen(pos, texto):
    #part1 = "### "+ sub_menu['name']
    part1 = texto
    len_part1 = len(part1)
    part2 = pos - len_part1
    espacios =  " "*part2
    #print "_____________________________________________"+ str(part2)
    return espacios  

def menu_version_php():    
    escribir_log_local("   MODULE","Cargado menu_version_php")
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
                print "### " + bcolors.OKBLUE + "Ver-"+install_version[i] +"  ->"+  bcolors.ENDC+"|"+  str(cont) + "|"+ automargen(24, "Ver-"+ str(cont) +"|   ###")+ "  ###"
                cont = cont + 1
    print "#"*35

def mostrar_menu():
    escribir_log_local("MENU","Cargado Menu Principal")
    global cont
    cont = 1    
    os.system("clear")
    comprobar_version_php_funcionando()
    menu_informacion_sistema()
    menu_reinicio()
    menu_log()
    menu_modulos_php()
    menu_version_php()
    apache_status()
    mostrar_mensaje("True")
    cargar_opciones_menu()
    escribir_log_local("MENU","Entrando en Menu")
  
def cargar_opciones_menu():   
    global restart    
    print "#"*35
    option = raw_input("###    "+bcolors.HEADER + "(0=Menu - 00=subMenu)"+bcolors.ENDC +"    ###\n"+"#"*35+"\nOpcion ->        ")   
      
    option = str(option)

    if option == "a":
       sub_menu()    
    
    if option == "m":                     
        sub_menu()

    if option == "y":
        reiniciar_apache()
        mostrar_menu()        
    
    if option == "00":                     
        sub_menu()

    if option == "0":                
        os.system("clear")  
        mostrar_menu()
                    
    if option == "1":        
        reiniciar_apache()      
        restart = False
        mostrar_menu()

    if option == "2":
        print 2

    if option == "3":
        print 3

    if option == "4":      
        print bcolors.OKBLUE + "------ APACHE ERROR LOG ------"+bcolors.ENDC
        os.system("tail -f /var/log/apache2/error.log")         

    if option == "5":
        print bcolors.OKBLUE + "------ APACHE ACCESS LOG ------"+bcolors.ENDC     
        os.system("tail -f /var/log/apache2/access.log") 

    if option == "6":               
        print bcolors.OKBLUE + "------      HOSTS        ------"+bcolors.ENDC     
        print bcolors.OKBLUE + "------     ctrl + c      ------"+bcolors.ENDC 
        cat_hosts        = subprocess.check_output("cat /etc/hosts", shell=True)
        mostrar_mensaje("True", cat_hosts)
                    
    
    if option == "7":  
        listar_modulos_php()    
    
    if option == "8":
        set_version_php("8")  

    if option == "9":
        set_version_php("9")    

    if option == "10":
        set_version_php("10")

    if option == "11":
        set_version_php("11")          
    
    else:
        #mostrar_menu()
        cargar_opciones_menu()

    if (option == "NULL"):
        print "null"
    
    print option


def sub_menu():
    config_json = cargar_config_json()
    escribir_log_local("MENU","Entrando en Sub Menu")
    while(1==1):
        os.system("clear") 
        print "#"*35
        print "###          "+ bcolors.BOLD   +"SUB-MENU" +  bcolors.ENDC +"           ###"
        print "#"*35
        print "#"*35
        print "### "+ bcolors.OKBLUE   +"         INSTALAR" +  bcolors.ENDC +"           ###"
        print "#"*35
        
        for sub_menu in config_json['submenu']:     
            if sub_menu["visible"] == True:              
                print "### "+ bcolors.OKBLUE   + sub_menu['name'] +  bcolors.ENDC +    automargen(25, "### "+ sub_menu['name'])   +"-> "+ bcolors.OKBLUE +  str(sub_menu['id']) +  bcolors.ENDC +"   ###"      
    
        print "#"*35
        sub_option = raw_input("###        "+bcolors.OKBLUE + "(SUB_OPTION)"+bcolors.ENDC +"         ###\n"+"#"*35+"\nOpcion ->     ")
        
        for opt in config_json['submenu']:                                 
            if str(opt["id"]) == str(sub_option):               
                action =  str(opt["action"])
                if opt["type"] == "command":
                    escribir_log_local("ACTION", str(action))
                    os.system(action)                                     
                else:
                    escribir_log_local("ACTION", str(action))      
                    exec(action)    


def inicio():
    os.system("clear")
    mostrar_menu()
    cargar_opciones_menu()



#Ejecutamos inico
inicio()


# escribir_local_log()
# leer_local_log()
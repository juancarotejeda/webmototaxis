
def check_parada(cur,parada):
    cur.execute(f"SELECT balance_banco FROM tabla_index WHERE nombre = '{parada}' ")
    check=cur.fetchall()
    for valor in check:
        if valor[0] > 1000.00:
            return True
        else: 
            return False
    
def listado_paradas(cur):
    cur.execute("SELECT nombre FROM tabla_index")  
    db_paradas=cur.fetchall()     
    return db_paradas

def info_parada(cur,parada):
    cur.execute(f"SELECT codigo,nombre,direccion,municipio,provincia,zona,cuota,pago,banco,num_cuenta FROM  tabla_index  WHERE nombre='{parada}'" )
    infos=cur.fetchall()     
    return infos

def info_cabecera(cur,parada):
    cur.execute(f"SELECT cuota, pago FROM tabla_index WHERE nombre = '{parada}'")
    resp=cur.fetchall()
    for repueta in resp:
      cuota=repueta[0]  
      pago=repueta[1]
          
    cur.execute(f'SELECT nombre FROM {parada}')
    seleccion=cur.fetchall()
    cant=len(seleccion)
       
    presidente = []       
    cur.execute(f"SELECT nombre FROM {parada}  WHERE funcion = 'Presidente'")   
    press=cur.fetchone()
    for pres in press:   
        presidente=pres 

    veedor = []
    cur.execute(f"SELECT nombre FROM {parada}  WHERE funcion = 'Veedor'")   
    presd=cur.fetchone()
    for prex in presd:
       veedor=prex    
    return cuota,pago,cant,presidente,veedor               
     
def lista_miembros(cur,parada):
    listas=[]
    cur.execute(f"SELECT codigo,nombre,cedula,telefono,funcion  FROM {parada}")
    miembros=cur.fetchall()
    for miembro in miembros:     
        listas+=miembro    
    lista=dividir_lista(listas,5)    
    return lista
    
def diario_general(cur,parada):
    prestamos=[]
    ingresos=[]
    gastos=[]
    aporte=[]
    pendiente=[]
    abonos=[]
    balance_bancario=[]
    cur.execute(f"SELECT  prestamos, ingresos, gastos, aporte, pendiente, abonos, balance_banco FROM tabla_index WHERE nombre='{parada}' " )  
    consult=cur.fetchall()
    for valor in consult:
      prestamos=valor[0]
      ingresos=valor[1]
      gastos=valor[2]
      aporte=valor[3]
      pendiente=valor[4]
      abonos=valor[5]
      balance_bancario=valor[6]
    balance=(aporte + ingresos + abonos )-(gastos+prestamos)
    data=(balance,prestamos,ingresos,gastos,aporte,pendiente,abonos,balance_bancario)   
    return data

def dividir_lista(lista,lon) : 
    return [lista[n:n+lon] for n in range(0,len(lista),lon)]     


def aportacion(cur,parada):           
    cur.execute(f"SELECT codigo, nombre, cedula, telefono, funcion FROM {parada}")
    data=cur.fetchall()
    return data
  
def verif_p(cur,parada,cedula,password):
    cur.execute(f"SELECT * FROM tabla_index WHERE  adm_password = '{password}'")
    result=cur.fetchall()
    if result:
      cur.execute(f"SELECT * FROM {parada} WHERE  cedula = '{cedula}'")                                       
      accounts =cur.fetchall()
      if accounts != []:
         return True
      else:
         return False 
    else: 
        return False

def crear_p(cur,parada,string,valor_cuota,hoy):
       suma_no=[];suma_si=[]
       cur.execute(f'CREATE TABLE IF NOT EXISTS {parada}_cuota( item VARCHAR(50)  NULL, fecha VARCHAR(50)  NULL, estado VARCHAR(50)  NULL, nombre VARCHAR(50)  NULL, cedula VARCHAR(50)  NULL)')
       for data in string:
          cur.execute(f"INSERT INTO {parada}_cuota(item, fecha, estado, nombre, cedula) VALUES('{data[0]}', '{hoy}',  '{data[1]}', '{data[2]}', '{data[3]}')")    
       cur.execute(f"SELECT COUNT(estado) FROM {parada}_cuota WHERE estado = 'no_pago' ")   
       suma=cur.fetchall()
       for num in suma:
           suma_no=num[0]       
       cur.execute(f"SELECT COUNT(estado) FROM {parada}_cuota WHERE estado = 'pago' ")   
       sumas=cur.fetchall() 
       for numb in sumas:
           suma_si=numb[0]        
       n_aporte=int(suma_si) * float(valor_cuota)
       n_pendiente=int(suma_no) * float(valor_cuota)
       cur.execute(f"UPDATE tabla_index SET aporte={n_aporte}, pendiente={n_pendiente} WHERE nombre='{parada}'")
       return
   
def prestamo_aport(cur,parada):
    vgral=[]
    cur.execute(f"SELECT nombre FROM {parada}")
    list_nomb=cur.fetchall()
    for nombre in list_nomb:
        cur.execute(f"SELECT COUNT(estado) FROM {parada}_cuota WHERE estado = 'pago' and nombre='{nombre[0]}'") 
        var_x = cur.fetchall()
        for var_p in var_x:
              var1=var_p[0]
        cur.execute(f"SELECT COUNT(estado) FROM {parada}_cuota WHERE estado = 'no_pago' and nombre='{nombre[0]}'")
        var_z = cur.fetchall()
        for var_n in var_z:
              var2=var_n[0]   
        sub_t=var1+var2 
        if sub_t != 0 :    
         avg=round((var1/sub_t)*100,2)
        else: 
         avg=0          
        vgral+=(nombre[0],var1,var2,sub_t,avg) 
    list_1=dividir_lista(vgral,5)                    
    return list_1

def verif_dig(cur,nombre,password):
    cur.execute(f"SELECT username FROM digitadores WHERE password='{password}'")
    valor=[]
    result=cur.fetchall()
    if result != []:
       for valores in result:
           valor=valores[0]
       if valor == nombre:
          return True
       else:
         return False 
    else: 
        return False
 
def estado_bancario(cur,parada,fecha,nom_banco,t_cuenta,n_cuenta,balance_c): 
    cur.execute(f"CREATE TABLE IF NOT EXISTS {parada}_banco( fecha VARCHAR(50)  NULL, banco VARCHAR(50) NULL, tipo_cuenta VARCHAR(50) NULL,  numero_cuenta VARCHAR(50) NULL, balance DECIMAl(10,2) unsigned DEFAULT 0)")                                                                                                                                
    cur.execute(f"INSERT INTO {parada}_banco(fecha, banco, tipo_cuenta, numero_cuenta, balance) VALUES('{fecha}', '{nom_banco}', '{t_cuenta}', '{n_cuenta}', {balance_c})")
    cur.execute(f"UPDATE tabla_index SET balance_banco={balance_c} WHERE nombre='{parada}'")
    return  

def report_gastos(cur,parada,fecha,descripcion_gastos,cantidad_gastos):
     n_gastos=[] 
     cur.execute(f"CREATE TABLE IF NOT EXISTS {parada}_gastos( fecha VARCHAR(50)  NULL,descripcion_gastos VARCHAR(50) NULL, cantidad_gastos DECIMAl(10,2) unsigned DEFAULT 0)")                                                                                                                         
     cur.execute(f"INSERT INTO {parada}_gastos(fecha, descripcion_gastos, cantidad_gastos) VALUES('{fecha}', '{descripcion_gastos}', {cantidad_gastos})")
     cur.execute(f"SELECT SUM(cantidad_gastos) FROM  {parada}_gastos ")
     suma=cur.fetchall() 
     for total in suma:
        n_gastos=total[0]   
     cur.execute(f"UPDATE tabla_index SET gastos={n_gastos} WHERE nombre='{parada}'")
     return
 
def report_ingresos(cur,parada,fecha,descripcion_ingreso,cantidad_ingreso):
       n_ingresos=[]    
       cur.execute(f"CREATE TABLE IF NOT EXISTS {parada}_ingresos( fecha VARCHAR(50)  NULL, descripcion_ingresos VARCHAR(50)  NULL, cantidad_ingresos DECIMAl(10,2) unsigned DEFAULT 0)" )                                                                                                                               
       cur.execute(f"INSERT INTO {parada}_ingresos(fecha, descripcion_ingresos, cantidad_ingresos) VALUES('{fecha}', '{descripcion_ingreso}', { cantidad_ingreso})")       
       cur.execute(f"SELECT SUM(cantidad_ingresos) FROM  {parada}_ingresos ")
       suma=cur.fetchall() 
       for total in suma:  
         n_ingresos=total[0]        
       cur.execute(f"UPDATE tabla_index SET ingresos={n_ingresos}  WHERE nombre='{parada}'")
       return
 
def report_prestamo(cur,parada,fecha,prestamo,monto): 
       n_prestamos=[]     
       cur.execute(f"CREATE TABLE IF NOT EXISTS {parada}_prestamos( fecha VARCHAR(50)  NULL, prestamo_a VARCHAR(50)  NULL, monto_prestamo DECIMAl(10,2) unsigned DEFAULT 0 )")                                                                                                                                 
       cur.execute(f"INSERT INTO {parada}_prestamos(fecha, prestamo_a, monto_prestamo) VALUES('{fecha}',  '{prestamo}', {monto})")            
       cur.execute(f"SELECT SUM(monto_prestamo) FROM  {parada}_prestamos ")
       suma=cur.fetchall 
       for total in suma:
          n_prestamos=total[0]          
       cur.execute(f"UPDATE tabla_index SET prestamos={n_prestamos}  WHERE nombre='{parada}'")
       return     
       
def report_abono(cur,parada,fecha,abono_a,cantidad_a):
    balance_prestamos=[]
    n_abonos=[]
    prestamo=[] 
    abono_persona=[]
    cur.execute(f"CREATE TABLE IF NOT EXISTS {parada}_abonos( fecha VARCHAR(50)  NULL,  abono_a VARCHAR(50)  NULL, monto_abono DECIMAl(10,2) unsigned DEFAULT 0, balance_prestamo DECIMAl(10,2) unsigned DEFAULT 0)" )                                                                                                                            
    cur.execute(f"INSERT INTO {parada}_abonos(fecha, abono_a, monto_abono) VALUES('{fecha}', '{abono_a}', {cantidad_a})")         
    cur.execute(f"SELECT SUM(monto_abono) FROM  {parada}_abonos ")
    suma=cur.fetchall() 
    for total in suma: 
         n_abonos=total[0]
    cur.execute(f"SELECT SUM(monto_abono) FROM  {parada}_abonos WHERE abono_a='{abono_a}' ")
    suma=cur.fetchall() 
    for total in suma: 
        abono_persona=total[0]
    cur.execute(f"SELECT monto_prestamo FROM  {parada}_prestamos WHERE prestamo_a = '{abono_a}' ")
    prestado=cur.fetchall()
    for pres in prestado:
        prestamo=pres[0]           
    if prestamo==[] or prestamo== 0:
      cur.execute(f"UPDATE {parada}_abonos SET balance_prestamo = 0.0 ")
      return
    else:       
      balance_prestamos=float(prestamo) - float(abono_persona)                
      cur.execute(f"UPDATE {parada}_abonos SET balance_prestamo = {balance_prestamos} WHERE abono_a = '{abono_a}' AND fecha = '{fecha}' ")
      cur.execute(f"UPDATE tabla_index SET abonos={n_abonos} WHERE nombre='{parada}'")
      return 
  
def actualizar_pp(cur,parada,direccion,municipio,provincia,zona,cuota,pago,banco,num_cuenta):
     cur.execute(f"UPDATE tabla_index SET direccion='{direccion}',municipio='{municipio}',provincia='{provincia}',zona='{zona}',cuota='{cuota}',pago='{pago}',banco='{banco}', num_cuenta='{num_cuenta}' WHERE nombre='{parada}'")
     return 
 
def generar_pp(cur,nombre,direccion,municipio,provincia,zona,cuota,pago,banco,num_cuenta): 
    cur.execute(f"CREATE TABLE IF NOT EXISTS {nombre} (id INT NOT NULL AUTO_INCREMENT,codigo VARCHAR(50) NULL, nombre VARCHAR(150)  NULL, cedula VARCHAR(50)  NULL, telefono VARCHAR(50)  NULL, funcion VARCHAR(50)  NULL, cuota DECIMAL(10,2) unsigned DEFAULT 0)")
    cur.execute(f"INSERT INTO tabla_index(nombre,direccion,municipio,provincia,zona,cuota,pago,banco,num_cuenta) VALUES('{nombre}','{direccion}','{municipio}','{provincia}','{zona}','{cuota}','{pago}','{banco}','{num_cuenta}') ")
    return

def nombres_miembro(cur,parada):
        listado=[]
        cur.execute(f"SELECT nombre FROM {parada} ")
        nombres=cur.fetchall()
        for nombre in nombres:
            listado += nombre
        return listado 


def dat_miembros(cur,parada,miembro):
    cur.execute(f"SELECT nombre,cedula,telefono,funcion FROM {parada} WHERE nombre='{miembro}'")
    listado=cur.fetchall()
    return listado

def insertar_Asociado(cur,parada,nombre,cedula,telefono,funcion):
     cur.execute(f"INSERT INTO {parada}( nombre,cedula,telefono,funcion) VALUES('{nombre}','{cedula}','{telefono}','{funcion}')")
     return 

def actualizar_asoc(cur,parada,nombre,cedula,telefono,funcion,id):
     cur.execute(F"UPDATE {parada} SET nombre='{nombre}',cedula='{cedula}',telefono='{telefono}',funcion='{funcion}' WHERE nombre ='{id}' ") 
     return
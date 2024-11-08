

import mysql.connector,funciones,os
from flask import Flask, render_template,flash, request, session, redirect, url_for
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key=os.getenv("APP_KEY")

DB_HOST =os.getenv('DB_HOST')
DB_USERNAME =os.getenv("DB_USERNAME")
DB_PASSWORD =os.getenv("DB_PASSWORD")
DB_NAME =os.getenv("DB_NAME")

# Connect to the database
connection =mysql.connector.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_NAME,
    autocommit=True
)

@app.route("/")
def login():   
    cur = connection.cursor() 
    resultado=funciones.listado_paradas(cur)
    paradas=[]
    for paradax in resultado:
       paradas+=paradax  
    cur.close()                   
    return render_template('login.html',n_paradas=paradas)

@app.route("/new_data", methods=["GUET","POST"])
def new_data(): 
   msg = ''
   if request.method == 'POST':  
    global parada,cedula,password     
    parada = request.form['parada']
    cedula = request.form['cedula']
    password = request.form['clave']    
    cur = connection.cursor()    
    estacion=funciones.check_parada(cur,parada)
    if estacion == True:   
        cur.execute(f"SELECT cedula FROM {parada} WHERE cedula='{cedula}'")
        result = cur.fetchall()
        if result != []:   
         cur.execute(f"SELECT password FROM tabla_index  WHERE nombre ='{parada}'" )
         ident=cur.fetchall() 
         for idx in ident:   
            if password == idx[0]:                                             
                fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")
                informacion=funciones.info_parada(cur,parada)
                cabecera=funciones.info_cabecera(cur,parada)
                miembros=funciones.lista_miembros(cur,parada)
                diario=funciones.diario_general(cur,parada)
                cuotas_hist=funciones.prestamo_aport(cur,parada)
                cur.close()
                return render_template('info.html',informacion=informacion,cabecera=cabecera,fecha=fecha,miembros=miembros,diario=diario,cuotas_hist=cuotas_hist) 
            else:
                msg = 'Incorrecta contraseña de la parada!'          
                flash(msg)           
                return redirect(url_for('login')) 
        else:
          msg = 'cedula Incorrecta para esta parada!'
          flash(msg)           
          return redirect(url_for('login'))    
    else:
      msg = 'Esta parada esta inoperante!' 
      flash(msg)          
      return redirect(url_for('login'))
    
    
@app.route('/administrador') 
def administrador():
    return render_template('login_a.html',parada=parada)

@app.route('/digitadores') 
def digitadores():
    return render_template('login_dir.html')

@app.route('/contacto') 
def contacto():
    return render_template('contactos.html')

@app.route('/login_a', methods =[ 'POST'])
def login_a():
    msg = ''
    account=[]
    if 'parada' in request.form and 'cedula' in request.form and 'password' in request.form:
        parada = request.form['parada']
        cedula = request.form['cedula']
        password = request.form['password']
        cur = connection.cursor()
        account=funciones.verif_p(cur,parada,cedula,password) 
        if account ==True:
            fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")  
            informacion=funciones.info_parada(cur,parada) 
            miembros=funciones.lista_miembros(cur,parada)
            datos=funciones.aportacion(cur,parada) 
            cabecera=funciones.info_cabecera(cur,parada)
            cur.close()
            return render_template('administrador.html',informacion=informacion,miembros=miembros,datos=datos,cabecera=cabecera,fecha=fecha,parada=parada)
        else:
            msg = 'Incorrecto nombre de usuario / password !'           
            return render_template('login_a.html',msg=msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('data_confirmacion'))

@app.route("/data_cuotas", methods=["GET","POST"])
def data_cuotas():
    my_list=[]
    if request.method == 'POST': 
        parada=request.form['parada']     
        hoy = request.form['time']
        cant=request.form['numero']
        valor_cuota=request.form['valor']
        for i in range(int(cant)): 
            my_list +=(request.form.getlist('item')[i],
                    request.form.getlist('select')[i],
                    request.form.getlist('nombre')[i],
                    request.form.getlist('cedula')[i])  
        string=funciones.dividir_lista(my_list,4) 
        cur = connection.cursor()
        funciones.crear_p(cur,parada,string,valor_cuota,hoy)  
        cur.close()                                                        
        return redirect(url_for('data_confirmacion'))   
 
@app.route("/data_confirmacion", methods=["GET","POST"])
def data_confirmacion():
         cur = connection.cursor()
         informacion=funciones.info_parada(cur,parada) 
         miembros=funciones.lista_miembros(cur,parada)
         diario=funciones.diario_general(cur,parada)
         datos=funciones.aportacion(cur,parada) 
         hoy = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")
         cabecera=funciones.info_cabecera(cur,parada)
         cuotas_hist=funciones.prestamo_aport(cur,parada)
         cur.close()  
         return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha={hoy},cuotas_hist=cuotas_hist)

@app.route("/data_bancos",methods=["GET","POST"])
def data_bancos(): 
    if request.method == 'POST':
       fecha = request.form['time']
       parada=request.form['parada'] 
       nom_banco = request.form['nom_banco'] 
       t_cuenta = request.form['t_cuenta']
       n_cuenta = request.form['n_cuenta']
       balance_c = request.form['balance']
       cur = connection.cursor() 
       funciones.estado_bancario(cur,parada,fecha,nom_banco,t_cuenta,n_cuenta,balance_c)      
       cur.close()   
       return redirect(url_for('data_confirmacion'))   

@app.route("/data_gastos",methods=["GET","POST"])
def data_gastos():
    if request.method == 'POST':
       fecha=request.form['time']
       descripcion_gastos = request.form['descripcion_g'] 
       cantidad_gastos = request.form['cantidad_g']
       cur = connection.cursor() 
       funciones.report_gastos(cur,parada,fecha,descripcion_gastos,cantidad_gastos)          
       cur.close()
       return redirect(url_for('data_confirmacion')) 

@app.route("/data_ingresos",methods=["GET","POST"])
def data_ingresos(): 
    if request.method == 'POST':
       fecha=request.form['time']
       descripcion_ingreso = request.form['descripcion_i'] 
       cantidad_ingreso = request.form['cantidad_i'] 
       cur = connection.cursor() 
       funciones.report_ingresos(cur,parada,fecha,descripcion_ingreso,cantidad_ingreso)          
       cur.close()  
       return redirect(url_for('data_confirmacion'))        
              
@app.route("/data_prestamos",methods=["GET","POST"])
def data_prestamos(): 
    if request.method == 'POST':            
       fecha=request.form['time']              
       prestamo = request.form['descripcion_p'] 
       monto = request.form['cantidad_p']
       cur = connection.cursor() 
       funciones.report_prestamo(cur,parada,fecha,prestamo,monto)          
       cur.close()
       return redirect(url_for('data_confirmacion')) 

@app.route("/data_abonos",methods=["GET","POST"])
def data_abonos(): 
    if request.method == 'POST':               
       fecha=request.form['time']       
       abono_a = request.form['descripcion_a'] 
       cantidad_a = request.form['cantidad_a']  
       cur = connection.cursor() 
       funciones.report_abono(cur,parada,fecha,abono_a,cantidad_a)          
       cur.close()
       return redirect(url_for('data_confirmacion')) 


@app.route('/crear_nueva_p',methods=['GUEST','POST']) 
def crear_nueva_p():
    if request.method == 'POST':
       cur = connection.cursor()
       parada=request.form['nombre']
       direccion=request.form['direccion']
       municipio=request.form['municipio']
       provincia=request.form['provincia']
       zona=request.form['zona']
       cuota=request.form['cuota']
       pago=request.form['pago']
       banco=request.form['banco']
       num_cuenta=request.form['cuenta']
       funciones.generar_pp(cur,parada,direccion,municipio,provincia,zona,cuota,pago,banco,num_cuenta)
       return render_template('digitadores.html')



                                                   
@app.route('/edit_parada',methods=['GUEST','POST']) 
def edit_parada(): 
    if request.method == 'POST':               
       parada=request.form['e-parada']
       cur = connection.cursor()
       data=funciones.info_parada(cur,parada)
       cur.close()      
       return render_template('digitadores.html',data=data,parada=parada) 
 
@app.route('/actualizar_p',methods=['GUEST','POST']) 
def actualizar_p():
    if request.method == 'POST':
       cur = connection.cursor()
       parada=request.form['parada']
       direccion=request.form['direccion']
       municipio=request.form['municipio']
       provincia=request.form['provincia']
       zona=request.form['zona']
       cuota=request.form['cuota']
       pago=request.form['pago']
       banco=request.form['banco']
       num_cuenta=request.form['num_cuenta']
       funciones.actualizar_pp(cur,parada,direccion,municipio,provincia,zona,cuota,pago,banco,num_cuenta)   
       cur.close()
       return render_template('digitadores.html')                      
                           
@app.route('/n_miembro',methods=['GUEST','POST']) 
def n_miembro(): 
    if request.method == 'POST':
       cur = connection.cursor()
       parada=request.form['E-parada']
       nombre=request.form['nombre']
       cedula=request.form['cedula']
       telefono=request.form['telefono']
       funcion=request.form['funcion']
       funciones.insertar_Asociado(cur,parada,nombre,cedula,telefono,funcion)
       cur.close()
       return render_template('digitadores.html')

@app.route('/select_p',methods=['GUEST','POST']) 
def select_p(): 
    if request.method == 'POST':
       cur = connection.cursor()
       parada=request.form['parada']
       list_miembros=funciones.nombres_miembro(cur,parada)
       cur.close()
       return render_template('digitadores.html',parada=parada,list_miembros=list_miembros)
                           
                           
@app.route('/select_miembro',methods=['GUEST','POST']) 
def select_miembro(): 
    if request.method == 'POST':
       cur = connection.cursor()
       parada=request.form['parada']
       miembro=request.form['miembros']
       datos_miembro=funciones.dat_miembros(cur,parada,miembro)
    return render_template('digitadores.html',datos_miembro=datos_miembro,parada=parada ) 
 
@app.route('/redit_miembro',methods=['GUEST','POST']) 
def redit_miembro(): 
    if request.method == 'POST':
       cur = connection.cursor()
       parada=request.form['parada']
       id=request.form['id']
       nombre=request.form['nombre']
       cedula=request.form['cedula']
       telefono=request.form['telefono']
       funcion=request.form['funcion']
       funciones.actualizar_asoc(cur,parada,nombre,cedula,telefono,funcion,id)
       cur.close()
       return render_template('digitadores.html')


if __name__ == "__main__":
    app.run(debug=True,port=5600,host='0.0.0.0')




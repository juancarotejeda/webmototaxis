

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
    return render_template('login.html',paradas=paradas)

@app.route("/verificador", methods=["GUET","POST"])
def verificador(): 
   msg = ''
   global parada 
   if request.method == 'POST':        
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
                fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H")
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

@app.route('/chofer') 
def chofer():
    cur = connection.cursor()
    fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H")
    informacion=funciones.info_parada(cur,parada) 
    miembros=funciones.lista_miembros(cur,parada)
    diario=funciones.diario_general(cur,parada)
    datos=funciones.aportacion(cur,parada) 
    cabecera=funciones.info_cabecera(cur,parada)
    cuotas_hist=funciones.prestamo_aport(cur,parada)
    cur.close()  
    return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha=fecha,cuotas_hist=cuotas_hist)   

@app.route('/administrador') 
def administrador():
    return render_template('login_a.html',parada=parada)

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
            fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H")  
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
	return render_template('login.html',paradas=parada)

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
        informacion=funciones.info_parada(cur,parada) 
        miembros=funciones.lista_miembros(cur,parada)
        diario=funciones.diario_general(cur,parada)
        datos=funciones.aportacion(cur,parada) 
        cabecera=funciones.info_cabecera(cur,parada)
        cuotas_hist=funciones.prestamo_aport(cur,parada)
        cur.close()  
        return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha={hoy},cuotas_hist=cuotas_hist)   
    
@app.route("/data_bancos",methods=["GET","POST"])
def data_bancos(): 
    if request.method == 'POST':
       parada=request.form['parada'] 
       fecha = request.form['time']
       banco = request.form['banco'] 
       cuenta = request.form['cuenta'] 
       operacion = request.form['operacion']
       balance = request.form['balance']
       cur = connection.cursor() 
       funciones.estado_bancario(cur,parada,fecha,banco,cuenta,operacion,balance)      
       informacion=funciones.info_parada(cur,parada) 
       miembros=funciones.lista_miembros(cur,parada)
       diario=funciones.diario_general(cur,parada)
       datos=funciones.aportacion(cur,parada) 
       cabecera=funciones.info_cabecera(cur,parada)
       cuotas_hist=funciones.prestamo_aport(cur,parada)
       cur.close()  
       return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha=fecha,cuotas_hist=cuotas_hist)  

@app.route("/data_gastos",methods=["GET","POST"])
def data_gastos():
    if request.method == 'POST':
       fecha=request.form['time']
       descripcion_gastos = request.form['descripcion_g'] 
       cantidad_gastos = request.form['cantidad_g']
       cur = connection.cursor() 
       funciones.report_gastos(cur,parada,fecha,descripcion_gastos,cantidad_gastos)          
       informacion=funciones.info_parada(cur,parada) 
       miembros=funciones.lista_miembros(cur,parada)
       diario=funciones.diario_general(cur,parada)
       datos=funciones.aportacion(cur,parada) 
       cabecera=funciones.info_cabecera(cur,parada)
       cuotas_hist=funciones.prestamo_aport(cur,parada)
       cur.close()  
       return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha=fecha,cuotas_hist=cuotas_hist)

@app.route("/data_ingresos",methods=["GET","POST"])
def data_ingresos(): 
    if request.method == 'POST':
       fecha=request.form['time']
       descripcion_ingreso = request.form['descripcion_i'] 
       cantidad_ingreso = request.form['cantidad_i'] 
       cur = connection.cursor() 
       funciones.report_ingresos(cur,parada,fecha,descripcion_ingreso,cantidad_ingreso)          
       informacion=funciones.info_parada(cur,parada) 
       miembros=funciones.lista_miembros(cur,parada)
       diario=funciones.diario_general(cur,parada)
       datos=funciones.aportacion(cur,parada) 
       cabecera=funciones.info_cabecera(cur,parada)
       cuotas_hist=funciones.prestamo_aport(cur,parada)
       cur.close()  
       return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha=fecha,cuotas_hist=cuotas_hist)       


              
@app.route("/data_prestamos",methods=["GET","POST"])
def data_prestamos(): 
    if request.method == 'POST':            
       fecha=request.form['time']              
       prestamo = request.form['descripcion_p'] 
       monto = request.form['cantidad_p']
       cur = connection.cursor() 
       funciones.report_prestamo(cur,parada,fecha,prestamo,monto)          
       informacion=funciones.info_parada(cur,parada) 
       miembros=funciones.lista_miembros(cur,parada)
       diario=funciones.diario_general(cur,parada)
       datos=funciones.aportacion(cur,parada) 
       cabecera=funciones.info_cabecera(cur,parada)
       cuotas_hist=funciones.prestamo_aport(cur,parada)
       cur.close()  
       return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha=fecha,cuotas_hist=cuotas_hist)

@app.route("/data_abonos",methods=["GET","POST"])
def data_abonos(): 
    if request.method == 'POST':               
       fecha=request.form['time']       
       abono_a = request.form['descripcion_a'] 
       cantidad_a = request.form['cantidad_a']  
       cur = connection.cursor() 
       funciones.report_abono(cur,parada,fecha,abono_a,cantidad_a)          
       informacion=funciones.info_parada(cur,parada) 
       miembros=funciones.lista_miembros(cur,parada)
       diario=funciones.diario_general(cur,parada)
       datos=funciones.aportacion(cur,parada)
       cabecera=funciones.info_cabecera(cur,parada)
       cuotas_hist=funciones.prestamo_aport(cur,parada)
       cur.close()  
       return render_template("info.html",informacion=informacion,miembros=miembros,diario=diario,datos=datos,cabecera=cabecera,fecha=fecha,cuotas_hist=cuotas_hist)


if __name__ == "__main__":
    app.run(debug=True,port=5700,host='0.0.0.0')




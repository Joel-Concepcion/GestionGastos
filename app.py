from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import traceback
import MySQLdb.cursors 

from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'bzriokq8w1ja8kilnhbl-mysql.services.clever-cloud.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'uvf565cymdupuorh'
app.config['MYSQL_PASSWORD'] = 'xmm8z4rlb5etk2jbTIEK'
app.config['MYSQL_DB'] = 'bzriokq8w1ja8kilnhbl'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Página principal
@app.route('/')
def inicio():
    return render_template('index.html')

# Página de login y registro
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'nombre' in request.form:
            nombre = request.form['nombre']
            email = request.form['email']
            password = pbkdf2_sha256.hash (request.form['password'])

            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO usuario (email, password, id_rol) VALUES (%s, %s, %s)", (email, password, 2))
            mysql.connection.commit()
            cursor.close()
            return render_template('index.html', error='Usuario registrado exitosamente')
        
        elif 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            
            #cursor = mysql.connection.cursor()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            if user and pbkdf2_sha256.verify(password, user['password']):
                session['logueado'] = True
                session['id'] = user['id']
                session['id_rol'] = user['id_rol']
                session['email'] = user['email']

                if user['id_rol'] == 1:
                    return redirect(url_for('admin', email=user['email']))
                elif user['id_rol'] == 2:
                    return redirect(url_for('vistaUsuario'))
            else:
                return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html', error='Mensaje')

@app.route('/acercaDe')
def acercaDe():
    return render_template('acercaDe.html')

@app.route('/admin')
def admin():
    #ide de usuario
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #contador de usuarios
    cursor.execute("SELECT COUNT(*) AS total FROM usuario")
    resultado = cursor.fetchone()
    contadorUsuarios = resultado['total'] if resultado else 0
   

    #contador de gastos
    cursor.execute("SELECT COUNT(*) AS total FROM gastos WHERE id_usuario = %s", (id_usuario,))
    resultado_gastos = cursor.fetchone()
    contadorGastos = resultado_gastos['total'] if resultado_gastos else 0

    cursor.close()

    return render_template('admin.html', contadorUsuarios=contadorUsuarios, contadorGastos=contadorGastos)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/listaUsuario', methods=['GET', 'POST'])
def listaUsuario():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO usuario (email, password, id_rol) VALUES (%s, %s, %s)", (email, password, 2))
            mysql.connection.commit()
            cursor.close()

            flash('Usuario registrado exitosamente', 'success')
        except Exception as e:
            flash('Error al registrar el usuario', 'error')
            
        return redirect(url_for('listaUsuario'))

    # Obtener lista de usuarios
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, password FROM usuario ORDER BY id DESC")
    listaUsuario = cursor.fetchall()
    contadorUsuarios = len(listaUsuario) #contador de usuarios
    cursor.close()

    return render_template('listaUsuario.html', usuarios=listaUsuario, contadorUsuarios=contadorUsuarios)


#metodo POST para actualizar usuario
@app.route('/updateUsuario', methods=['POST'])
def updateUsuario():
    try:
        id = request.form['id']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE usuario SET email = %s, password = %s WHERE id = %s", (email, password, id))
        mysql.connection.commit()
        cursor.close()

       # Devolver respuesta JSON para fetch()
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })

    except Exception as e:
        print("Error al actualizar:", e)

        # Devolver error en formato JSON
        return jsonify({
            'success': False,
            'message': 'Error interno al actualizar'
        })


   # return render_template('listaUsuario.html', usuarios=listaUsuario)


#metodo Get para optener al usuario 
@app.route('/getUsuario/<int:id>', methods=['GET'])
def getUsuario(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, email, password FROM usuario WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario is not None:
            return jsonify({
                'success': True,
                'usuario': {
                    'id': usuario[0],
                    'email': usuario[1],
                    'password': usuario[2]
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    except Exception as e:
        import traceback
        print("Error en /getUsuario:", e)
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

#metod para eliminar Usuario
@app.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})

@app.route('/listaProductos', methods=['GET', 'POST'])
def listaProductos():
    if request.method == 'POST':
        id_gasto = request.form.get('id_gasto') 
        tipo = request.form['tipo']
        categoria = request.form['categoria']
        monto = request.form['monto']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        id_usuario = session.get('id')

        # funcion para actualización de un registro en este caps de la tabla gastos 
        cursor = mysql.connection.cursor()
        if id_gasto: 
            cursor.execute("""
                UPDATE gastos SET tipo = %s, categoria = %s, monto = %s, fecha = %s, descripcion = %s
                WHERE id_gasto = %s AND id_usuario = %s
            """, (tipo, categoria, monto, fecha, descripcion, id_gasto, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('listaProductos'))
        else:  
            cursor.execute("""
                INSERT INTO gastos (tipo, categoria, monto, fecha, descripcion, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, categoria, monto, fecha, descripcion, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('listaProductos'))


    # Mostrar los gastos de la tabla
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gastos WHERE id_usuario = %s ORDER BY fecha DESC", (id_usuario,))
    gastos = cursor.fetchall()
    cursor.close()
    return render_template('listaProductos.html', gastos=gastos)

# Página de control de gastos
@app.route('/control', methods=['GET', 'POST'])
def control():
    if request.method == 'POST':
        id_gasto = request.form.get('id_gasto') 
        tipo = request.form['tipo']
        categoria = request.form['categoria']
        monto = request.form['monto']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        id_usuario = session.get('id')

        # funcion para actualización de un registro en este caps de la tabla gastos 
        cursor = mysql.connection.cursor()
        if id_gasto: 
            cursor.execute("""
                UPDATE gastos SET tipo = %s, categoria = %s, monto = %s, fecha = %s, descripcion = %s
                WHERE id_gasto = %s AND id_usuario = %s
            """, (tipo, categoria, monto, fecha, descripcion, id_gasto, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Gasto actualizado exitosamente'})
        else:  
            cursor.execute("""
                INSERT INTO gastos (tipo, categoria, monto, fecha, descripcion, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, categoria, monto, fecha, descripcion, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Gasto registrado exitosamente'})

    # Mostrar los gastos de la tabla
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gastos WHERE id_usuario = %s ORDER BY fecha DESC", (id_usuario,))
    gastos = cursor.fetchall()
    cursor.close()
    return render_template('control.html', gastos=gastos)

# cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Ruta para obtener un gasto y que este listo para ser editado
@app.route('/get_gasto/<int:id_gasto>', methods=['GET'])
def get_gasto(id_gasto):
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gastos WHERE id_gasto = %s AND id_usuario = %s", (id_gasto, id_usuario))
    gasto = cursor.fetchone()
    cursor.close()
    if gasto:
        return jsonify({'success': True, 'gasto': gasto})
    else:
        return jsonify({'success': False, 'message': 'Gasto no encontrado'})


# Ruta para eliminar un gasto
@app.route('/delete/<int:id_gasto>', methods=['DELETE'])  # Cambiado a id_gasto
def delete_gasto(id_gasto):
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gastos WHERE id_gasto = %s AND id_usuario = %s", (id_gasto, id_usuario))
    gasto = cursor.fetchone()
    if not gasto:
        return jsonify({'success': False, 'message': 'Gasto no encontrado'}), 404
    
    try:
        cursor.execute("DELETE FROM gastos WHERE id_gasto = %s AND id_usuario = %s", (id_gasto, id_usuario))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Gasto eliminado exitosamente'}), 200
    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        print(f"Error al eliminar: {str(e)}")  # Agrega logging para depuración
        return jsonify({'success': False, 'message': f'Error al eliminar: {str(e)}'}), 500
    
@app.route('/vistaUsuario')
def vistaUsuario():
    return render_template('vistaUsuario.html')

@app.route('/control1')
def control1():
    if request.method == 'POST':
        id_gasto = request.form.get('id_gasto') 
        tipo = request.form['tipo']
        categoria = request.form['categoria']
        monto = request.form['monto']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        id_usuario = session.get('id')

        # funcion para actualización de un registro en este caps de la tabla gastos 
        cursor = mysql.connection.cursor()
        if id_gasto: 
            cursor.execute("""
                UPDATE gastos SET tipo = %s, categoria = %s, monto = %s, fecha = %s, descripcion = %s
                WHERE id_gasto = %s AND id_usuario = %s
            """, (tipo, categoria, monto, fecha, descripcion, id_gasto, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Gasto actualizado exitosamente'})
        else:  
            cursor.execute("""
                INSERT INTO gastos (tipo, categoria, monto, fecha, descripcion, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, categoria, monto, fecha, descripcion, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Gasto registrado exitosamente'})

    # Mostrar los gastos de la tabla
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gastos WHERE id_usuario = %s ORDER BY fecha DESC", (id_usuario,))
    gastos = cursor.fetchall()
    cursor.close()
    return render_template('control1.html', gastos=gastos)
    #return render_template('control1.html')
@app.route('/listaProductos1', methods=['GET', 'POST'])
def listaProductos1():
    if request.method == 'POST':
        id_gasto = request.form.get('id_gasto') 
        tipo = request.form['tipo']
        categoria = request.form['categoria']
        monto = request.form['monto']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        id_usuario = session.get('id')

        cursor = mysql.connection.cursor()
        if id_gasto: 
            cursor.execute("""
                UPDATE gastos SET tipo = %s, categoria = %s, monto = %s, fecha = %s, descripcion = %s
                WHERE id_gasto = %s AND id_usuario = %s
            """, (tipo, categoria, monto, fecha, descripcion, id_gasto, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('listaProductos1'))
        else:  
            cursor.execute("""
                INSERT INTO gastos (tipo, categoria, monto, fecha, descripcion, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, categoria, monto, fecha, descripcion, id_usuario))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('listaProductos1'))

    # Mostrar los gastos de la tabla
    id_usuario = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM gastos WHERE id_usuario = %s ORDER BY fecha DESC", (id_usuario,))
    gastos = cursor.fetchall()
    cursor.close()
    return render_template('listaProductos1.html', gastos=gastos)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
from flask import Flask, render_template, request, redirect, url_for,session
from flask_wtf.csrf import CSRFProtect
import os
from databases import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')


app = Flask(__name__, template_folder = template_dir)
app.config['SECRET_KEY'] = 'KoKoa'
csrf = CSRFProtect(app)


@app.route('/')
def index():
    return render_template('auth/login.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Verificar las credenciales en la base de datos
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reguser WHERE name = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        # Credenciales correctas, establecer sesión
        session['user_id'] = user['id']
        return redirect(url_for('admin'))
    else:
        # Credenciales incorrectas, mostrar mensaje de error
        error_message = "Usuario o contraseña incorrectos. Inténtalo de nuevo."
        return render_template('auth/login.html', error_message=error_message)



@app.route('/admin')
def admin():
    if 'user_id' in session:
        cursor = db.database.cursor()
        cursor.execute("SELECT * FROM users")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        return render_template('index.html', data=insertObject)
    else:
        error_message = "No has iniciado Sesion. Inténtalo de nuevo."
        return render_template('auth/login.html', error_message=error_message)

# Ruta para guardar usuarios en la base de datos
@app.route('/user', methods=['POST'])
def addUser():
    if 'user_id' in session:
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']

        if username and name and password:
            cursor = db.database.cursor(dictionary=True)
            sql = "INSERT INTO users (username, name, password) VALUES (%s, %s, %s)"
            data = (username, name, password)
            cursor.execute(sql, data)
            db.database.commit()
        return redirect(url_for('admin'))
    else:
        error_message = "No has iniciado Sesión. Inténtalo de nuevo."
        return render_template('auth/login.html', error_message=error_message)


# Ruta para eliminar usuarios de la base de datos
@app.route('/delete/<string:id>')
def delete(id):
    if 'user_id' in session:
        cursor = db.database.cursor()
        sql = "DELETE FROM users WHERE id=%s"
        data = (id,)
        cursor.execute(sql, data)
        db.database.commit()
        return redirect(url_for('admin'))
    else:
        error_message = "No has iniciado Sesión. Inténtalo de nuevo."
        return render_template('auth/login.html', error_message=error_message)


# Ruta para editar usuarios en la base de datos
@app.route('/edit/<string:id>', methods=['POST'])
def edit(id):
    if 'user_id' in session:
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']

        if username and name and password:
            cursor = db.database.cursor()
            sql = "UPDATE users SET username = %s, name = %s, password = %s WHERE id = %s"
            data = (username, name, password, id)
            cursor.execute(sql, data)
            db.database.commit()
        return redirect(url_for('admin'))
    else:
        error_message = "No has iniciado Sesión. Inténtalo de nuevo."
        return render_template('auth/login.html', error_message=error_message)


@app.route('/logout')
def logout():
    # Eliminar 'user_id' de la sesión
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
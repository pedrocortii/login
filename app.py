from flask import Flask, render_template, request, redirect, url_for, session

import pyodbc

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'  # Cambiá esto por algo más seguro

# Configurar conexión a SQL Server
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=miprimeradb;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clientes WHERE Email = ? AND Contraseña = ?", email, password)
    user = cursor.fetchone()
    conn.close()
    if user:
        session['user_id'] = user.IdCliente
        session['email'] = user.Email
        return redirect(url_for('dashboard'))
    return 'Login inválido. Intenta de nuevo.'


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clientes WHERE IdCliente = ?", session['user_id'])
    user = cursor.fetchone()
    conn.close()
    return render_template('dashboard.html', user=user)


@app.route('/editar/<int:idcliente>', methods=['GET', 'POST'])
def editar(idcliente):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nuevo_correo = request.form['email']
        nueva_clave = request.form['password']
        cursor.execute("UPDATE Clientes SET Email = ?, Contraseña = ? WHERE IdCliente = ?", nuevo_correo, nueva_clave, idcliente)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    cursor.execute("SELECT * FROM Clientes WHERE IdCliente = ?", idcliente)
    user = cursor.fetchone()
    conn.close()
    return render_template('editar.html', user=user)

@app.route('/eliminar/<int:idcliente>')
def eliminar(idcliente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Clientes WHERE IdCliente = ?", idcliente)
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Conexión a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el correo ya está registrado
        cursor.execute("SELECT * FROM Clientes WHERE Email = ?", email)
        existing_user = cursor.fetchone()

        if existing_user:
            return 'El correo ya está registrado. Intenta con otro.'

        # Insertar el nuevo usuario
        cursor.execute("INSERT INTO Clientes (Email, Contraseña) VALUES (?, ?)", email, password)
        conn.commit()
        conn.close()

        return redirect(url_for('index'))  # Redirige a la página de login

    return render_template('registro.html')

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    # Se asume que el usuario ya ha iniciado sesión y está en la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener la ID del usuario logueado (puedes implementarlo de otra manera según tu lógica)
    user_id = 1  # Supongamos que el ID del usuario es 1. Esto debe cambiarse a algo dinámico.

    if request.method == 'POST':
        nuevo_correo = request.form['email']
        nueva_clave = request.form['password']
        
        # Actualizar la información
        cursor.execute("UPDATE Clientes SET Email = ?, Contraseña = ? WHERE IdCliente = ?", nuevo_correo, nueva_clave, user_id)
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    cursor.execute("SELECT * FROM Clientes WHERE IdCliente = ?", user_id)
    user = cursor.fetchone()
    conn.close()

    return render_template('editar_perfil.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Genera una clave secreta segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Define el modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_apellido = db.Column(db.String(80), nullable=False)
    legajo = db.Column(db.String(80), unique=True, nullable=False)

# Crear las tablas de la base de datos si no existen
with app.app_context():
    db.create_all()

# Ruta para la página de administración
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        legajo = request.form.get('legajo')

        if not nombre or not apellido or not legajo:
            flash('Faltan campos en el formulario', 'error')
            return redirect(url_for('admin'))

        # Verificar si el legajo ya está registrado
        if User.query.filter_by(legajo=legajo).first():
            flash('El legajo ya está registrado', 'error')
        else:
            try:
                # Crear un nuevo usuario y agregarlo a la base de datos
                new_user = User(nombre=nombre ,apellido=apellido,legajo=legajo)
                db.session.add(new_user)
                db.session.commit()
                flash('Usuario registrado con éxito', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Ocurrió un error: {str(e)}', 'error')
    
    users = User.query.all()
    return render_template('admin.html', users=users)

# Ruta para el login de administrador
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_password = request.form.get('password')
        if admin_password == '12345':  # Cambia esto a una contraseña segura
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Contraseña incorrecta', 'error')

    return render_template('admin_login.html')

# Ruta para el login de usuario
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        user = User.query.filter_by(legajo=legajo).first()

        if user:
            session['user_logged_in'] = True
            session['user_legajo'] = legajo
            return redirect(url_for('user_dashboard'))
        else:
            flash('Número de legajo incorrecto', 'error')

    return render_template('user_login.html')

# Ruta para el dashboard del usuario
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_logged_in' not in session:
        return redirect(url_for('user_login'))
    return f'Bienvenido, usuario con legajo {session["user_legajo"]}!'

# Para cerrar sesión de usuario
@app.route('/user_logout')
def user_logout():
    session.pop('user_logged_in', None)
    session.pop('user_legajo', None)
    flash('Sesión cerrada con éxito', 'success')
    return redirect(url_for('user_login'))

# Para cerrar sesión de administrador
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Sesión cerrada con éxito', 'success')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)

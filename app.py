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

# Define el modelo de Código QR
class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)

# Crear las tablas de la base de datos si no existen
with app.app_context():
    db.create_all()

# Función para agregar códigos QR a la base de datos
def populate_qr_codes():
    for i in range(1, 12):  # Generar 11 códigos QR
        qr_code = f'QR_CODE_{i}'
        if not QRCode.query.filter_by(code=qr_code).first():
            db.session.add(QRCode(code=qr_code))
    db.session.commit()

# Ejecuta esta función una sola vez para poblar la base de datos con los códigos QR
#with app.app_context():
 #   populate_qr_codes()

# Ruta principal redirige a /user_login
@app.route('/')
def index():
    return redirect(url_for('user_login'))

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
                nombre_apellido = f"{nombre} {apellido}"
                new_user = User(nombre_apellido=nombre_apellido, legajo=legajo)
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
    return render_template('user_dashboard.html')

# Ruta para escanear códigos QR
@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    if 'user_logged_in' not in session:
        return redirect(url_for('user_login'))

    qr_code = request.form.get('qr_code')

@app.route('/view_qrcodes')
def view_qrcodes():
    # Obtener la lista de archivos de QR en el directorio
    qr_codes = os.listdir('static/qr_codes/')
    qr_codes = [f'qr_codes/{qr_code}' for qr_code in qr_codes]  # Ruta accesible en HTML
    return render_template('view_qrcodes.html', qr_codes=qr_codes)

    # Verificar si el código QR es válido
    if QRCode.query.filter_by(code=qr_code).first():
        # Aquí puedes agregar la lógica para registrar el QR escaneado
        # Por ejemplo, podrías registrar la fecha y hora del escaneo, o asociar el QR con el usuario
        flash('Código QR registrado con éxito', 'success')
    else:
        flash('Código QR no válido', 'error')

    return redirect(url_for('user_dashboard'))

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
    app.run(debug=True, port=5000)  # Puedes cambiar el puerto aquí si es necesario

from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

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

# Define el modelo de Escaneo de Código QR
class QRScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('scans', lazy=True))

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
        nombre_apellido = request.form.get('nombre_apellido')
        legajo = request.form.get('legajo')

        if not nombre_apellido or not legajo:
            flash('Faltan campos en el formulario', 'error')
            return redirect(url_for('admin'))

        if User.query.filter_by(legajo=legajo).first():
            flash('El legajo ya está registrado', 'error')
        else:
            try:
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
            flash('Usuario no registrado', 'error')

    return render_template('user_login.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_logged_in' not in session:
        return redirect(url_for('user_login'))

    legajo = session.get('user_legajo')
    user = User.query.filter_by(legajo=legajo).first()

    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('user_login'))

    scanned_qrs = QRScan.query.filter_by(user_id=user.id).all()

    return render_template('user_dashboard.html', user=user, scanned_qrs=scanned_qrs)

@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    if 'user_logged_in' not in session:
        return redirect(url_for('user_login'))

    qr_code = request.form.get('qr_code')
    user_legajo = session.get('user_legajo')
    user = User.query.filter_by(legajo=user_legajo).first()

    if QRCode.query.filter_by(code=qr_code).first() and user:
        qr_scan = QRScan(user_id=user.id, code=qr_code)
        db.session.add(qr_scan)
        db.session.commit()
        flash('Código QR registrado con éxito', 'success')
    else:
        flash('Código QR no válido', 'error')

    return redirect(url_for('user_dashboard'))

# Ruta para ver códigos QR
@app.route('/view_qrcodes')
def view_qrcodes():
    qr_codes = os.listdir('static/qr_codes/')
    qr_codes = [f'qr_codes/{qr_code}' for qr_code in qr_codes]
    return render_template('view_qrcodes.html', qr_codes=qr_codes)

# Ruta para editar un usuario
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        nombre_apellido = request.form.get('nombre_apellido')
        legajo = request.form.get('legajo')

        if not nombre_apellido or not legajo:
            flash('Faltan campos en el formulario', 'error')
        else:
            user.nombre_apellido = nombre_apellido
            user.legajo = legajo

            try:
                db.session.commit()
                flash('Usuario actualizado con éxito', 'success')
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ocurrió un error: {str(e)}', 'error')

    return render_template('edit_user.html', user=user)

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
    app.run(debug=True, port=5000)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

def inspect_db():
    with app.app_context():
        # Listar tablas en la base de datos
        print("Tablas en la base de datos:")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"- {table}")

        # Consultar datos en la tabla 'user'
        print("\nDatos en la tabla 'user':")
        users = db.session.execute(text('SELECT * FROM user')).fetchall()
        for user in users:
            print(user)

        # Consultar datos en la tabla 'QRCode'
        print("\nDatos en la tabla 'QRCode':")
        qrcodes = db.session.execute(text('SELECT * FROM qr_code')).fetchall()
        for qr in qrcodes:
            print(qr)

if __name__ == '__main__':
    inspect_db()

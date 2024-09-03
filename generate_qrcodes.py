import qrcode
import os

# Directorio donde se guardarán los códigos QR
output_dir = 'static/qr_codes/'
# Crear el directorio si no existe
os.makedirs(output_dir, exist_ok=True)

# Lista de nombres personalizados para los códigos QR
names = [
    'RRHH',
    'ROBOTICA',
    'FINANZAS',
    'CALIDAD',
    'PROCESOS',
    'LOGISTICA',
    'INGENIERIA',
    'IT',
    'COMPRAS',
    'CORTE',
    'ADMINISTRACION'
]

# Generar códigos QR
for name in names:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(name)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Define el nombre del archivo
    img_file = os.path.join(output_dir, f'{name}.png')
    
    # Guarda la imagen del QR
    img.save(img_file)
    
    # Imprime el mensaje de confirmación
    #print(f'Código QR para "{name}" guardado como {img_file}')

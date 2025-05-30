from flask import request, redirect, url_for, flash
from flask import Blueprint, render_template, abort
from .uploadImage import save_image
from datetime import datetime
from app.db import get_db 
import pymysql
from flask import current_app
import os
import tensorflow as tf
from PIL import Image
import numpy as np

main_bp = Blueprint('main', __name__)

# ----------------------
# Autenticación básica
# ----------------------

from werkzeug.security import check_password_hash
from flask import session

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        error = None

        if not email or not password:
            error = 'Por favor ingresa tu correo y contraseña.'
        else:
            db = get_db()
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute('SELECT * FROM mod_user WHERE email=%s', (email,))
                user = cursor.fetchone()
                if user is None or not check_password_hash(user['password_hash'], password):
                    error = 'Correo o contraseña incorrectos.'

        if error:
            flash(error)
            return render_template('login.html')
        # Login correcto: guardar datos en sesión
        session.clear()
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['name'] = user['name']
        session['lastname'] = user['lastname']
        flash('Bienvenido, {}!'.format(user['name']))
        return redirect(url_for('main.index'))  # Cambia 'main.index' por la ruta principal de tu app

    return render_template('login.html')

from werkzeug.security import generate_password_hash

@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.')
    return redirect(url_for('main.login'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('first_name', '').strip()
        lastname = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        errors = []

        # Validaciones básicas
        if not name or not lastname or not email or not username or not password:
            errors.append('Todos los campos son obligatorios.')
        if password != password2:
            errors.append('Las contraseñas no coinciden.')
        if len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')

        db = get_db()
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Verificar unicidad de email y username
            cursor.execute('SELECT user_id FROM mod_user WHERE email=%s OR username=%s', (email, username))
            if cursor.fetchone():
                errors.append('El correo o usuario ya está registrado.')

        if errors:
            for err in errors:
                flash(err)
            return render_template('register.html')

        # Guardar usuario
        password_hash = generate_password_hash(password)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO mod_user (name, lastname, username, email, password_hash, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, lastname, username, email, password_hash, created_at))
            db.commit()
        flash('Usuario registrado correctamente. Ahora puedes iniciar sesión.')
        return redirect(url_for('main.login'))

    return render_template('register.html')

# Cargar modelo de radiografía dental
modelo_radiografia = tf.keras.models.load_model('modelo_radiografia.h5')

def es_radiografia_dental(img_path):
    try:
        img = Image.open(img_path).convert('RGB').resize((224, 224))
        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)
        pred = modelo_radiografia.predict(arr)[0][0]
        return pred > 0.5  # True si es radiografía dental
    except Exception:
        # No es una imagen válida
        return False

@main_bp.route('/image/<int:image_id>')
def image_detail(image_id):
    connection = get_db()
    paciente_id = None
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM mod_images WHERE mod_img_id = %s", (image_id,))
            image = cursor.fetchone()
            # Buscar paciente asociado a la imagen
            cursor.execute("SELECT paciente_id FROM paciente_imagen WHERE imagen_id = %s LIMIT 1", (image_id,))
            rel = cursor.fetchone()
            if rel:
                paciente_id = rel['paciente_id']
    finally:
        connection.close()
    if image is None:
        abort(404)
    return render_template('image_detail.html', image=image, paciente_id=paciente_id)

@main_bp.route('/')
def index():
    return render_template('index.html')  # Busca en app/templates/index.html

@main_bp.route('/paciente/form', methods=['GET'])
def patient_form():
    # Formulario vacío para registrar paciente nuevo
    return render_template('patient_form.html', paciente=None)

@main_bp.route('/paciente/form/<int:paciente_id>', methods=['GET'])
def patient_form_id(paciente_id):
    connection = get_db()
    paciente = None
    revision = None
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM mod_paciente WHERE mod_pac_id = %s', (paciente_id,))
            paciente = cursor.fetchone()
            if paciente and paciente.get('mod_pac_form_diag'):
                cursor.execute('SELECT * FROM mod_paciente_revision WHERE mod_pac_rev_id = %s', (paciente['mod_pac_form_diag'],))
                revision = cursor.fetchone()
    finally:
        connection.close()
    return render_template('patient_form.html', paciente=paciente, revision=revision)


@main_bp.route('/paciente/form/<int:image_id>', methods=['GET'])
def patient_form_image(image_id):
    connection = get_db()
    paciente = None
    revision = None
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Buscar paciente relacionado a la imagen (si existe)
            cursor.execute('''
                SELECT p.* FROM mod_paciente p
                JOIN paciente_imagen pi ON p.mod_pac_id = pi.paciente_id
                WHERE pi.imagen_id = %s
                LIMIT 1
            ''', (image_id,))
            paciente = cursor.fetchone()
            # Si hay paciente y tiene revisión asociada, buscar la revisión
            if paciente and paciente.get('mod_pac_form_diag'):
                cursor.execute('SELECT * FROM mod_paciente_revision WHERE mod_pac_rev_id = %s', (paciente['mod_pac_form_diag'],))
                revision = cursor.fetchone()
    finally:
        connection.close()
    return render_template('patient_form.html', paciente=paciente, image_id=image_id, revision=revision)

@main_bp.route('/paciente/save', methods=['POST'])
def save_patient():
    mod_pac_ci = request.form.get('mod_pac_ci')
    mod_pac_nombre = request.form.get('mod_pac_nombre')
    mod_pac_apellido = request.form.get('mod_pac_apellido')
    mod_pac_fecha_nacimiento = request.form.get('mod_pac_fecha_nacimiento')
    mod_pac_telefono = request.form.get('mod_pac_telefono')
    mod_pac_direccion = request.form.get('mod_pac_direccion')
    mod_pac_email = request.form.get('mod_pac_email')
    mod_pac_form_diag = request.form.get('mod_pac_form_diag')
    mod_pac_observaciones = request.form.get('mod_pac_observaciones')
    image_id = request.form.get('image_id')

    connection = get_db()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Verifica si el paciente ya existe (por CI)
            cursor.execute("SELECT mod_pac_id FROM mod_paciente WHERE mod_pac_ci = %s", (mod_pac_ci,))
            result = cursor.fetchone()
            if result:
                paciente_id = result['mod_pac_id']
                cursor.execute('''
                    UPDATE mod_paciente SET
                        mod_pac_nombre=%s, mod_pac_apellido=%s, mod_pac_fecha_nacimiento=%s,
                        mod_pac_telefono=%s, mod_pac_direccion=%s, mod_pac_email=%s, mod_pac_form_diag=%s, mod_pac_observaciones=%s
                    WHERE mod_pac_id=%s
                ''', (mod_pac_nombre, mod_pac_apellido, mod_pac_fecha_nacimiento, mod_pac_telefono, mod_pac_direccion, mod_pac_email, mod_pac_form_diag, mod_pac_observaciones, paciente_id))
            else:
                cursor.execute('''
                    INSERT INTO mod_paciente (mod_pac_ci, mod_pac_nombre, mod_pac_apellido, mod_pac_fecha_nacimiento, mod_pac_telefono, mod_pac_direccion, mod_pac_email, mod_pac_form_diag, mod_pac_observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (mod_pac_ci, mod_pac_nombre, mod_pac_apellido, mod_pac_fecha_nacimiento, mod_pac_telefono, mod_pac_direccion, mod_pac_email, mod_pac_form_diag, mod_pac_observaciones))
                paciente_id = cursor.lastrowid
                # Relacionar usuario y paciente (solo si es nuevo)
                user_id = session.get('user_id')
                if user_id:
                    cursor.execute("SELECT user_paciente FROM mod_user_paciente WHERE user_id=%s AND paciente=%s", (user_id, paciente_id))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO mod_user_paciente (user_id, paciente) VALUES (%s, %s)", (user_id, paciente_id))

            # Relaciona el paciente con la imagen en la tabla intermedia
            if image_id:
                cursor.execute("SELECT id FROM paciente_imagen WHERE paciente_id=%s AND imagen_id=%s", (paciente_id, image_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO paciente_imagen (paciente_id, imagen_id) VALUES (%s, %s)", (paciente_id, image_id))
            connection.commit()
    finally:
        connection.close()

    flash('Datos del paciente guardados correctamente.')
    return redirect(url_for('main.patient_form_id', paciente_id=paciente_id))

@main_bp.route('/pacientes')
def patient_list():
    user_id = session.get('user_id')
    pacientes = []
    if not user_id:
        flash('Debes iniciar sesión para ver tus pacientes.')
        return redirect(url_for('main.login'))
    connection = get_db()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('''
                SELECT p.* FROM mod_paciente p
                JOIN mod_user_paciente up ON p.mod_pac_id = up.paciente
                WHERE up.user_id = %s
            ''', (user_id,))
            pacientes = cursor.fetchall()
    finally:
        connection.close()
    return render_template('patient_list.html', pacientes=pacientes)

# Eliminar paciente
@main_bp.route('/paciente/eliminar/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    connection = get_db()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Obtener el id del formulario de revisión
            cursor.execute("SELECT mod_pac_form_diag FROM mod_paciente WHERE mod_pac_id=%s", (patient_id,))
            result = cursor.fetchone()
            revision_id = result['mod_pac_form_diag'] if result and result['mod_pac_form_diag'] else None

            # 2. Borrar de paciente_imagen todos los registros con ese paciente_id
            cursor.execute("DELETE FROM paciente_imagen WHERE paciente_id=%s", (patient_id,))

            # 2.1. Borrar la relación usuario-paciente
            user_id = session.get('user_id')
            if user_id:
                cursor.execute("DELETE FROM mod_user_paciente WHERE user_id=%s AND paciente=%s", (user_id, patient_id))

            # 3. Borrar de mod_paciente el paciente
            cursor.execute("DELETE FROM mod_paciente WHERE mod_pac_id=%s", (patient_id,))

            # 4. Si existe, borrar de mod_paciente_revision el registro con el id del formulario de revisión
            if revision_id:
                cursor.execute("DELETE FROM mod_paciente_revision WHERE mod_pac_rev_id=%s", (revision_id,))

            connection.commit()
        flash('Paciente y registros asociados eliminados correctamente.')
    finally:
        connection.close()
    return redirect(url_for('main.patient_list'))

# Editar paciente

@main_bp.route('/paciente/editar_form/<int:paciente_id>', methods=['GET', 'POST'])
def edit_patient_form(paciente_id):
    connection = get_db()
    paciente = None
    revision = None
    if request.method == 'POST':
        # Datos de paciente
        mod_pac_ci = request.form.get('mod_pac_ci')
        mod_pac_nombre = request.form.get('mod_pac_nombre')
        mod_pac_apellido = request.form.get('mod_pac_apellido')
        mod_pac_fecha_nacimiento = request.form.get('mod_pac_fecha_nacimiento')
        mod_pac_telefono = request.form.get('mod_pac_telefono')
        mod_pac_direccion = request.form.get('mod_pac_direccion')
        mod_pac_email = request.form.get('mod_pac_email')
        mod_pac_observaciones = request.form.get('mod_pac_observaciones')
        # Datos de revisión
        mod_pac_rev_dolor_persistente = 1 if request.form.get('mod_pac_rev_dolor_persistente') else 0
        mod_pac_rev_sensibilidad_prolongada = 1 if request.form.get('mod_pac_rev_sensibilidad_prolongada') else 0
        mod_pac_rev_hinchazon = 1 if request.form.get('mod_pac_rev_hinchazon') else 0
        mod_pac_rev_fistula = 1 if request.form.get('mod_pac_rev_fistula') else 0
        mod_pac_rev_cambio_color = 1 if request.form.get('mod_pac_rev_cambio_color') else 0
        mod_pac_rev_dolor_percusion = 1 if request.form.get('mod_pac_rev_dolor_percusion') else 0
        mod_pac_rev_movilidad = 1 if request.form.get('mod_pac_rev_movilidad') else 0
        mod_pac_rev_caries_profunda = 1 if request.form.get('mod_pac_rev_caries_profunda') else 0
        mod_pac_rev_lesion_radiografica = 1 if request.form.get('mod_pac_rev_lesion_radiografica') else 0
        mod_pac_rev_observaciones = request.form.get('mod_pac_rev_observaciones')
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Actualizar paciente
                cursor.execute('''
                    UPDATE mod_paciente SET
                        mod_pac_ci=%s,
                        mod_pac_nombre=%s,
                        mod_pac_apellido=%s,
                        mod_pac_fecha_nacimiento=%s,
                        mod_pac_telefono=%s,
                        mod_pac_direccion=%s,
                        mod_pac_email=%s,
                        mod_pac_observaciones=%s
                    WHERE mod_pac_id=%s
                ''', (mod_pac_ci, mod_pac_nombre, mod_pac_apellido, mod_pac_fecha_nacimiento, mod_pac_telefono, mod_pac_direccion, mod_pac_email, mod_pac_observaciones, paciente_id))
                # Obtener id de revisión
                cursor.execute('SELECT mod_pac_form_diag FROM mod_paciente WHERE mod_pac_id=%s', (paciente_id,))
                result = cursor.fetchone()
                revision_id = result['mod_pac_form_diag'] if result and result['mod_pac_form_diag'] else None
                if revision_id:
                    cursor.execute('''
                        UPDATE mod_paciente_revision SET
                            mod_pac_rev_dolor_persistente=%s,
                            mod_pac_rev_sensibilidad_prolongada=%s,
                            mod_pac_rev_hinchazon=%s,
                            mod_pac_rev_fistula=%s,
                            mod_pac_rev_cambio_color=%s,
                            mod_pac_rev_dolor_percusion=%s,
                            mod_pac_rev_movilidad=%s,
                            mod_pac_rev_caries_profunda=%s,
                            mod_pac_rev_lesion_radiografica=%s,
                            mod_pac_rev_observaciones=%s
                        WHERE mod_pac_rev_id=%s
                    ''', (
                        mod_pac_rev_dolor_persistente, mod_pac_rev_sensibilidad_prolongada, mod_pac_rev_hinchazon,
                        mod_pac_rev_fistula, mod_pac_rev_cambio_color, mod_pac_rev_dolor_percusion, mod_pac_rev_movilidad,
                        mod_pac_rev_caries_profunda, mod_pac_rev_lesion_radiografica, mod_pac_rev_observaciones, revision_id
                    ))
                connection.commit()
            flash('Paciente y revisión actualizados correctamente.')
            return redirect(url_for('main.patient_list'))
        finally:
            connection.close()
    # Si GET, renderiza el formulario con datos actuales
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM mod_paciente WHERE mod_pac_id = %s', (paciente_id,))
            paciente = cursor.fetchone()
            if paciente and paciente.get('mod_pac_form_diag'):
                cursor.execute('SELECT * FROM mod_paciente_revision WHERE mod_pac_rev_id = %s', (paciente['mod_pac_form_diag'],))
                revision = cursor.fetchone()
    finally:
        connection.close()
    return render_template('patient_edit_form.html', paciente=paciente, revision=revision)

@main_bp.route('/paciente/editar/<int:paciente_id>', methods=['GET', 'POST'])
def edit_patient(paciente_id):
    connection = get_db()
    if request.method == 'POST':
        mod_pac_ci = request.form.get('mod_pac_ci')
        mod_pac_nombre = request.form.get('mod_pac_nombre')
        mod_pac_apellido = request.form.get('mod_pac_apellido')
        mod_pac_fecha_nacimiento = request.form.get('mod_pac_fecha_nacimiento')
        mod_pac_telefono = request.form.get('mod_pac_telefono')
        mod_pac_direccion = request.form.get('mod_pac_direccion')
        mod_pac_email = request.form.get('mod_pac_email')
        mod_pac_observaciones = request.form.get('mod_pac_observaciones')
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    UPDATE mod_paciente SET
                        mod_pac_ci=%s,
                        mod_pac_nombre=%s,
                        mod_pac_apellido=%s,
                        mod_pac_fecha_nacimiento=%s,
                        mod_pac_telefono=%s,
                        mod_pac_direccion=%s,
                        mod_pac_email=%s,
                        mod_pac_observaciones=%s
                    WHERE mod_pac_id=%s
                ''', (
                    mod_pac_ci, mod_pac_nombre, mod_pac_apellido, mod_pac_fecha_nacimiento,
                    mod_pac_telefono, mod_pac_direccion, mod_pac_email, mod_pac_observaciones, paciente_id
                ))
                connection.commit()
            flash('Paciente actualizado correctamente.')
            return redirect(url_for('main.patient_form_id', paciente_id=paciente_id))
        finally:
            connection.close()
    else:
        revision = None
        paciente = None
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Obtener datos de paciente
                cursor.execute('SELECT * FROM mod_paciente WHERE mod_pac_id=%s', (paciente_id,))
                paciente = cursor.fetchone()
                # Obtener datos de revisión si existe
                if paciente and paciente.get('mod_pac_form_diag'):
                    cursor.execute('SELECT * FROM mod_paciente_revision WHERE mod_pac_rev_id = %s', (paciente['mod_pac_form_diag'],))
                    revision = cursor.fetchone()
        finally:
            connection.close()
        if not paciente:
            flash('Paciente no encontrado.')
            return redirect(url_for('main.patient_list'))
        # Pasar ambos diccionarios al formulario
        return render_template('patient_form.html', paciente=paciente, revision=revision)

# Ver imágenes de un paciente

@main_bp.route('/ia_resultado/<int:image_id>/<int:paciente_id>')
def ia_caries_result(image_id, paciente_id):
    # Por ahora, mostramos una imagen de ejemplo resaltando caries
    highlighted_img_path = 'img/caries_demo.jpg'  # Cambia esto cuando tengas la imagen procesada
    return render_template(
        'ai_caries_result.html',
        highlighted_img_path=highlighted_img_path,
        paciente_id=paciente_id,
        image_id=image_id
    )

@main_bp.route('/paciente/<int:paciente_id>/imagenes')
def patient_images(paciente_id):
    connection = get_db()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Solo imágenes asociadas a ese paciente
            cursor.execute('''
                SELECT img.* FROM mod_images img
                JOIN paciente_imagen pi ON img.mod_img_id = pi.imagen_id
                WHERE pi.paciente_id = %s
            ''', (paciente_id,))
            images = cursor.fetchall()
    finally:
        connection.close()
    return render_template('images.html', images=images, paciente_id=paciente_id)


@main_bp.route('/uploadImage/<int:paciente_id>', methods=['GET'])
def uploadImage(paciente_id):
    return render_template('uploadImage.html', paciente_id=paciente_id)  # Busca en app/templates/uploadImage.html

@main_bp.route('/reportes')
def reportes():
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para ver los reportes.')
        return redirect(url_for('main.login'))
    connection = get_db()
    pacientes = []
    paciente_seleccionado = None
    imagen_principal = None
    paciente_id = request.args.get('paciente_id', type=int)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('''
                SELECT p.* FROM mod_paciente p
                JOIN mod_user_paciente up ON p.mod_pac_id = up.paciente
                WHERE up.user_id = %s
            ''', (user_id,))
            pacientes = cursor.fetchall()
            if paciente_id:
                cursor.execute('SELECT * FROM mod_paciente WHERE mod_pac_id = %s', (paciente_id,))
                paciente_seleccionado = cursor.fetchone()
                # Obtener la primera imagen asociada
                cursor.execute('''SELECT img.mod_img_path FROM mod_images img JOIN paciente_imagen pi ON img.mod_img_id = pi.imagen_id WHERE pi.paciente_id = %s LIMIT 1''', (paciente_id,))
                img = cursor.fetchone()
                if img:
                    imagen_principal = img['mod_img_path']
    finally:
        connection.close()
    return render_template('reportes.html', pacientes=pacientes, paciente_seleccionado=paciente_seleccionado, imagen_principal=imagen_principal)

# Vista previa HTML del reporte
@main_bp.route('/reportes/<int:paciente_id>')
def reporte_vista(paciente_id):
    connection = get_db()
    paciente = None
    revision = None
    imagen_principal = None
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM mod_paciente WHERE mod_pac_id = %s', (paciente_id,))
            paciente = cursor.fetchone()
            # Buscar datos de revisión si existen
            revision_id = paciente['mod_pac_form_diag'] if paciente else None
            if revision_id:
                cursor.execute('SELECT * FROM mod_paciente_revision WHERE mod_pac_rev_id = %s', (revision_id,))
                revision = cursor.fetchone()
            cursor.execute('''SELECT img.mod_img_path FROM mod_images img JOIN paciente_imagen pi ON img.mod_img_id = pi.imagen_id WHERE pi.paciente_id = %s LIMIT 1''', (paciente_id,))
            img = cursor.fetchone()
            if img:
                imagen_principal = img['mod_img_path']
    finally:
        connection.close()
    return render_template('reporte_vista.html', paciente=paciente, revision=revision, imagen_principal=imagen_principal)


# Descargar PDF del reporte
@main_bp.route('/reportes/<int:paciente_id>/descargar')
def reporte_pdf(paciente_id):
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from flask import send_file
    import io, os

    connection = get_db()
    paciente = None
    revision = None
    imagen_principal = None
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM mod_paciente WHERE mod_pac_id = %s', (paciente_id,))
            paciente = cursor.fetchone()
            # Traer también los datos de revisión
            revision_id = paciente['mod_pac_form_diag'] if paciente else None
            if revision_id:
                cursor.execute('SELECT * FROM mod_paciente_revision WHERE mod_pac_rev_id = %s', (revision_id,))
                revision = cursor.fetchone()
            cursor.execute('''SELECT img.mod_img_path FROM mod_images img JOIN paciente_imagen pi ON img.mod_img_id = pi.imagen_id WHERE pi.paciente_id = %s LIMIT 1''', (paciente_id,))
            img = cursor.fetchone()
            if img:
                imagen_principal = img['mod_img_path']
    finally:
        connection.close()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # Encabezado profesional
    # Logo (círculo azul con cruz blanca)
    c.setStrokeColorRGB(0.1, 0.5, 0.9)
    c.setFillColorRGB(0.1, 0.5, 0.9)
    c.circle(60, height-50, 20, fill=1)
    c.setStrokeColorRGB(1, 1, 1)
    c.setLineWidth(3)
    c.line(52, height-50, 68, height-50)  # línea horizontal de la cruz
    c.line(60, height-58, 60, height-42)  # línea vertical de la cruz
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    # Nombre y dirección
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-40, "Consultorio EndoRayo")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height-55, "Av. Principal #123, Ciudad Ejemplo")
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width/2, height-68, "HISTORIA CLÍNICA ODONTOLÓGICA")
    c.line(30, height-75, width-30, height-75)
    y = height-95

    # Datos del Paciente en tabla
    c.setFont("Helvetica-Bold", 11)
    c.setFillGray(0.85)
    c.rect(40, y, 500, 20, fill=1, stroke=0)
    c.setFillGray(0)
    c.drawString(45, y+6, "Datos del Paciente")
    y -= 24
    c.setFont("Helvetica", 10)
    campos_paciente = [
        ("Nombre y Apellido", f"{paciente['mod_pac_nombre']} {paciente['mod_pac_apellido']}" if paciente else ""),
        ("CI", f"{paciente['mod_pac_ci']}" if paciente else ""),
        ("Fecha de nacimiento", f"{paciente['mod_pac_fecha_nacimiento']}" if paciente else ""),
        ("Teléfono", f"{paciente['mod_pac_telefono']}" if paciente else ""),
        ("Email", f"{paciente['mod_pac_email']}" if paciente else ""),
        ("Dirección", f"{paciente['mod_pac_direccion']}" if paciente else ""),
        ("Observaciones", f"{paciente['mod_pac_observaciones']}" if paciente else ""),
    ]
    for label, value in campos_paciente:
        c.rect(40, y, 120, 18, fill=0, stroke=1)
        c.rect(160, y, 380, 18, fill=0, stroke=1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, y+5, label+":")
        c.setFont("Helvetica", 10)
        c.drawString(165, y+5, value)
        y -= 18
    y -= 8

    # Datos de Revisión en tabla
    if revision:
        c.setFont("Helvetica-Bold", 11)
        c.setFillGray(0.85)
        c.rect(40, y, 500, 20, fill=1, stroke=0)
        c.setFillGray(0)
        c.drawString(45, y+6, "Datos de Revisión")
        y -= 24
        campos_revision = [
            ("Dolor persistente", 'mod_pac_rev_dolor_persistente'),
            ("Sensibilidad prolongada", 'mod_pac_rev_sensibilidad_prolongada'),
            ("Hinchazón", 'mod_pac_rev_hinchazon'),
            ("Fístula", 'mod_pac_rev_fistula'),
            ("Cambio de color", 'mod_pac_rev_cambio_color'),
            ("Dolor a la percusión", 'mod_pac_rev_dolor_percusion'),
            ("Movilidad", 'mod_pac_rev_movilidad'),
            ("Caries profunda", 'mod_pac_rev_caries_profunda'),
            ("Lesión radiográfica", 'mod_pac_rev_lesion_radiografica'),
        ]
        for label, key in campos_revision:
            c.rect(40, y, 220, 18, fill=0, stroke=1)
            c.rect(260, y, 260, 18, fill=0, stroke=1)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(45, y+5, label+":")
            c.setFont("Helvetica", 10)
            valor = revision.get(key)
            valor_str = "Sí" if valor else "No"
            c.drawString(265, y+5, valor_str)
            y -= 18
        c.rect(40, y, 220, 18, fill=0, stroke=1)
        c.rect(260, y, 260, 18, fill=0, stroke=1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, y+5, "Observaciones:")
        c.setFont("Helvetica", 10)
        c.drawString(265, y+5, revision.get('mod_pac_rev_observaciones', ''))
        y -= 18
        c.rect(40, y, 220, 18, fill=0, stroke=1)
        c.rect(260, y, 260, 18, fill=0, stroke=1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, y+5, "Fecha de revisión:")
        c.setFont("Helvetica", 10)
        c.drawString(265, y+5, str(revision.get('mod_pac_rev_fecha', '')))
        y -= 26

    # Radiografía principal (justo después de los datos de revisión)
    if imagen_principal:
        # Ajuste: construir la ruta absoluta correcta para Proyecto_final/static/media/uploads
        static_path = os.path.join(os.getcwd(), 'static', imagen_principal)
        print(f"[PDF] Buscando imagen en: {static_path}")
        print(f"[PDF] ¿Existe el archivo?: {os.path.exists(static_path)}")
        if os.path.exists(static_path):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Radiografía principal:")
            y -= 10
            # Si el espacio es muy bajo, baja a la siguiente página
            if y < 180:
                c.showPage()
                y = height-90
            c.drawImage(static_path, 40, y-150, width=200, height=150, preserveAspectRatio=True, mask='auto')
            y -= 160
        else:
            print("[PDF] Imagen no encontrada, no se insertará en el PDF.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"reporte_paciente_{paciente_id}.pdf", mimetype='application/pdf')

@main_bp.route('/perfil')
def profile():
    return render_template('profile.html')  # Busca en app/templates/profile.html

@main_bp.route('/subir_imagen', methods=['POST'])
def subir_imagen():
    paciente_id = request.form.get('paciente_id')
    if 'imagen' not in request.files or not paciente_id:
        flash('No se encontró el archivo o falta el paciente.')
        return redirect(url_for('main.patient_list'))

    file = request.files['imagen']

    if file.filename == '':
        flash('No se seleccionó ninguna imagen.')
        return redirect(url_for('main.patient_images', paciente_id=paciente_id))

    # Guardar temporalmente para validación IA
    temp_path = os.path.join('/tmp', file.filename)
    file.save(temp_path)

    import shutil
    try:
        # Validar con IA antes de guardar definitivamente
        prob = None
        try:
            from PIL import Image
            import numpy as np
            img = Image.open(temp_path).convert('RGB').resize((224, 224))
            arr = np.array(img) / 255.0
            arr = np.expand_dims(arr, axis=0)
            prob = float(modelo_radiografia.predict(arr)[0][0])
            es_radio = prob > 0.9  # UMBRAL SUBIDO a 0.9
        except Exception as e_ia:
            print(f"[IA][ERROR] No se pudo procesar la imagen con el modelo: {e_ia}")
            es_radio = False
            prob = None
        print(f"[IA][INFO] Imagen: {temp_path}")
        print(f"[IA][INFO] Probabilidad de radiografía dental: {prob}")
        print(f"[IA][INFO] ¿Es radiografía dental (umbral 0.9)?: {'SÍ' if es_radio else 'NO'}")
        if not es_radio:
            flash('Solo se permiten radiografías dentales. Imagen rechazada por IA.')
            print(f"[IA] Imagen rechazada por el modelo: {temp_path}")
            os.remove(temp_path)
            return redirect(url_for('main.patient_images', paciente_id=paciente_id))

        # Si pasa la validación, guardar imagen definitiva
        print(f"[DEBUG] paciente_id recibido: {paciente_id}")
        uploads_dir = os.path.join(current_app.static_folder, 'media/uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        dest_path = os.path.join(uploads_dir, file.filename)
        shutil.move(temp_path, dest_path)
        filename = file.filename
        flash('Imagen guardada correctamente: ' + filename)
        file_url = url_for('static', filename='media/uploads/' + filename, _external=True)
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("📁 Imagen guardada:")
        print("🔗 URL:", file_url)
        print("📄 Nombre del archivo:", filename)
        print("📅 Fecha:", fecha_actual)
        db = get_db()
        with db.cursor() as cursor:
            # Insertar imagen en mod_images
            sql_img = """
                INSERT INTO mod_images (mod_img_name, mod_img_path, mod_img_date)
                VALUES (%s, %s, %s)
            """
            print(f"[DEBUG] Ejecutando: {sql_img} con valores ({filename}, media/uploads/{filename}, {fecha_actual})")
            cursor.execute(sql_img, (filename, 'media/uploads/' + filename, fecha_actual))
            imagen_id = cursor.lastrowid
            print(f"[DEBUG] imagen_id insertado: {imagen_id}")
            # Insertar relación paciente-imagen
            sql_rel = "INSERT INTO paciente_imagen (paciente_id, imagen_id) VALUES (%s, %s)"
            print(f"[DEBUG] Ejecutando: {sql_rel} con valores ({paciente_id}, {imagen_id})")
            cursor.execute(sql_rel, (paciente_id, imagen_id))
            db.commit()
            print(f"[DEBUG] Commit realizado correctamente.")
        # Siempre eliminar el archivo temporal si aún existe
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as e:
        flash(f'Error al subir la imagen: {str(e)}')
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return redirect(url_for('main.patient_images', paciente_id=paciente_id))

    return redirect(url_for('main.patient_images', paciente_id=paciente_id))


@main_bp.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Obtener ruta del archivo
        cursor.execute("SELECT mod_img_path FROM mod_images WHERE mod_img_id = %s", (image_id,))
        result = cursor.fetchone()
        
        if result:
            print("Ruta del archivo:", result)
            img_path = result['mod_img_path']
            print("img_path:", img_path)
            img_path = img_path.lstrip('/')
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            full_path = os.path.join(project_root, 'static', img_path)
            print("Ruta completa del archivo a eliminar:", full_path)
            print("¿Existe el archivo?", os.path.exists(full_path))
            if os.path.exists(full_path):
                os.remove(full_path)
                print("Archivo eliminado correctamente.")
                # Eliminar relación paciente-imagen primero
                cursor.execute("DELETE FROM paciente_imagen WHERE imagen_id = %s", (image_id,))
                # Eliminar registro de la base de datos
                cursor.execute("DELETE FROM mod_images WHERE mod_img_id = %s", (image_id,))
                db.commit()
                print("Registros eliminados de paciente_imagen y mod_images.")
                flash("Imagen eliminada correctamente.")
            else:
                print("El archivo NO existe.")
        else:
            flash("Imagen no encontrada.")
    except Exception as e:
        flash(f"Error al eliminar imagen: {str(e)}")
    
    return redirect(url_for('main.patient_list'))

@main_bp.route('/paciente/revision/save', methods=['POST'])
def save_revision():
    paciente_id = request.form.get('paciente_id')
    mod_pac_rev_dolor_persistente = 1 if request.form.get('mod_pac_rev_dolor_persistente') else 0
    mod_pac_rev_sensibilidad_prolongada = 1 if request.form.get('mod_pac_rev_sensibilidad_prolongada') else 0
    mod_pac_rev_hinchazon = 1 if request.form.get('mod_pac_rev_hinchazon') else 0
    mod_pac_rev_fistula = 1 if request.form.get('mod_pac_rev_fistula') else 0
    mod_pac_rev_cambio_color = 1 if request.form.get('mod_pac_rev_cambio_color') else 0
    mod_pac_rev_dolor_percusion = 1 if request.form.get('mod_pac_rev_dolor_percusion') else 0
    mod_pac_rev_movilidad = 1 if request.form.get('mod_pac_rev_movilidad') else 0
    mod_pac_rev_caries_profunda = 1 if request.form.get('mod_pac_rev_caries_profunda') else 0
    mod_pac_rev_lesion_radiografica = 1 if request.form.get('mod_pac_rev_lesion_radiografica') else 0
    mod_pac_rev_observaciones = request.form.get('mod_pac_rev_observaciones')

    connection = get_db()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Verificar si el paciente ya tiene una revisión asociada
            cursor.execute('SELECT mod_pac_form_diag FROM mod_paciente WHERE mod_pac_id = %s', (paciente_id,))
            result = cursor.fetchone()
            revision_id = result['mod_pac_form_diag'] if result else None

            if not revision_id:
                # INSERT: el paciente NO tiene revisión, crearla y asociarla
                cursor.execute('''
                    INSERT INTO mod_paciente_revision (
                        mod_pac_rev_dolor_persistente, mod_pac_rev_sensibilidad_prolongada, mod_pac_rev_hinchazon,
                        mod_pac_rev_fistula, mod_pac_rev_cambio_color, mod_pac_rev_dolor_percusion, mod_pac_rev_movilidad,
                        mod_pac_rev_caries_profunda, mod_pac_rev_lesion_radiografica, mod_pac_rev_observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    mod_pac_rev_dolor_persistente, mod_pac_rev_sensibilidad_prolongada, mod_pac_rev_hinchazon,
                    mod_pac_rev_fistula, mod_pac_rev_cambio_color, mod_pac_rev_dolor_percusion, mod_pac_rev_movilidad,
                    mod_pac_rev_caries_profunda, mod_pac_rev_lesion_radiografica, mod_pac_rev_observaciones
                ))
                revision_id = cursor.lastrowid
                # Actualiza el paciente con el id de la revisión
                cursor.execute('UPDATE mod_paciente SET mod_pac_form_diag=%s WHERE mod_pac_id=%s', (revision_id, paciente_id))
            else:
                # UPDATE: el paciente YA tiene revisión, solo actualizar la revisión
                cursor.execute('''
                    UPDATE mod_paciente_revision SET
                        mod_pac_rev_dolor_persistente=%s, mod_pac_rev_sensibilidad_prolongada=%s, mod_pac_rev_hinchazon=%s,
                        mod_pac_rev_fistula=%s, mod_pac_rev_cambio_color=%s, mod_pac_rev_dolor_percusion=%s, mod_pac_rev_movilidad=%s,
                        mod_pac_rev_caries_profunda=%s, mod_pac_rev_lesion_radiografica=%s, mod_pac_rev_observaciones=%s
                    WHERE mod_pac_rev_id=%s
                ''', (
                    mod_pac_rev_dolor_persistente, mod_pac_rev_sensibilidad_prolongada, mod_pac_rev_hinchazon,
                    mod_pac_rev_fistula, mod_pac_rev_cambio_color, mod_pac_rev_dolor_percusion, mod_pac_rev_movilidad,
                    mod_pac_rev_caries_profunda, mod_pac_rev_lesion_radiografica, mod_pac_rev_observaciones,
                    revision_id
                ))
            connection.commit()
    finally:
        connection.close()
    return redirect(url_for('main.patient_list'))
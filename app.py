from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import requests
import re
import os
import uuid
import json
from datetime import date

import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave-secreta-temporal')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

# ==========================================
# CLOUDINARY — PEGA TUS CREDENCIALES AQUÍ
# ==========================================
cloudinary.config(
    cloud_name = 'dujr07pke',
    api_key    = '384764555351673',
    api_secret = 'WHTigoGfk9Dw-whgtZ-ZnLDnvQc',
    secure     = True
)

MAX_UPLOAD_BYTES   = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_BYTES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# CARRUSEL — persistido en archivo JSON
# ==========================================
CARRUSEL_FILE = os.path.join(BASE_DIR, 'carrusel_data.json')


def carrusel_load():
    if os.path.exists(CARRUSEL_FILE):
        try:
            with open(CARRUSEL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo carrusel_data.json: {e}")
    return []


def carrusel_save(imagenes):
    try:
        with open(CARRUSEL_FILE, 'w', encoding='utf-8') as f:
            json.dump(imagenes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando carrusel_data.json: {e}")


carrusel_imagenes = carrusel_load()


def carrusel_to_dict(img):
    return {
        'id':          img['id'],
        'public_id':   img['public_id'],
        'url':         img['url'],
        'titulo':      img['titulo'],
        'descripcion': img['descripcion'],
        'orden':       img['orden'],
    }


# ==========================================
# USUARIOS — persistidos en archivo JSON
# Si el archivo no existe se usan los datos semilla y se crea el archivo.
# ==========================================
USUARIOS_FILE = os.path.join(BASE_DIR, 'usuarios_data.json')

USUARIOS_SEMILLA = [
    {'id':1,'nombre':'Ana','apellido':'Martínez','correo':'ana@ejemplo.com','password':'Admin123','telefono':'5512345678','nacimiento':'1990-05-20','rol':'admin','estado':'activo','direccion':'Av. Reforma 100','ciudad':'Ciudad de México','pais':'México','notas':'Administradora principal','fechaRegistro':'2024-01-10'},
    {'id':2,'nombre':'Carlos','apellido':'López','correo':'carlos@ejemplo.com','password':'Carlos123','telefono':'5598765432','nacimiento':'1985-11-03','rol':'editor','estado':'activo','direccion':'Calle Juárez 45','ciudad':'Guadalajara','pais':'México','notas':'','fechaRegistro':'2024-02-15'},
    {'id':3,'nombre':'María','apellido':'González','correo':'maria@ejemplo.com','password':'Maria123','telefono':'5567891234','nacimiento':'1995-08-17','rol':'user','estado':'activo','direccion':'Blvd. Insurgentes 200','ciudad':'Monterrey','pais':'México','notas':'Usuario estándar','fechaRegistro':'2024-03-01'},
    {'id':4,'nombre':'Pedro','apellido':'Ramírez','correo':'pedro@ejemplo.com','password':'Pedro123','telefono':'5534567890','nacimiento':'1988-02-28','rol':'viewer','estado':'inactivo','direccion':'','ciudad':'Puebla','pais':'México','notas':'Cuenta suspendida temporalmente','fechaRegistro':'2024-03-20'},
    {'id':5,'nombre':'Sofía','apellido':'Torres','correo':'sofia@ejemplo.com','password':'Sofia123','telefono':'5523456789','nacimiento':'1993-07-14','rol':'editor','estado':'activo','direccion':'Col. Roma 55','ciudad':'Ciudad de México','pais':'México','notas':'','fechaRegistro':'2024-04-05'},
    {'id':6,'nombre':'Luis','apellido':'Hernández','correo':'luis@ejemplo.com','password':'Luis1234','telefono':'5511223344','nacimiento':'1980-12-01','rol':'admin','estado':'activo','direccion':'Av. Insurgentes Sur 1500','ciudad':'Ciudad de México','pais':'México','notas':'Admin secundario','fechaRegistro':'2024-04-18'},
    {'id':7,'nombre':'Valeria','apellido':'Cruz','correo':'valeria@ejemplo.com','password':'Vale1234','telefono':'5599887766','nacimiento':'2000-03-22','rol':'user','estado':'activo','direccion':'','ciudad':'Tijuana','pais':'México','notas':'','fechaRegistro':'2024-05-02'},
]


def usuarios_load():
    if os.path.exists(USUARIOS_FILE):
        try:
            with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo usuarios_data.json: {e}")
    # Primera vez: guardar semilla y devolver
    usuarios_save(USUARIOS_SEMILLA)
    return [u.copy() for u in USUARIOS_SEMILLA]


def usuarios_save(usuarios):
    try:
        with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando usuarios_data.json: {e}")


# Carga inicial — los usuarios sobreviven reinicios
usuarios_db = usuarios_load()


def next_id():
    return max((u['id'] for u in usuarios_db), default=0) + 1


# ==========================================
# DECORADORES
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# RECAPTCHA
# ==========================================
def verify_recaptcha(recaptcha_response):
    if not recaptcha_response:
        return False
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response, 'remoteip': request.remote_addr}
    try:
        response = requests.post(verify_url, data=data)
        result = response.json()
        if result.get('success'):
            return True
        print(f"reCAPTCHA fallo: {result.get('error-codes', [])}")
        return False
    except Exception as e:
        print(f"Error al verificar reCAPTCHA: {str(e)}")
        return False


# ==========================================
# VALIDACIONES REUTILIZABLES
# ==========================================
def validar_nombre(valor):
    if not valor or len(valor.strip()) < 2:
        return 'Debe tener al menos 2 caracteres'
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', valor.strip()):
        return 'Solo se permiten letras y espacios'
    return None

def validar_correo(valor):
    if not valor:
        return 'El correo es obligatorio'
    if not re.match(r'^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$', valor.strip()):
        return 'Formato de correo inválido (ej: usuario@dominio.com)'
    return None

def validar_password(valor):
    if not valor:
        return 'La contraseña es obligatoria'
    if len(valor) < 8:
        return 'Mínimo 8 caracteres'
    if not re.search(r'[A-Z]', valor):
        return 'Debe incluir al menos una mayúscula'
    if not re.search(r'[a-z]', valor):
        return 'Debe incluir al menos una minúscula'
    if not re.search(r'\d', valor):
        return 'Debe incluir al menos un número'
    return None


# ==========================================
# RUTAS PÚBLICAS
# ==========================================
@app.route('/')
def index():
    breadcrumbs = [{'nombre': 'Inicio', 'url': url_for('index')}]
    return render_template('index.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Registro', 'url': url_for('registro')}
    ]
    if request.method == 'POST':
        nombre   = (request.form.get('nombre') or '').strip()
        correo   = (request.form.get('correo') or '').strip()
        password = (request.form.get('password') or '').strip()
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not verify_recaptcha(recaptcha_response):
            flash('Por favor, completa la verificación de reCAPTCHA', 'error')
            return render_template('registro.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        err = validar_nombre(nombre)
        if err:
            flash(f'Nombre: {err}', 'error')
            return render_template('registro.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        err = validar_correo(correo)
        if err:
            flash(f'Correo: {err}', 'error')
            return render_template('registro.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        err = validar_password(password)
        if err:
            flash(f'Contraseña: {err}', 'error')
            return render_template('registro.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        if any(u['correo'] == correo for u in usuarios_db):
            flash('Este correo ya está registrado', 'error')
            return render_template('registro.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        nuevo = {
            'id': next_id(), 'nombre': nombre, 'apellido': '',
            'correo': correo, 'password': password, 'telefono': '',
            'nacimiento': '', 'rol': 'user', 'estado': 'activo',
            'direccion': '', 'ciudad': '', 'pais': '',
            'notas': 'Registrado desde el formulario público',
            'fechaRegistro': str(date.today())
        }
        usuarios_db.append(nuevo)
        usuarios_save(usuarios_db)
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route('/login', methods=['GET', 'POST'])
def login():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Iniciar Sesión', 'url': url_for('login')}
    ]
    if request.method == 'POST':
        correo   = (request.form.get('correo') or '').strip()
        password = (request.form.get('password') or '').strip()
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not verify_recaptcha(recaptcha_response):
            flash('Por favor, completa la verificación de reCAPTCHA', 'error')
            return render_template('login.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

        usuario = next(
            (u for u in usuarios_db if u['correo'] == correo and u['password'] == password),
            None
        )

        if usuario:
            if usuario.get('estado', 'activo') == 'inactivo':
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
                return render_template('login.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)

            session['usuario_id']  = usuario['id']
            session['usuario']     = usuario['nombre']
            session['usuario_rol'] = usuario.get('rol', 'user')
            flash(f'¡Bienvenido, {usuario["nombre"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'error')

    return render_template('login.html', breadcrumbs=breadcrumbs, recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('index'))


# ==========================================
# RUTAS PRIVADAS
# ==========================================
@app.route('/dashboard')
@login_required
def dashboard():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')}
    ]
    imagenes = [carrusel_to_dict(img) for img in sorted(carrusel_imagenes, key=lambda x: x['orden'])]
    return render_template('dashboard.html', breadcrumbs=breadcrumbs, carrusel_imagenes=imagenes)


@app.route('/perfil')
@login_required
def perfil():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Mi Perfil', 'url': url_for('perfil')}
    ]
    usuario = next((u for u in usuarios_db if u['id'] == session['usuario_id']), None)
    return render_template('perfil.html', breadcrumbs=breadcrumbs, usuario=usuario)


@app.route('/configuracion')
@login_required
def configuracion():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Configuración', 'url': url_for('configuracion')}
    ]
    return render_template('configuracion.html', breadcrumbs=breadcrumbs)


@app.route('/usuarios')
@login_required
def usuarios():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Usuarios', 'url': url_for('usuarios')}
    ]
    return render_template('usuarios.html', breadcrumbs=breadcrumbs)


@app.route('/usuarios/crear')
@login_required
def usuario_crear():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Usuarios', 'url': url_for('usuarios')},
        {'nombre': 'Crear Usuario', 'url': url_for('usuario_crear')}
    ]
    return render_template('usuario_crear.html', breadcrumbs=breadcrumbs)


@app.route('/usuarios/<int:uid>')
@login_required
def usuario_detalle(uid):
    usuario = next((u for u in usuarios_db if u['id'] == uid), None)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuarios'))
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Usuarios', 'url': url_for('usuarios')},
        {'nombre': f"{usuario['nombre']} {usuario.get('apellido','')}", 'url': url_for('usuario_detalle', uid=uid)}
    ]
    return render_template('usuario_detalle.html', breadcrumbs=breadcrumbs, usuario=usuario)


@app.route('/usuarios/<int:uid>/editar')
@login_required
def usuario_editar(uid):
    usuario = next((u for u in usuarios_db if u['id'] == uid), None)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuarios'))
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Usuarios', 'url': url_for('usuarios')},
        {'nombre': f"Editar: {usuario['nombre']}", 'url': url_for('usuario_editar', uid=uid)}
    ]
    return render_template('usuario_editar.html', breadcrumbs=breadcrumbs, usuario=usuario)


@app.route('/carrusel')
@login_required
def carrusel():
    breadcrumbs = [
        {'nombre': 'Inicio', 'url': url_for('index')},
        {'nombre': 'Panel de Control', 'url': url_for('dashboard')},
        {'nombre': 'Carrusel de Imágenes', 'url': url_for('carrusel')}
    ]
    imagenes = [carrusel_to_dict(img) for img in sorted(carrusel_imagenes, key=lambda x: x['orden'])]
    return render_template('carrusel.html', breadcrumbs=breadcrumbs, imagenes=imagenes)


# ==========================================
# API JSON — CARRUSEL (con Cloudinary)
# ==========================================

@app.route('/api/carrusel', methods=['GET'])
@login_required
def api_carrusel_list():
    data = [carrusel_to_dict(img) for img in sorted(carrusel_imagenes, key=lambda x: x['orden'])]
    return jsonify(data)


@app.route('/api/carrusel', methods=['POST'])
@login_required
def api_carrusel_upload():
    """Sube una imagen a Cloudinary y guarda la referencia en disco."""
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se recibió ningún archivo'}), 400

    file = request.files['imagen']

    if not file or file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato no permitido. Usa PNG, JPG, JPEG, GIF o WEBP'}), 400

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        return jsonify({'error': 'El archivo supera el límite de 5 MB'}), 400

    titulo      = (request.form.get('titulo') or '').strip()
    descripcion = (request.form.get('descripcion') or '').strip()

    if not titulo:
        return jsonify({'error': 'El título es obligatorio'}), 400
    if len(titulo) > 100:
        return jsonify({'error': 'El título no puede superar 100 caracteres'}), 400

    try:
        public_id = f"masonite/carrusel/{uuid.uuid4().hex}"
        result    = cloudinary.uploader.upload(
            file,
            public_id       = public_id,
            overwrite       = True,
            resource_type   = 'image',
            transformation  = [{'quality': 'auto', 'fetch_format': 'auto'}]
        )
        imagen_url = result['secure_url']
        cloud_id   = result['public_id']
    except Exception as e:
        print(f"Error Cloudinary upload: {e}")
        return jsonify({'error': 'Error al subir la imagen. Verifica tus credenciales de Cloudinary.'}), 500

    nueva = {
        'id':          str(uuid.uuid4()),
        'public_id':   cloud_id,
        'url':         imagen_url,
        'titulo':      titulo,
        'descripcion': descripcion,
        'orden':       len(carrusel_imagenes) + 1,
    }
    carrusel_imagenes.append(nueva)
    carrusel_save(carrusel_imagenes)

    return jsonify(carrusel_to_dict(nueva)), 201


@app.route('/api/carrusel/<img_id>', methods=['PUT'])
@login_required
def api_carrusel_update(img_id):
    """Actualiza título y descripción de una imagen."""
    img = next((i for i in carrusel_imagenes if i['id'] == img_id), None)
    if not img:
        return jsonify({'error': 'Imagen no encontrada'}), 404

    body        = request.get_json(silent=True) or {}
    titulo      = (body.get('titulo') or '').strip()
    descripcion = (body.get('descripcion') or '').strip()

    if not titulo:
        return jsonify({'error': 'El título es obligatorio'}), 400
    if len(titulo) > 100:
        return jsonify({'error': 'El título no puede superar 100 caracteres'}), 400

    img['titulo']      = titulo
    img['descripcion'] = descripcion
    carrusel_save(carrusel_imagenes)

    return jsonify(carrusel_to_dict(img))


@app.route('/api/carrusel/reorder', methods=['POST'])
@login_required
def api_carrusel_reorder():
    """Recibe lista de ids en nuevo orden y reordena."""
    body = request.get_json(silent=True) or {}
    ids  = body.get('ids', [])

    if not isinstance(ids, list):
        return jsonify({'error': 'Se esperaba una lista de ids'}), 400

    id_order = {id_: idx + 1 for idx, id_ in enumerate(ids)}
    for img in carrusel_imagenes:
        if img['id'] in id_order:
            img['orden'] = id_order[img['id']]

    carrusel_save(carrusel_imagenes)
    data = [carrusel_to_dict(img) for img in sorted(carrusel_imagenes, key=lambda x: x['orden'])]
    return jsonify(data)


@app.route('/api/carrusel/<img_id>', methods=['DELETE'])
@login_required
def api_carrusel_delete(img_id):
    """Elimina la imagen de Cloudinary y la quita de la lista persistida."""
    global carrusel_imagenes

    img = next((i for i in carrusel_imagenes if i['id'] == img_id), None)
    if not img:
        return jsonify({'error': 'Imagen no encontrada'}), 404

    try:
        cloudinary.uploader.destroy(img['public_id'], resource_type='image')
    except Exception as e:
        print(f"Cloudinary delete warning: {e}")

    carrusel_imagenes = [i for i in carrusel_imagenes if i['id'] != img_id]

    for idx, i in enumerate(sorted(carrusel_imagenes, key=lambda x: x['orden'])):
        i['orden'] = idx + 1

    carrusel_save(carrusel_imagenes)
    return jsonify({'ok': True})


# ==========================================
# API JSON — CRUD DE USUARIOS
# ==========================================

@app.route('/api/usuarios', methods=['GET'])
@login_required
def api_usuarios_list():
    data = [{k: v for k, v in u.items() if k != 'password'} for u in usuarios_db]
    return jsonify(data)


@app.route('/api/usuarios', methods=['POST'])
@login_required
def api_usuarios_create():
    body     = request.get_json(silent=True) or {}
    nombre   = (body.get('nombre') or '').strip()
    apellido = (body.get('apellido') or '').strip()
    correo   = (body.get('correo') or '').strip()
    password = (body.get('password') or '').strip()
    telefono = (body.get('telefono') or '').strip()
    rol      = (body.get('rol') or '').strip()

    err = validar_nombre(nombre)
    if err: return jsonify({'error': f'Nombre: {err}'}), 400
    err = validar_nombre(apellido)
    if err: return jsonify({'error': f'Apellido: {err}'}), 400
    err = validar_correo(correo)
    if err: return jsonify({'error': f'Correo: {err}'}), 400
    if any(u['correo'] == correo for u in usuarios_db):
        return jsonify({'error': 'El correo ya está registrado por otro usuario'}), 409
    err = validar_password(password)
    if err: return jsonify({'error': f'Contraseña: {err}'}), 400
    if not telefono or not re.match(r'^\d{7,15}$', telefono):
        return jsonify({'error': 'Teléfono: solo dígitos, entre 7 y 15 caracteres'}), 400
    if rol not in ('admin', 'editor', 'user', 'viewer'):
        return jsonify({'error': 'Rol inválido'}), 400

    nuevo = {
        'id': next_id(), 'nombre': nombre, 'apellido': apellido,
        'correo': correo, 'password': password, 'telefono': telefono,
        'nacimiento': (body.get('nacimiento') or '').strip(),
        'rol': rol, 'estado': body.get('estado', 'activo'),
        'direccion': (body.get('direccion') or '').strip(),
        'ciudad':    (body.get('ciudad') or '').strip(),
        'pais':      (body.get('pais') or '').strip(),
        'notas':     (body.get('notas') or '').strip(),
        'fechaRegistro': str(date.today())
    }
    usuarios_db.append(nuevo)
    usuarios_save(usuarios_db)
    return jsonify({k: v for k, v in nuevo.items() if k != 'password'}), 201


@app.route('/api/usuarios/<int:uid>', methods=['PUT'])
@login_required
def api_usuarios_update(uid):
    usuario = next((u for u in usuarios_db if u['id'] == uid), None)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    body     = request.get_json(silent=True) or {}
    nombre   = (body.get('nombre') or '').strip()
    apellido = (body.get('apellido') or '').strip()
    correo   = (body.get('correo') or '').strip()
    telefono = (body.get('telefono') or '').strip()
    rol      = (body.get('rol') or '').strip()

    err = validar_nombre(nombre)
    if err: return jsonify({'error': f'Nombre: {err}'}), 400
    err = validar_nombre(apellido)
    if err: return jsonify({'error': f'Apellido: {err}'}), 400
    err = validar_correo(correo)
    if err: return jsonify({'error': f'Correo: {err}'}), 400
    if any(u['correo'] == correo and u['id'] != uid for u in usuarios_db):
        return jsonify({'error': 'El correo ya está registrado por otro usuario'}), 409
    if not telefono or not re.match(r'^\d{7,15}$', telefono):
        return jsonify({'error': 'Teléfono: solo dígitos, entre 7 y 15 caracteres'}), 400
    if rol not in ('admin', 'editor', 'user', 'viewer'):
        return jsonify({'error': 'Rol inválido'}), 400

    nueva_pwd = (body.get('password') or '').strip()
    if nueva_pwd:
        err = validar_password(nueva_pwd)
        if err: return jsonify({'error': f'Contraseña: {err}'}), 400
        usuario['password'] = nueva_pwd

    usuario.update({
        'nombre':    nombre,    'apellido':   apellido,   'correo':    correo,
        'telefono':  telefono,  'rol':        rol,
        'estado':    body.get('estado', usuario['estado']),
        'nacimiento':(body.get('nacimiento') or '').strip(),
        'direccion': (body.get('direccion')  or '').strip(),
        'ciudad':    (body.get('ciudad')     or '').strip(),
        'pais':      (body.get('pais')       or '').strip(),
        'notas':     (body.get('notas')      or '').strip(),
    })

    if session.get('usuario_id') == uid:
        session['usuario']     = usuario['nombre']
        session['usuario_rol'] = usuario['rol']

    usuarios_save(usuarios_db)
    return jsonify({k: v for k, v in usuario.items() if k != 'password'})


@app.route('/api/usuarios/<int:uid>', methods=['DELETE'])
@login_required
def api_usuarios_delete(uid):
    if session.get('usuario_id') == uid:
        return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 403

    global usuarios_db
    antes = len(usuarios_db)
    usuarios_db = [u for u in usuarios_db if u['id'] != uid]

    if len(usuarios_db) == antes:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    usuarios_save(usuarios_db)
    return jsonify({'ok': True})


# ==========================================
# RUTA DE ERROR DE PRUEBA
# ==========================================
@app.route('/simular-error')
def simular_error():
    resultado = 1 / 0
    return resultado


# ==========================================
# MANEJADORES DE ERRORES
# ==========================================
@app.errorhandler(404)
def error_404(error):
    breadcrumbs = [{'nombre': 'Inicio', 'url': url_for('index')}, {'nombre': 'Error 404', 'url': '#'}]
    return render_template('error.html', breadcrumbs=breadcrumbs, error_code=404,
                           error_title='Página no encontrada',
                           error_message='La página que buscas no existe o fue movida.'), 404

@app.errorhandler(413)
def error_413(error):
    return jsonify({'error': 'El archivo es demasiado grande. Máximo 5 MB.'}), 413

@app.errorhandler(500)
def error_500(error):
    breadcrumbs = [{'nombre': 'Inicio', 'url': url_for('index')}, {'nombre': 'Error 500', 'url': '#'}]
    return render_template('error.html', breadcrumbs=breadcrumbs, error_code=500,
                           error_title='Error del servidor',
                           error_message='Ocurrió un error inesperado. Por favor, inténtalo más tarde.'), 500

@app.errorhandler(Exception)
def error_general(error):
    breadcrumbs = [{'nombre': 'Inicio', 'url': url_for('index')}, {'nombre': 'Error', 'url': '#'}]
    return render_template('error.html', breadcrumbs=breadcrumbs, error_code='ERROR',
                           error_title='Ocurrió un problema',
                           error_message=f'Se produjo una excepción: {str(error)}'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

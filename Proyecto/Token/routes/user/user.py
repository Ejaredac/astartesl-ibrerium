from flask import Blueprint, request, Flask, request, url_for, render_template, redirect, jsonify, make_response
from sqlalchemy import exc
from app import session
from models import User, Libro, Images
import json
from app import db, bcrypt
from auth import tokenCheck
from forms import UserForm
import pdfkit
from fpdf import FPDF
config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

appuser = Blueprint('appuser', __name__, template_folder="templates")


@appuser.route('/auth/registro', methods=['POST', 'GET'])
def registro():
    mensaje = "Registro"
    pop = ""
    userExist = User(email=" ", password=" ")
    userExist.email = ""
    userExist.password = ""
    usuarioForma = UserForm(obj=userExist)
    if request.method == "POST":
        if usuarioForma.validate_on_submit():
            usuarioForma.populate_obj(userExist)

            email = usuarioForma.email.data
            password = usuarioForma.password.data
            admin = usuarioForma.admin.data
            userjson = {'email': email, 'password': password, 'admin': admin}
            usercom = User.query.filter_by(email=userjson['email']).first()
            if not usercom:
                usuarionuevo = User(
                    email=userjson['email'], password=userjson['password'])
                usuarionuevo.admin = userjson['admin']
                db.session.add(usuarionuevo)
                db.session.commit()
                return redirect(url_for('inicio'))
            else:
                pop = "Usuario ya existe"
        # user = request.get_json()
        # userExist = User.query.filter_by(email=user['email']).first()
        # if not userExist:
        #     usuario = User(email=user['email'], password=user["password"])
        #     try:
        #         db.session.add(usuario)
        #         db.session.commit()
        #         mensaje = "Usuario creado"
        #     except exc.SQLAlchemyError as e:
        #         mensaje = "Error"
        # else:
        #     mensaje = "El usuario ya existe"
        # return jsonify({"mensaje": mensaje})
    return render_template('usuario.html', forma=usuarioForma, mensaje=mensaje, pop=pop)


@appuser.route('/auth/login', methods=['POST', 'GET'])
def login():
    mensaje = "Login"
    pop = ""
    usuarioForma = UserForm()
    if request.method == "POST":
        if usuarioForma.validate_on_submit():
            userjson = {"email": usuarioForma.email.data,
                        "password": usuarioForma.password.data}
            useri = User(email=userjson['email'],
                         password=userjson['password'])
            searchUser = User.query.filter_by(email=useri.email).first()
            if searchUser:
                validation = bcrypt.check_password_hash(
                    searchUser.password, userjson["password"])
                if validation:
                    auth_token = useri.encode_auth_token(user_id=searchUser.id)
                    responseObj = {
                        "status": "exitoso",
                        "mensaje": "Login",
                        "auth_token": auth_token
                    }
                    session['token'] = auth_token
                    #request.headers['token'] = session['api_session_token']
                    return render_template('index.html')
                pop = "Datos incorrectos"
                return render_template('usuario.html', forma=usuarioForma, mensaje=mensaje, pop=pop)
    # user = request.get_json()
    # usuario = User(email=user['email'], password=user['password'])
    # searchUser = User.query.filter_by(email=usuario.email).first()
    # if searchUser:
    #     validation = bcrypt.check_password_hash(
    #         searchUser.password, user["password"])
    #     if validation:
    #         auth_token = usuario.encode_auth_token(user_id=searchUser.id)
    #         #print(f'Auth: {auth_token}')
    #         responseObj = {
    #             "status": "exitoso",
    #             "mensaje": "Login",
    #             "auth_token": auth_token
    #         }
    #         #print(responseObj)
    #         return jsonify(responseObj)
    # return jsonify({"mensaje": "Datos incorrectos"})
    return render_template('usuario.html', forma=usuarioForma, mensaje=mensaje, pop=pop)


@appuser.route('/admin/usuarios', methods=["GET"])
@tokenCheck
def getUsers(usuario):
    # print(usuario)
    if usuario['admin']:
        output = []
        usuarios = User.query.all()
        for usuario in usuarios:
            obj = {}
            obj['id'] = usuario.id
            obj['email'] = usuario.email
            obj['password'] = usuario.password
            obj['reistered_on'] = usuario.registered_on
            obj['admin'] = usuario.admin
            output.append(obj)
        return render_template('usuariostable.html', usuarios=usuarios)
    else:
        return jsonify({"mensaje": "no eres admin"})


@appuser.route('/admin', methods=["GET"])
@tokenCheck
def adminpage(usuario):
    # print(usuario)
    if usuario['admin']:
        output = []
        libros = Libro.query.all()

        return render_template('admin.html', libros=libros)
    else:
        return jsonify({"mensaje": "no eres admin"})


# --------------------------------------------------------------------------------------------------------

@appuser.route('/admin/usuario/editar/<int:id>', methods=['GET', 'POST'])
@tokenCheck
def editarusuario(usuario, id):
    if usuario['admin']:
        user = User.query.get_or_404(id)
        userForm = UserForm(obj=user)
        userForm.password.data = ""
        if request.method == "POST":
            if userForm.validate_on_submit():
                userForm.populate_obj(user)
                db.session.commit()
                return redirect(url_for('appuser.adminpage'))
        return render_template('usuario.html', forma=userForm, act="editar")
    return jsonify({"mensaje": "no eres admin"})


@appuser.route('/admin/usuario/agregar/', methods=['GET', 'POST'])
@tokenCheck
def agregarusuario(usuario):
    if usuario['admin']:
        user = User()
        userForm = UserForm(obj=user)
        userForm.password.data = ""
        if request.method == "POST":
            if userForm.validate_on_submit():
                userForm.populate_obj(user)
                # insert
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('appuser.adminpage'))
        return render_template('librotemp.html', forma=userForm, act="agregar")
    return jsonify({"mensaje": "no eres admin"})


@appuser.route('/admin/usuario/eliminar/<int:id>', methods=['GET', 'POST'])
@tokenCheck
def eliminarusuario(usuario, id):
    if usuario['admin']:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('appuser.adminpage'))
    return jsonify({"mensaje": "no eres admin"})


@appuser.route('/admin/usuario/detalle/<int:id>', methods=['GET', 'POST'])
@tokenCheck
def detalleusuario(usuario, id):
    if 'admin' in usuario:
        user = User.query.get_or_404(id)
        searchImage = Images.query.filter_by(user_id=id).first()
        imag = searchImage.rendered_data
        return render_template('userdet.html', user=user, imagen=imag)
    return jsonify({"mensaje": "no eres admin"})


@appuser.route('/user', methods=['GET', 'POST'])
@tokenCheck
def usuariopant(usuario):
    if 'admin' in usuario:
        user = User.query.get_or_404(usuario['user_id'])
        searchImage = Images.query.filter_by(
            user_id=usuario['user_id']).first()
        imag = searchImage.rendered_data
        return render_template('userdet.html', user=user, imagen=imag, id=usuario['user_id'])
    return jsonify({"mensaje": "no eres admin"})


@appuser.route('/download/user/<int:id>', methods=['GET', 'POST'])
@tokenCheck
def usuariodown(usuario, id):
    if 'admin' in usuario:
        user = User.query.get_or_404(id)
        searchImage = Images.query.filter_by(user_id=id).first()
        
        imag = searchImage.rendered_data
        data = searchImage.data
        imagen = data
        
        rendered = render_template('userdet.html', user=user, imagen=imag, id=usuario['user_id'])
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(40,10,f'Email: {user.email}')
        pdf.cell(50,30,txt=f'Admin: {user.admin.__str__()}')
        #pdf.image(imagen, 30, 30, w = 70, h = 40, type = 'jpg')
        pdf.output("archi.pdf")
        
        response = make_response(pdf.output(dest='s'))
        #response = make_response(pdf)
        response.headers["Content-Type"] = 'application/pdf'
        response.headers["Content-Disposition"] = 'inline; filename=output.pdf'
        return response
    return jsonify({"mensaje": "no encontrado"})

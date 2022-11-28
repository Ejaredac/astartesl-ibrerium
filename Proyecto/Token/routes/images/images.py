from flask import Blueprint, request,Flask,url_for,render_template,redirect,jsonify
from sqlalchemy import exc
from models import Images
from app import session
from app import db
from auth import tokenCheck
from forms import ImageForm
import base64
from models import User
imageUser = Blueprint('imageUser', __name__, template_folder="templates")


def render_image(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


@imageUser.route("/perfil", methods=["POST","GET"])
@tokenCheck
def upload(usuario):
    if 'registered_on' in usuario:
        pop=""
        mensaje="Ingresar imagen"
        imageForm = ImageForm()
        imageForm.type.data = "Perfil"
        elegido = usuario["user_id"]
        imageForm.user_id.choices = [(user.id,user.email) for user in User.query.filter_by(id=elegido).all()]
        
        if request.method == "POST":
            if imageForm.validate_on_submit():
                try:
                    elegido = imageForm.user_id.data
                    searchImage = Images.query.filter_by(user_id=elegido).first()
                    if searchImage:
                        file = imageForm.imagen.data
                        data = file.read()
                        render_file = render_image(data)
                        searchImage.data = data
                        searchImage.rendered_data = render_file
                        db.session.commit()
                        pop = "Imagen actualizada"
                        return (render_template('images.html',forma=imageForm,mensaje=mensaje,pop=pop))
                    else:
                        file = imageForm.imagen.data
                        data = file.read()
                        render_file = render_image(data)
                        newFile = Images()
                        newFile.type = imageForm.type.data
                        newFile.rendered_data = render_file
                        newFile.user_id = imageForm.user_id.data
                        newFile.data=data
                        db.session.add(newFile)
                        db.session.commit()
                        pop="Imagen insertada"
                        return (render_template('images.html',forma=imageForm,mensaje=mensaje,pop=pop))
                except exc.SQLAlchemyError as e:
                    print(e)
                    pop = f'Error: {e}'
                    return render_template ('images.html',forma=imageForm,mensaje=mensaje,pop=pop)
        return render_template ('images.html',forma=imageForm,mensaje=mensaje,pop=pop)
    else:
        return jsonify({"mensaje":"Sesion erronea"})
    # searchImage = Images.query.filter_by(user_id=usuario["user_id"]).first()
    # try:
    #     if searchImage:
    #         file = request.files["inputFile"]
    #         data = file.read()
    #         render_file = render_image(data)
    #         searchImage.data = data
    #         searchImage.rendered_data = render_file
    #         db.session.commit()
    #         return jsonify({"mensaje": "Imagen actualizada"})
    #     else:
    #         file = request.files["inputFile"]
    #         data = file.read()
    #         render_file = render_image(data)
    #         newFile = Images()
    #         newFile.type = "Perfil"
    #         newFile.rendered_data = render_file
    #         newFile.user_id = usuario["user_id"]
    #         newFile.data = data
    #         db.session.add(newFile)
    #         db.session.commit()
    #         return jsonify({"mensaje":"Imagen agregada"})
    # except exc.SQLAlchemyError as e:
    #     print(e)
    #     return jsonify({"mensaje": "Error"})

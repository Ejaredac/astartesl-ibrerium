from flask import Blueprint, request, Flask,request,url_for,render_template,redirect,jsonify
from sqlalchemy import exc
from app import session
from models import Libro,User
import json
from app import db, bcrypt
from auth import tokenCheck
from forms import LibroForm
applibros = Blueprint('applibros', __name__, template_folder="templates")

@applibros.route('/libro/editar/<int:id>',methods=['GET','POST'])
@tokenCheck
def editarlibro(usuario,id):
    if usuario['admin']:
        libro = Libro.query.get_or_404(id)
        libroForm = LibroForm(obj=libro)
        if request.method=="POST":
            if libroForm.validate_on_submit():
                libroForm.populate_obj(libro)
                db.session.commit()
                return redirect(url_for('appuser.adminpage'))
        return render_template('librotemp.html', forma=libroForm,act="editar")
    return jsonify({"mensaje":"no eres admin"})

@applibros.route('/libro/agregar',methods=['GET','POST'])
@tokenCheck
def agregarlibro(usuario):
    if usuario['admin']:
        libro = Libro()
        libroForm = LibroForm(obj=libro)
        if request.method == "POST":
            if libroForm.validate_on_submit():
                libroForm.populate_obj(libro)
                #insert
                db.session.add(libro)
                db.session.commit()
                return redirect(url_for('appuser.adminpage'))
        return render_template('librotemp.html',forma=libroForm,act="agregar")
    return jsonify({"mensaje":"no eres admin"})


@applibros.route('/libro/eliminar/<int:id>',methods=['GET','POST'])
@tokenCheck
def eliminarlibro(usuario,id):
    if usuario['admin']:
        libro = Libro.query.get_or_404(id)
        db.session.delete(libro)
        db.session.commit()
        return redirect(url_for('appuser.adminpage'))
    return jsonify({"mensaje":"no eres admin"})


@applibros.route('/libro/detalle/<int:id>',methods=['GET','POST'])
@tokenCheck
def detallelibro(usuario,id):
    if usuario['admin']:
        libro = Libro.query.get_or_404(id)
        return render_template('librodet.html',libro=libro)
    return jsonify({"mensaje":"no eres admin"})
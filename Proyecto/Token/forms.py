from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FileField,SelectField
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    admin = BooleanField('admin')
    enviar = SubmitField('enviar')


class ImageForm(FlaskForm):
    type = StringField('type', validators=[DataRequired()])
    imagen = FileField('imagen', validators=[DataRequired()])
    user_id = SelectField('user',choices=[],coerce=int,validators=[DataRequired()])
    enviar = SubmitField('enviar')

class LibroForm(FlaskForm):
    titulo = StringField('titulo',validators=[DataRequired()])
    autor = StringField('autor',validators=[DataRequired()])
    genero = StringField('genero',validators=[DataRequired()])
    enviar = SubmitField('enviar')

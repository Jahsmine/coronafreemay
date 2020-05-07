import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flaskblog import mail
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
    output_size = (325, 325)
    sized_image = Image.open(form_picture)
    sized_image.thumbnail(output_size)
    sized_image.save(picture_path)
    return picture_filename


def send_reset_email(user):
    token = user.get_reset_token()
    message = Message(
        'Password Reset Request',
        sender='africanmotheronthebeat@gmail.com',
        recipients=[user.email]
    )
    message.body = f''' To reset your password, visit the following link: 
    {url_for('users.reset_token', token=token, _external=True)} 

    If you did not make this request then simply ignore this email and no changes will be made
    '''
    mail.send(message)


def send_confirmation_email(email, subject, text, html):
    message = Message(
        subject,
        sender='africanmotheronthebeat@gmail.com',
        recipients=[email]
    )
    message.body = text
    message.html = html

    mail.send(message)

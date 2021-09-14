from ..models import Teacher
from apis.utils.exceptions import BadRequestException, NotFoundException
import cloudinary.uploader
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import jwt
from datetime import datetime, timedelta
import os

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
DEFAULT_IMAGE_URL_MALE = settings.DEFAULT_IMAGE_URL_MALE
DEFAULT_IMAGE_URL_FEMALE = settings.DEFAULT_IMAGE_URL_FEMALE
DOMAIN_NAME = settings.DOMAIN_NAME


def replace(html_content, search_string, replace_string):
    index = html_content.find(search_string)
    html_content = (
        html_content[:index]
        + replace_string
        + html_content[index + len(search_string) :]
    )
    return html_content


def replace_from_template(html_content, name, verfication_url):
    html_content = replace(
        html_content, "Hi {{name}}, </span></p>", f"Hi {name}, </span></p>"
    )
    html_content = replace(
        html_content, 'href="{{verfication_url}}"', f'href="{verfication_url}"'
    )
    return html_content


def send_verfication_mail(user):
    subject = "ExamOne | Verify Your E-mail Address"
    from_mail = settings.EMAIL_HOST_USER
    to_mail = [
        user.email,
    ]
    text_content = ""
    type_of_user = "teacher" if type(user) == Teacher else "student"
    with open("email/email.html", "r") as f:
        html_content = f.read()
    secret_code = jwt.encode(
        {
            "exp": datetime.now() + timedelta(days=1),
            f"{type_of_user}_id": str(user.id),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    verfication_url = DOMAIN_NAME + f"{type_of_user}/verify/{secret_code}/{user.id}"
    html_content = replace_from_template(html_content, user.name, verfication_url)
    msg = EmailMultiAlternatives(subject, text_content, from_mail, to_mail)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def check_for_empty(*args):
    for arg in args:
        if arg is None:
            raise BadRequestException("Parameters not passed")


def check_for_not_found(model, email):
    if not model.objects.filter(email=email).exists():
        raise NotFoundException(f"{email} does not exist")


def get_image_url_and_upload(image, user):
    try:
        if image:
            type_of_user = "teacher" if type(user) == Teacher else "student"
            image_upload = cloudinary.uploader.upload(
                image,
                folder=f"examone/{type_of_user}s/",
                public_id=f"{user.id}",
                overwrite=True,
            )
            return image_upload["url"]
        else:
            return (
                DEFAULT_IMAGE_URL_MALE
                if user.gender.lower().strip() == "male"
                else DEFAULT_IMAGE_URL_FEMALE
            )
    except Exception:
        return (
            DEFAULT_IMAGE_URL_MALE
            if user.gender.lower().strip() == "male"
            else DEFAULT_IMAGE_URL_FEMALE
        )

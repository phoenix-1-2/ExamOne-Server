from apis.models import Teacher
from apis.utils.helpers import (
    check_token_and_get_teacher,
    get_image_url_and_upload,
    send_verfication_mail,
)
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
import json
from django.conf import settings
import cryptocode
from datetime import datetime

JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
CRYPTO_SECRET_KEY = settings.CRYPTO_SECRET_KEY


@api_view(["GET", "PUT"])
def get_teacher_profile(request):
    """
    Request-Methods : GET,PUT
    Request-Headers : Authorization Token
    Request-Body : PUT ->   email_id -> str
                            password -> str
                            image -> file
                            name -> str
                            gender -> str
                            date_of_birth -> str
                            education_qualification -> JSON
    Request-Response : GET ->   email_id -> str
                                password -> str
                                image -> file
                                name -> str
                                gender -> str
                                date_of_birth -> str
                                education_qualification -> JSON
                        PUT -> message -> str
    """

    teacher = check_token_and_get_teacher(request)
    if request.method == "GET":
        education_qualification = json.loads(teacher.education_qualification)[
            "education_qualification"
        ]
        response = {
            "email": teacher.email,
            "password": cryptocode.decrypt(teacher.password, CRYPTO_SECRET_KEY),
            "image_url": teacher.image_url,
            "name": teacher.name,
            "gender": teacher.gender,
            "date_of_birth": teacher.date_of_birth,
            "education_qualification": education_qualification,
        }
        return JsonResponse(data=response, status=200)
    if request.method == "PUT":
        email = request.data.get("email")
        password = request.data.get("password")
        image = request.data.get("image")
        gender = request.data.get("gender")
        name = request.data.get("name")
        date_of_birth = request.data.get("date_of_birth")
        education_qualification = request.data.get("education_qualification")

        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, "%d-%m-%Y").date()

        if password:
            teacher.password = cryptocode.encrypt(password, CRYPTO_SECRET_KEY)

        teacher.gender = gender if gender else teacher.gender

        teacher.name = name if name else teacher.name

        teacher.date_of_birth = (
            date_of_birth if date_of_birth else teacher.date_of_birth
        )

        teacher.education_qualification = (
            education_qualification
            if education_qualification
            else teacher.education_qualification
        )
        image_url = get_image_url_and_upload(image, teacher)

        teacher.image_url = image_url if image else teacher.image_url

        if email:
            teacher.email = email
            teacher.is_verified = False
            send_verfication_mail(teacher)

        teacher.save()
        response = {"message": "Updatation Successfull"}

        return JsonResponse(response, status=200)

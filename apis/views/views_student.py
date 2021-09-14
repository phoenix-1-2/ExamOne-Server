from apis.utils.helpers import (
    check_token_and_get_student,
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
def get_student_profile(request):
    """
    Request-Methods : GET,PUT
    Request-Headers : Authorization Token
    Request-Body : PUT ->   email_id -> str
                            password -> str
                            image -> file
                            name -> str
                            gender -> str
                            batch -> str
                            date_of_birth -> str
                            education_qualification -> JSON
    Request-Response : GET ->   email_id -> str
                                password -> str
                                image -> file
                                name -> str
                                gender -> str
                                batch -> str
                                date_of_birth -> str
                                education_qualification -> JSON
                        PUT -> message -> str
    """

    student = check_token_and_get_student(request)
    if request.method == "GET":
        education_qualification = json.loads(student.education_qualification)[
            "education_qualification"
        ]
        response = {
            "email": student.email,
            "password": cryptocode.decrypt(student.password, CRYPTO_SECRET_KEY),
            "image_url": student.image_url,
            "name": student.name,
            "batch": student.batch,
            "gender": student.gender,
            "date_of_birth": student.date_of_birth,
            "education_qualification": education_qualification,
        }
        return JsonResponse(data=response, status=200)
    if request.method == "PUT":
        email = request.data.get("email")
        password = request.data.get("password")
        image = request.data.get("image")
        gender = request.data.get("gender")
        name = request.data.get("name")
        batch = request.data.get("batch")
        date_of_birth = request.data.get("date_of_birth")
        education_qualification = request.data.get("education_qualification")

        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, "%d-%m-%Y").date()

        if password:
            student.password = cryptocode.encrypt(password, CRYPTO_SECRET_KEY)

        student.gender = gender if gender else student.gender
        student.batch = batch if batch else student.batch
        student.name = name if name else student.name

        student.date_of_birth = (
            date_of_birth if date_of_birth else student.date_of_birth
        )

        student.education_qualification = (
            education_qualification
            if education_qualification
            else student.education_qualification
        )
        image_url = get_image_url_and_upload(image, student)

        student.image_url = image_url if image else student.image_url

        if email:
            student.email = email
            student.is_verified = False
            send_verfication_mail(student)

        student.save()
        response = {"message": "Updatation Successfull"}

        return JsonResponse(response, status=200)

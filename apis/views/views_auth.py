import cryptocode
from apis.utils.helpers import (
    check_for_empty,
    check_for_not_found,
    get_image_url_and_upload,
    send_verfication_mail,
)
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.conf import settings
from ..models import Student, Teacher
from ..utils.exceptions import (
    AlreadyExistsException,
    BadRequestException,
    NotFoundException,
    EmailNotVerfiedException,
)
import jwt
from datetime import datetime, timedelta

CRYPTO_SECRET_KEY = settings.CRYPTO_SECRET_KEY
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM


@api_view(["POST"])
def teacher_login(request):
    """
    Info: Login for the teacher.
    Request-Body: email_id -> str
                password -> str
    Response: message -> str
            auth_key -> str
    """
    email = request.data.get("email", None)
    password = request.data.get("password", None)

    check_for_empty(email, password)
    check_for_not_found(Teacher, email)

    teacher = Teacher.objects.get(email=email)
    if not teacher.is_verified:
        raise EmailNotVerfiedException("Email-ID not verified")
    decrypted_password = cryptocode.decrypt(teacher.password, CRYPTO_SECRET_KEY)
    if decrypted_password != password:
        raise BadRequestException("Password mismatch ! Please try again.")

    encoded_jwt = jwt.encode(
        {
            "exp": datetime.now() + timedelta(days=1),
            "teacher_id": str(teacher.id),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    response = {
        "message": "Authentication Successfull",
        "auth_key": f"Bearer {encoded_jwt}",
    }
    return JsonResponse(data=response, status=200)


@api_view(["POST"])
def teacher_registeration(request):
    """
    Info: Registeration for the teacher.
    Request-Body: email_id -> str
                password -> str
                image -> file
                name -> str
                date_of_birth -> str
                education_qualification -> JSON
    Response: message -> str
    """
    email = request.data.get("email")
    password = request.data.get("password")
    image = request.data.get("image")
    gender = request.data.get("gender")
    name = request.data.get("name")
    date_of_birth = request.data.get("date_of_birth")
    education_qualification = request.data.get("education_qualification")
    check_for_empty(
        email, gender, password, date_of_birth, education_qualification, name
    )
    if Teacher.objects.filter(email=email).exists():
        raise AlreadyExistsException("Email-Id already exists")

    password = cryptocode.encrypt(password, CRYPTO_SECRET_KEY)
    date_of_birth = datetime.strptime(date_of_birth, "%d-%m-%Y").date()
    teacher = Teacher(
        email=email,
        gender=gender,
        password=password,
        date_of_birth=date_of_birth,
        name=name,
        education_qualification=education_qualification,
    )
    image_url = get_image_url_and_upload(image, teacher)
    teacher.image_url = image_url
    teacher.save()
    send_verfication_mail(teacher)
    response = {"message": "Verfication Mail Sent"}
    return JsonResponse(response, status=200)


@api_view(["POST"])
def teacher_verify_email(request, secret_code, teacher_id):
    """
    Path Params: secret_code,teacher_id
    Response : message -> str
    """
    try:
        data = jwt.decode(secret_code, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        id = data["teacher_id"]
        if not Teacher.objects.filter(id=id).exists():
            raise NotFoundException(f"Does not exist")
        teacher = Teacher.objects.get(id=id)
        if teacher.is_verified:
            raise BadRequestException("Already Verfied User")
        teacher.is_verified = True
        teacher.save()
        response = {"message": "Registration Successfull"}
        return JsonResponse(data=response, status=200)

    except jwt.ExpiredSignatureError:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.delete()
        response = {"message": "Link is Expired"}
        return JsonResponse(data=response, status=410)


@api_view(["POST"])
def student_login(request):
    """
    Info: Login for the Student.
    Request-Body: email_id -> str
                password -> str
    Response: message -> str
            auth_key -> str
    """
    email = request.data.get("email", None)
    password = request.data.get("password", None)

    check_for_empty(email, password)
    check_for_not_found(Student, email)

    student = Student.objects.get(email=email)
    if not student.is_verified:
        raise EmailNotVerfiedException("Email-ID not verified")
    decrypted_password = cryptocode.decrypt(student.password, CRYPTO_SECRET_KEY)
    if decrypted_password != password:
        raise BadRequestException("Password mismatch ! Please try again.")

    encoded_jwt = jwt.encode(
        {
            "exp": datetime.now() + timedelta(days=1),
            "student_id": str(student.id),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    response = {
        "message": "Authentication Successfull",
        "auth_key": f"Bearer {encoded_jwt}",
    }
    return JsonResponse(data=response, status=200)


@api_view(["POST"])
def student_registeration(request):
    """
    Info: Registeration for the Student.
    Request-Body: email_id -> str
                password -> str
                image_url -> str
                name -> str
                batch -> str
                date_of_birth -> str
                education_qualification -> JSON
    Response: message -> str
    """
    email = request.data.get("email")
    password = request.data.get("password")
    image = request.data.get("image")
    gender = request.data.get("gender")
    batch = request.data.get("batch")
    name = request.data.get("name")
    date_of_birth = request.data.get("date_of_birth")
    education_qualification = request.data.get("education_qualification")
    check_for_empty(
        email, batch, gender, password, date_of_birth, education_qualification, name
    )
    if Student.objects.filter(email=email).exists():
        raise AlreadyExistsException("Email-Id already exists")

    password = cryptocode.encrypt(password, CRYPTO_SECRET_KEY)
    date_of_birth = datetime.strptime(date_of_birth, "%d-%m-%Y").date()
    student = Student(
        email=email,
        gender=gender,
        password=password,
        date_of_birth=date_of_birth,
        name=name,
        batch=batch,
        education_qualification=education_qualification,
    )
    image_url = get_image_url_and_upload(image, student)
    student.image_url = image_url
    student.save()
    send_verfication_mail(student)
    response = {"message": "Verfication Mail Sent"}
    return JsonResponse(response, status=200)


@api_view(["POST"])
def student_verify_email(request, secret_code, student_id):
    """
    Path Params: secret_code,student_id
    Response : message -> str
    """
    try:
        data = jwt.decode(secret_code, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        id = data["student_id"]
        if not Student.objects.filter(id=id).exists():
            raise NotFoundException(f"Does not exist")
        student = Student.objects.get(id=id)
        if student.is_verified:
            raise BadRequestException("Already Verfied User")
        student.is_verified = True
        student.save()
        response = {"message": "Registration Successfull"}
        return JsonResponse(data=response, status=200)

    except jwt.ExpiredSignatureError:
        student = Student.objects.get(id=student_id)
        student.delete()
        response = {"message": "Link is Expired"}
        return JsonResponse(data=response, status=410)

from django.db.models.aggregates import Max
from apis.models import Exam, Student, Teacher, Result
from apis.utils.helpers import (
    check_token_and_get_teacher,
    get_image_url_and_upload,
    send_verfication_mail,
    get_exam_report,
)
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
import json
from django.conf import settings
import cryptocode
from datetime import datetime, time
from ..utils.exceptions import UnauthorizedException, NotFoundException
from django.db.models import Q
from django.db.models import Avg

JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
CRYPTO_SECRET_KEY = settings.CRYPTO_SECRET_KEY
DOMAIN_NAME = settings.DOMAIN_NAME


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


@api_view(["POST"])
def create_exam(request):
    """
    Request-Methods : POST
    Request-Headers : Authorization Token
    Request-Body : POST ->  examination_name -> str
                            batch -> str
                            total_marks -> file
                            exam_period -> str
                            expiry_date -> str
                            questions_and_solutions -> JSON
    Request-Response : POST -> message -> str
    """
    teacher = check_token_and_get_teacher(request)
    examination_name = request.data.get("examination_name")
    batch = request.data.get("batch")
    total_marks = request.data.get("total_marks")
    exam_period = request.data.get("exam_period")
    expiry_date = request.data.get("expiry_date")
    questions_and_solutions = request.data.get("questions_and_solutions")
    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%dT%H:%M:%SZ")
    exam = Exam(
        teacher=teacher,
        examination_name=examination_name,
        batch=batch,
        total_marks=float(total_marks),
        exam_period=time(hour=int(exam_period)),
        expiry_date=expiry_date,
        questions_and_solutions=questions_and_solutions,
    )
    exam.save()
    response = {"message": "Created Successfully"}
    return JsonResponse(data=response, status=201)


@api_view(["DELETE"])
def delete_exam(request, exam_id):
    """
    Request-Methods : DELETE
    Request-Headers : Authorization Token
    Request-Response : message -> str
    """
    teacher = check_token_and_get_teacher(request)
    if not Exam.objects.filter(Q(id=exam_id)).exists():
        raise NotFoundException("Exam not found")
    exam = Exam.objects.get(id=exam_id)
    if exam.teacher != teacher:
        raise UnauthorizedException("Not allowed to access exam")
    exam.delete()
    response = {"message": "Deleted Successfully"}
    return JsonResponse(data=response, status=204)


@api_view(["GET"])
def get_all_exams(request):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    Request-Response : Array of exam
    """
    teacher = check_token_and_get_teacher(request)
    queryset = Exam.objects.filter(teacher=teacher).values()
    exams = [
        {
            "examination_name": exam["examination_name"],
            "batch": exam["batch"],
<<<<<<< HEAD
            "total_marks": float(exam["total_marks"]),
=======
            "total_marks": exam["total_marks"],
>>>>>>> main
            "exam_period": exam["exam_period"],
            "expiry_date": exam["expiry_date"],
        }
        for exam in queryset
    ]
    response = {"count": len(queryset), "exams": exams}
    return JsonResponse(data=response, status=200)


@api_view(["GET"])
def get_batch_result(request, exam_id):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    """
    teacher = check_token_and_get_teacher(request)
    if not Exam.objects.filter(id=exam_id).exists():
        raise NotFoundException("Exam not found")

    exam = Exam.objects.get(id=exam_id)
    if exam.teacher != teacher:
        raise UnauthorizedException("Not allowed to access exam")
    queryset = Result.objects.filter(Q(teacher=teacher) & Q(exam=exam))
    highest_score = queryset.order_by("score").last()
    lowest_score = queryset.order_by("score").first()
    response = {
        "exam_name": exam.examination_name,
        "teacher_name": teacher.name,
        "max_score": float(exam.total_marks),
        "avg_score": float(queryset.aggregate(avg=Avg("score"))["avg"]),
        "highest_score": {
            "student_name": highest_score.student.name,
            "grade": highest_score.grade,
            "score": float(highest_score.score),
            "url": f"{DOMAIN_NAME}/teacher/results/{exam.id}/{highest_score.student.id}",
        },
        "minimum_score": {
            "student_name": lowest_score.student.name,
            "grade": lowest_score.grade,
            "score": float(lowest_score.score),
            "url": f"{DOMAIN_NAME}/teacher/results/{exam.id}/{lowest_score.student.id}",
        },
        "batch_report": [
            {
                "student_name": result.student.name,
                "exam_start_date_time": result.exam_start_date_time,
                "grade": result.grade,
                "score": float(result.score),
                "url": f"{DOMAIN_NAME}/teacher/results/{exam.id}/{result.student.id}",
            }
            for result in queryset
        ],
    }
    return JsonResponse(data=response, status=200)


@api_view(["GET"])
def get_student_result(request, exam_id, student_id):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    """
    teacher = check_token_and_get_teacher(request)
    student = Student.objects.get(id=student_id)
    exam = Exam.objects.get(id=exam_id)
    if exam.teacher != teacher:
        raise UnauthorizedException("Not allowed to access exam")

    result = Result.objects.filter(
        Q(student=student) & Q(exam=exam) & Q(teacher=teacher)
    ).first()

    response = {
        "exam_name": exam.examination_name,
        "exam_start_date_time": result.exam_start_date_time,
        "student_name": student.name,
        "teacher_name": teacher.name,
        "score": float(result.score),
        "max_score": float(result.total_marks),
        "grade": result.grade,
        "report": get_exam_report(
            exam.questions_and_solutions, result.student_solutions
        ),
    }
    return JsonResponse(data=response, status=200)

from ..utils.exceptions import NotFoundException, AlreadyExistsException
from apis.models import Result, Exam
from apis.utils.helpers import (
    check_token_and_get_student,
    get_image_url_and_upload,
    send_verfication_mail,
    evaluate_exam_score,
    evaluate_exam_grade,
    get_exam_report,
    get_total_mcqs,
    get_total_subjective_questions,
    get_total_coding_problems,
    get_questions,
)
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
import json
from django.conf import settings
import cryptocode
from datetime import datetime, timedelta, timezone
from django.db.models import Q

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


@api_view(["POST"])
def evaluate_exams(request, exam_id):
    """
    Request-Methods :POST
    Request-Headers : Authorization Token
    Request-Body: Student-Solution -> JSON
    Response:   "student_name" -> str,
                "teacher_name" -> str,
                "batch" -> str,
                "marks" -> str,
                "exam_start_date_time" -> str,
                "total_marks" -> str,
                "grade" -> str
    """
    student_solutions = request.data.get("student_solutions")

    student = check_token_and_get_student(request)
    if not Exam.objects.filter(Q(id=exam_id) & Q(batch=student.batch)).exists():
        raise NotFoundException("Exam not found")
    exam = Exam.objects.get(Q(id=exam_id) & Q(batch=student.batch))

    exam_start_date_time = datetime.now(tz=timezone.utc) - timedelta(
        hours=exam.exam_period.hour
    )

    if Result.objects.filter(Q(exam=exam) & Q(student=student)).exists():
        raise AlreadyExistsException("Already Submitted the exam")

    score = evaluate_exam_score(exam.questions_and_solutions, student_solutions)[
        "total_score"
    ]
    grade = evaluate_exam_grade(score, exam.total_marks)

    result = Result(
        exam_start_date_time=(exam_start_date_time),
        exam=exam,
        student=student,
        teacher=exam.teacher,
        student_solutions=student_solutions,
        total_marks=float(exam.total_marks),
        score=score,
        grade=grade,
    )
    result.save()
    response = {
        "student_name": student.name,
        "teacher_name": exam.teacher.name,
        "batch": exam.batch,
        "score": score,
        "exam_start_date_time": (exam_start_date_time),
        "total_marks": float(exam.total_marks),
        "grade": grade,
    }
    return JsonResponse(data=response, status=200)


@api_view(["GET"])
def get_student_result(request, exam_id):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    """
    student = check_token_and_get_student(request)
    if not Exam.objects.filter(Q(id=exam_id) & Q(batch=student.batch)).exists():
        raise NotFoundException("Exam not found")
    exam = Exam.objects.get(Q(id=exam_id) & Q(batch=student.batch))
    result = Result.objects.filter(Q(student=student) & Q(exam=exam)).first()
    response = {
        "exam_name": exam.examination_name,
        "exam_start_date_time": result.exam_start_date_time,
        "student_name": student.name,
        "teacher_name": result.teacher.name,
        "score": float(result.score),
        "max_score": float(result.total_marks),
        "grade": result.grade,
        "report": get_exam_report(
            exam.questions_and_solutions, result.student_solutions
        ),
    }
    return JsonResponse(data=response, status=200)


@api_view(["GET"])
def get_exam_info(request, exam_id):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    """
    student = check_token_and_get_student(request)
    if not Exam.objects.filter(Q(id=exam_id) & Q(batch=student.batch)).exists():
        raise NotFoundException("Exam not found")
    exam = Exam.objects.get(Q(id=exam_id) & Q(batch=student.batch))
    response = {
        "exam_info": {
            "examination_name": exam.examination_name,
            "batch": exam.batch,
            "total_marks": float(exam.total_marks),
            "exam_period": exam.exam_period,
            "expiry_date": exam.expiry_date,
            "total_mcqs": get_total_mcqs(exam.questions_and_solutions),
            "total_subjective_questions": get_total_subjective_questions(
                exam.questions_and_solutions
            ),
            "total_coding_problems": get_total_coding_problems(
                exam.questions_and_solutions
            ),
        }
    }
    return JsonResponse(data=response, status=200)


@api_view(["GET"])
def get_exam_questions(request, exam_id):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    """
    student = check_token_and_get_student(request)
    if not Exam.objects.filter(Q(id=exam_id) & Q(batch=student.batch)).exists():
        raise NotFoundException("Exam not found")
    exam = Exam.objects.get(Q(id=exam_id) & Q(batch=student.batch))
    response = get_questions(exam.questions_and_solutions)
    response["total_marks"] = float(exam.total_marks)
    return JsonResponse(data=response, status=200)


@api_view(["GET"])
def get_undone_exams(request):
    """
    Request-Methods : GET
    Request-Headers : Authorization Token
    """
    student = check_token_and_get_student(request)
    all_exams = Exam.objects.filter(batch=student.batch)
    undone_exams = []
    for exam in all_exams:
        if not Result.objects.filter(exam=exam).exists():
            res = {
                "examination_name": exam.examination_name,
                "batch": exam.batch,
                "total_marks": float(exam.total_marks),
                "exam_period": exam.exam_period,
                "expiry_date": exam.expiry_date,
            }
            undone_exams.append(res)
    response = {"count": len(undone_exams), "exams": undone_exams}
    return JsonResponse(data=response, status=200)

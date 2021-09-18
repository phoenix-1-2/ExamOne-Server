from ..models import Student, Teacher
from apis.utils.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
    ServiceUnavailableException,
    InvalidTokenException,
)
import cloudinary.uploader
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import jwt
import json
from datetime import datetime, timedelta
import requests
import time
import paralleldots

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
DEFAULT_IMAGE_URL_MALE = settings.DEFAULT_IMAGE_URL_MALE
DEFAULT_IMAGE_URL_FEMALE = settings.DEFAULT_IMAGE_URL_FEMALE
DOMAIN_NAME = settings.DOMAIN_NAME
LIMITED_TEST_CASES_SIZE = 2
HACKEREARTH_SECRET_KEY = settings.HACKEREARTH_SECRET_KEY
LANGUAGE_CODE = settings.LANGUAGE_SUPPORTED
PARALLEL_DOTS_API_KEY = settings.PARALLEL_DOTS_API_KEY
SUBMISSION_URL = "https://api.hackerearth.com/v4/partner/code-evaluation/submissions/"
TIME_WAIT_FOR_RESULT = 3


def check_token_and_get_student(request):
    auth_token = request.headers.get("Authorization", None)
    if auth_token is None:
        raise UnauthorizedException("Token not passed")
    if auth_token.split(" ")[0].lower() != "bearer":
        raise BadRequestException("Token should be a bearer token")

    auth_token = auth_token.split(" ")[1]
    try:
        data = jwt.decode(auth_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        student_id = data["student_id"]
        if not Student.objects.filter(id=student_id).exists():
            raise NotFoundException(f"Does not exist")
        student = Student.objects.get(id=student_id)
        if not student.is_verified:
            raise BadRequestException("User Not Verfied")
        return student
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Login Again,  Auth Token Expired")
    except KeyError:
        raise InvalidTokenException("Auth Token Invalid")


def check_token_and_get_teacher(request):
    auth_token = request.headers.get("Authorization", None)
    if auth_token is None:
        raise UnauthorizedException("Token not passed")
    if auth_token.split(" ")[0].lower() != "bearer":
        raise BadRequestException("Token should be a bearer token")

    auth_token = auth_token.split(" ")[1]
    try:
        data = jwt.decode(auth_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        teacher_id = data["teacher_id"]
        if not Teacher.objects.filter(id=teacher_id).exists():
            raise NotFoundException(f"Does not exist")
        teacher = Teacher.objects.get(id=teacher_id)
        if not teacher.is_verified:
            raise BadRequestException("User Not Verfied")
        return teacher
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Login Again,  Auth Token Expired")


def check_token_and_get_student(request):
    auth_token = request.headers.get("Authorization", None)
    if auth_token is None:
        raise UnauthorizedException("Token not passed")
    if auth_token.split(" ")[0].lower() != "bearer":
        raise BadRequestException("Token should be a bearer token")

    auth_token = auth_token.split(" ")[1]
    try:
        data = jwt.decode(auth_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        student_id = data["student_id"]
        if not Student.objects.filter(id=student_id).exists():
            raise NotFoundException(f"Does not exist")
        student = Student.objects.get(id=student_id)
        if not student.is_verified:
            raise BadRequestException("User Not Verfied")
        return student
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Login Again,  Auth Token Expired")
    except KeyError:
        raise InvalidTokenException("Auth Token Invalid")


def check_token_and_get_teacher(request):
    auth_token = request.headers.get("Authorization", None)
    if auth_token is None:
        raise UnauthorizedException("Token not passed")
    if auth_token.split(" ")[0].lower() != "bearer":
        raise BadRequestException("Token should be a bearer token")

    auth_token = auth_token.split(" ")[1]
    try:
        data = jwt.decode(auth_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        teacher_id = data["teacher_id"]
        if not Teacher.objects.filter(id=teacher_id).exists():
            raise NotFoundException(f"Does not exist")
        teacher = Teacher.objects.get(id=teacher_id)
        if not teacher.is_verified:
            raise BadRequestException("User Not Verfied")
        return teacher
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Login Again,  Auth Token Expired")


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
    html_content = requests.get(
        "https://res.cloudinary.com/phoenix-redstone-04/raw/upload/v1631603991/examone/email/email_udwtpd.html"
    ).text
    secret_code = jwt.encode(
        {
            "exp": datetime.now() + timedelta(days=1),
            f"{type_of_user}_id": str(user.id),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    verfication_url = DOMAIN_NAME + f"/{type_of_user}/verify/{secret_code}/{user.id}"
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


def run_and_get_result(source_code, test_case):
    try:
        headers = {"client-secret": HACKEREARTH_SECRET_KEY}
        data = {
            "source": source_code,
            "lang": LANGUAGE_CODE,
            "time_limit": TIME_WAIT_FOR_RESULT,
            "memory_limit": 246323,
            "input": test_case,
            "callback": "https://client.com/execute/result/",
            "id": 21312112,
        }
        response = requests.post(SUBMISSION_URL, json=data, headers=headers)
        response = json.loads(response.text)
        status_update_url = response["status_update_url"]
        time.sleep(TIME_WAIT_FOR_RESULT)
        response = requests.get(status_update_url, headers=headers)
        response = json.loads(response.text)
        output_url = response["result"]["run_status"]["output"]
        response = requests.get(output_url)
        return response.text.strip()
    except Exception as e:
        raise ServiceUnavailableException(str(e))


def evaluate_coding_result(original_result, student_result):
    return original_result.strip() == student_result.strip()


def check_correctness_of_solution(original_solution, solution):
    if original_solution.lower() == solution.lower():
        return 1
    try:
        paralleldots.set_api_key(PARALLEL_DOTS_API_KEY)
        response = paralleldots.similarity(original_solution, solution)
        similarity_score = response["similarity_score"]
        return similarity_score
    except Exception:
        return 0


def evaluate_exam_score(questions_and_solutions, student_solutions):
    """
    Return Value :
    {
        "total_score":"",
        "result":{
            "mcq":[
                {
                    "question_id":"",
                    "marks_acheived":10,
                },
            ],
            "subjective":[
                {
                    "question_id":"",
                    "marks_acheived":10,
                },
            ],
            "coding":[
                {
                    "question_id":"",
                    "test_cases":[
                        {
                        "test_case": "10 7 1 5 \n 2",
                        "student_result": "false",
                        "original_result": "false",
                        "passed": true
                        }
                    ],
                    "marks_acheived":10
                },
            ]
        }
    }
    """

    questions_and_solutions = json.loads(questions_and_solutions)[
        "questions_and_solutions"
    ]
    student_solutions = json.loads(student_solutions)["student_solutions"]

    mcqs = questions_and_solutions["mcq"]
    student_solutions_mcq = student_solutions["mcq"]

    mcq_result = []
    for student_solution_mcq in student_solutions_mcq:
        question_id = student_solution_mcq["question_id"]
        solution = student_solution_mcq["solution"]
        question_mcq = [mcq for mcq in mcqs if mcq["question_id"] == question_id][0]
        original_solution = question_mcq["solution"]
        marks_acheived = 0
        if solution == original_solution:
            marks_acheived = question_mcq["total_marks"]

        mcq_result.append(
            {
                "question_id": question_id,
                "marks_acheived": marks_acheived,
            }
        )

    subjectives = questions_and_solutions["subjective"]
    student_solutions_subjectives = student_solutions["subjective"]

    subjectives_result = []
    for student_solution_subjectives in student_solutions_subjectives:
        question_id = student_solution_subjectives["question_id"]
        solution = student_solution_subjectives["solution"]
        question_subjective = [
            subjective
            for subjective in subjectives
            if subjective["question_id"] == question_id
        ][0]
        original_solution = question_subjective["solution"]

        marks_acheived = (
            check_correctness_of_solution(original_solution, solution)
            * question_subjective["total_marks"]
        )
        marks_acheived = round(marks_acheived,2)
        subjectives_result.append(
            {
                "question_id": question_id,
                "marks_acheived": marks_acheived,
            }
        )

    codings = questions_and_solutions["coding"]
    student_solutions_codings = student_solutions["coding"]
    codings_result = []
    for student_solution_codings in student_solutions_codings:
        question_id = student_solution_codings["question_id"]
        source_code = student_solution_codings["source_code"]
        question_coding = [
            coding for coding in codings if coding["question_id"] == question_id
        ][0]
        test_cases = question_coding["test_cases"]
        test_cases_result = []
        for test_case in test_cases:
            try:
                student_result = run_and_get_result(source_code, test_case["test_case"])
                test_cases_result.append(
                    {
                        "test_case": test_case["test_case"],
                        "student_result": student_result,
                        "original_result": test_case["result"],
                        "passed": evaluate_coding_result(
                            test_case["result"], student_result
                        ),
                    }
                )
            except Exception:
                test_cases_result.append(
                    {
                        "test_case": test_case["test_case"],
                        "student_result": "Error",
                        "original_result": test_case["result"],
                        "passed": False,
                    }
                )

        total_test_case_success = sum(
            [(1 if test_case["passed"] else 0) for test_case in test_cases_result]
        )
        total_test_cases_count = len(test_cases_result)
        marks_acheived = (
            total_test_case_success / total_test_cases_count
        ) * question_coding["total_marks"]
        codings_result.append(
            {
                "question_id": question_id,
                "test_cases": test_cases_result,
                "marks_acheived": marks_acheived,
            }
        )

    total_score = (
        sum([mcq_res["marks_acheived"] for mcq_res in mcq_result])
        + sum(
            [
                subjective_result["marks_acheived"]
                for subjective_result in subjectives_result
            ]
        )
        + sum([coding_result["marks_acheived"] for coding_result in codings_result])
    )

    result = {
        "total_score": float(round(total_score, 1)),
        "result": {
            "mcq": mcq_result,
            "subjective": subjectives_result,
            "coding": codings_result,
        },
    }
    return result


def evaluate_exam_grade(score, total_marks):
    percentage = (score / float(total_marks)) * 100
    grade = ""
    if percentage > 90 and percentage <= 100:
        grade = "A+"
    elif percentage > 80 and percentage <= 90:
        grade = "A"
    elif percentage > 70 and percentage <= 80:
        grade = "B+"
    elif percentage > 60 and percentage <= 70:
        grade = "B"
    elif percentage > 50 and percentage <= 60:
        grade = "C+"
    elif percentage > 40 and percentage <= 50:
        grade = "C"
    elif percentage > 30 and percentage <= 40:
        grade = "D+"
    elif percentage > 20 and percentage <= 30:
        grade = "E"
    else:
        grade = "F"
    return grade


def get_exam_report(questions_and_solutions, student_solutions):
    result = evaluate_exam_score(questions_and_solutions, student_solutions)["result"]
    questions_and_solutions = json.loads(questions_and_solutions)[
        "questions_and_solutions"
    ]
    student_solutions = json.loads(student_solutions)["student_solutions"]
    # MCQs
    mcqs = questions_and_solutions["mcq"]
    mcqs_result = result["mcq"]
    student_solutions_mcq = student_solutions["mcq"]
    exam_set_mcqs = [
        {
            "question_id": mcq["question_id"],
            "question": mcq["question"],
            "option1": mcq["option1"],
            "option2": mcq["option2"],
            "option3": mcq["option3"],
            "option4": mcq["option4"],
            "total_marks": mcq["total_marks"],
            "original_solution": mcq["solution"],
        }
        for mcq in mcqs
    ]
    for exam_set_mcq in exam_set_mcqs:
        exam_set_mcq["student_solution"] = [
            student_solution_mcq["solution"]
            for student_solution_mcq in student_solutions_mcq
            if student_solution_mcq["question_id"] == exam_set_mcq["question_id"]
        ][0]

    for exam_set_mcq in exam_set_mcqs:
        exam_set_mcq["marks_acheived"] = [
            mcq_result["marks_acheived"]
            for mcq_result in mcqs_result
            if mcq_result["question_id"] == exam_set_mcq["question_id"]
        ][0]

    # Subjectives
    subjectives = questions_and_solutions["subjective"]
    subjectives_result = result["subjective"]
    student_solutions_subjectives = student_solutions["subjective"]

    exam_set_subjectives = [
        {
            "question_id": subjective["question_id"],
            "question": subjective["question"],
            "total_marks": subjective["total_marks"],
            "original_solution": subjective["solution"],
        }
        for subjective in subjectives
    ]
    for exam_set_subjective in exam_set_subjectives:
        exam_set_subjective["student_solution"] = [
            student_solutions_subjective["solution"]
            for student_solutions_subjective in student_solutions_subjectives
            if student_solutions_subjective["question_id"]
            == exam_set_subjective["question_id"]
        ][0]

    for exam_set_subjective in exam_set_subjectives:
        exam_set_subjective["marks_acheived"] = [
            subjective_result["marks_acheived"]
            for subjective_result in subjectives_result
            if subjective_result["question_id"] == exam_set_subjective["question_id"]
        ][0]

    # Coding
    codings = questions_and_solutions["coding"]
    codings_result = result["coding"]
    student_solutions_codings = student_solutions["coding"]

    exam_set_codings = [
        {
            "question_id": coding["question_id"],
            "question": coding["question"],
            "total_marks": coding["total_marks"],
        }
        for coding in codings
    ]

    for exam_set_coding in exam_set_codings:
        exam_set_coding["student_source_code"] = [
            student_solutions_coding["source_code"]
            for student_solutions_coding in student_solutions_codings
            if student_solutions_coding["question_id"] == exam_set_coding["question_id"]
        ][0]

    for exam_set_coding in exam_set_codings:
        exam_set_coding["test_cases"] = [
            coding_result["test_cases"]
            for coding_result in codings_result
            if coding_result["question_id"] == exam_set_coding["question_id"]
        ][0]

        exam_set_coding["marks_acheived"] = [
            coding_result["marks_acheived"]
            for coding_result in codings_result
            if coding_result["question_id"] == exam_set_coding["question_id"]
        ][0]

        exam_set_coding["total_test_cases_success"] = sum(
            [
                (1 if test_case["passed"] else 0)
                for test_case in exam_set_coding["test_cases"]
            ]
        )
        exam_set_coding["total_test_cases_count"] = len(exam_set_coding["test_cases"])

    report = {
        "mcq": {
            "total_marks": sum([mcq["total_marks"] for mcq in mcqs]),
            "marks_acheived": sum(
                mcq_result["marks_acheived"] for mcq_result in mcqs_result
            ),
            "exam_set": exam_set_mcqs,
        },
        "subjective": {
            "total_marks": sum(
                [subjective["total_marks"] for subjective in subjectives]
            ),
            "marks_acheived": sum(
                [
                    subjective_result["marks_acheived"]
                    for subjective_result in subjectives_result
                ]
            ),
            "exam_set": exam_set_subjectives,
        },
        "coding": {
            "total_marks": sum([coding["total_marks"] for coding in codings]),
            "marks_acheived": sum(
                [coding_result["marks_acheived"] for coding_result in codings_result]
            ),
            "exam_set": exam_set_codings,
        },
    }
    return report


def get_total_mcqs(questions_and_solutions):
    questions_and_solutions = json.loads(questions_and_solutions)[
        "questions_and_solutions"
    ]
    total_mcqs = len(questions_and_solutions["mcq"])
    return total_mcqs


def get_total_subjective_questions(questions_and_solutions):
    questions_and_solutions = json.loads(questions_and_solutions)[
        "questions_and_solutions"
    ]
    total_subjective_questions = len(questions_and_solutions["subjective"])
    return total_subjective_questions


def get_total_coding_problems(questions_and_solutions):
    questions_and_solutions = json.loads(questions_and_solutions)[
        "questions_and_solutions"
    ]
    total_coding_questions = len(questions_and_solutions["coding"])
    return total_coding_questions


def get_questions(questions_and_solutions):
    total_mcqs = get_total_mcqs(questions_and_solutions)
    total_subjective_questions = get_total_subjective_questions(questions_and_solutions)
    total_coding_problems = get_total_coding_problems(questions_and_solutions)
    questions_and_solutions = json.loads(questions_and_solutions)[
        "questions_and_solutions"
    ]
    mcqs = [
        {
            "question_id": mcq["question_id"],
            "question": mcq["question"],
            "option1": mcq["option1"],
            "option2": mcq["option2"],
            "option3": mcq["option3"],
            "option4": mcq["option4"],
            "total_marks": mcq["total_marks"],
        }
        for mcq in questions_and_solutions["mcq"]
    ]
    subjective_questions = [
        {
            "question_id": subjective_question["question_id"],
            "question": subjective_question["question"],
            "total_marks": subjective_question["total_marks"],
        }
        for subjective_question in questions_and_solutions["subjective"]
    ]

    coding_questions = [
        {
            "question_id": coding_question["question_id"],
            "question": coding_question["question"],
            "limited_test_cases": coding_question["test_cases"][
                :LIMITED_TEST_CASES_SIZE
            ],
            "total_marks": coding_question["total_marks"],
        }
        for coding_question in questions_and_solutions["coding"]
    ]

    question_set = {
        "question_set": {
            "total_mcqs": total_mcqs,
            "total_subjective_questions": total_subjective_questions,
            "total_coding_problems": total_coding_problems,
            "mcqs": mcqs,
            "subjective": subjective_questions,
            "coding": coding_questions,
        }
    }

    return question_set

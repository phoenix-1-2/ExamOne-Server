from django.http.response import JsonResponse
from rest_framework.decorators import api_view


@api_view(["POST"])
def teacher_login(request):
    """
    Teacher Login Post Request
    request_body: email_id,password
    response: auth_key
    """

    return JsonResponse(data={}, status_code=200)


@api_view(["POST"])
def student_login(request):
    pass


@api_view(["POST"])
def teacher_registeration(request):
    pass


@api_view(["POST"])
def student_registeration(request):
    pass

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django.http.response import JsonResponse

from producer import EmailProducerInstance

@require_http_methods(["GET"])
def create_brand_new_email_query(request):
    data = request.GET

    email_data = {
        'topic': 'Stworzono konto',
        'body': 'Witaj twoje konto zostało utworzone'
    }

    message = EmailProducerInstance.add_email_to_queue(email_data)

    return JsonResponse(
        data={
            'test': 1,
            'test2': 32
        }
    )

@require_http_methods(["POST"])
def create_modify_email_notification(request):
    data = request.POST
    receiver = data['to_email']
    subject = data['subject']
    email_data = {
        'receiver': receiver,
        'subject': subject,
    }

    message = EmailProducerInstance.add_email_to_queue(email_data)

    return JsonResponse(
        data={
            'test': 1,
            'test2': 32
        }
    )





from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django.http.response import JsonResponse

from producer import EmailProducerInstance

@require_http_methods(["GET"])
def create_brand_new_email_query(request):
    data = request.GET

    email_data = {
        'topic': 'Test',
        'body': 'Esa'
    }

    message = EmailProducerInstance.add_email_to_queue(email_data)

    return JsonResponse(
        data={
            'test': 1,
            'test2': 32
        }
    )

    # if everthing will work fine we have to add this into queue
    # email_service_create.add_email_to_queue(data)






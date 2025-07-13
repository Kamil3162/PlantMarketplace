from django.http import JsonResponse, HttpRequest


def health_endpoint(request: HttpRequest):
    print(request.get_full_path())
    print(request.get_host())
    print(request.get_port())
    print(request.path)
    return JsonResponse({'status': 'ok'})
from django.http import JsonResponse, HttpResponse


class CustomResponse(JsonResponse):
    def __init__(self, detail: str, status_code: int, type: str = "success"):
        self.response_data = {
            'type': type,
            'detail': detail
        }
        super().__init__(data=self.response_data, status=status_code)

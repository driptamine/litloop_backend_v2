from django import http

class CorsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = http.HttpResponse()
            response["Content-Length"] = "0"
            response["Access-Control-Max-Age"] = "0"
        else:
            response = self.get_response(request)

        origin = request.META.get("HTTP_ORIGIN", "")
        if origin:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Vary"] = "Origin"
        else:
            response["Access-Control-Allow-Origin"] = "*"

        response["Access-Control-Allow-Methods"] = "DELETE, GET, OPTIONS, PATCH, POST, PUT"
        acrh = request.META.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS", "")
        response["Access-Control-Allow-Headers"] = acrh or "accept, authorization, content-type, x-csrftoken, x-requested-with"
        return response

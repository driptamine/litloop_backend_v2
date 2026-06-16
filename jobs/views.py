import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Application, JobPosting, Resume

# Create your views here.
@csrf_exempt
def vacancies_api(request):
    if request.method == 'GET':
        vacancies = JobPosting.objects.select_related('company').all().order_by('-created_at')
        data = [v.as_dict() for v in vacancies]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            company_id = body['company_id']
            company = Company.objects.get(id=company_id)
            vacancy = JobPosting.objects.create(
                title=body['title'],
                description=body.get('description', ''),
                company=company,
            )
            return JsonResponse(vacancy.as_dict(), status=201)
        except Company.DoesNotExist:
            return JsonResponse({"error": "Company not found"}, status=404)
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest("Invalid JSON or missing fields")

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def companies_api(request):
    if request.method == 'GET':
        companies = Company.objects.all()
        return JsonResponse([c.as_dict() for c in companies], safe=False)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            company = Company.objects.create(
                name=body['name'],
                description=body.get('description', ''),
                website=body.get('website', '')
            )
            return JsonResponse(company.as_dict(), status=201)
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest("Invalid JSON or missing fields")

    return JsonResponse({"error": "Method not allowed"}, status=405)

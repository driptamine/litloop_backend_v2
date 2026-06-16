import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Application, JobPosting, Resume

@method_decorator(csrf_exempt, name='dispatch')  # For testing, consider proper CSRF later
@method_decorator(login_required, name='dispatch')
class ApplicationView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            job_id       = data.get('job_id')
            cover_letter = data.get('cover_letter', '')
            resume_id    = data.get('resume_id')

            job = JobPosting.objects.get(id=job_id)
             
            resume = Resume.objects.get(id=resume_id, user=request.user)

            application = Application.objects.create(
                user=request.user,
                job=job,
                cover_letter=cover_letter,
                resume=resume
            )
            return JsonResponse({
                'success': True,
                'application_id': application.id,
                'message': 'Application submitted successfully.'
            })
        except JobPosting.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job not found.'}, status=404)
        except Resume.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Resume not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

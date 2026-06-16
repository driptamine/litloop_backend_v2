# Create your models here.
from django.db import models
from users.models import User  # if you have user accounts

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    summary = models.TextField()
    skills = models.TextField()
    experience = models.TextField()
    education = models.TextField()

    def __str__(self):
        return f"Resume of {self.user.username} ({self.pk})"



class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    location = models.CharField(max_length=255, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class Application(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.applicant.username} for {self.job.title}"


class CoverLetter(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='cover_letter')
    content = models.TextField()

    def __str__(self):
        return f"Cover letter for {self.application}"

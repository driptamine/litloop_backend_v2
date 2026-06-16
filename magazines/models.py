from django.db import models


class Magazine(models.Model):
    title = models.CharField(max_length=255)
    issue_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.issue_date})"

class Cover(models.Model):
    magazine = models.OneToOneField(Magazine, on_delete=models.CASCADE, related_name='cover')
    featured_person = models.CharField(max_length=255)
    image_url = models.URLField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def as_dict(self):
        return {
            "id": self.id,
            "magazine_title": self.magazine.title,
            "featured_person": self.featured_person,
            "issue_date": self.magazine.issue_date.isoformat(),
            "image_url": self.image_url,
            "description": self.magazine.description,
            "price": str(self.price),
            "is_available": self.is_available,
        }

from django.db import models
from django.core.exceptions import ValidationError  # <--- Import this
class HeroSlide(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='hero_slides/', blank=True, null=True) 
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class PromoMessage(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text

class VideoSection(models.Model):
    title = models.CharField(max_length=100, default="Our Story")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True, help_text="Paste full YouTube URL here")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        # Check if BOTH fields are filled
        if self.video_file and self.youtube_url:
            raise ValidationError("You cannot provide both a Video File and a YouTube URL. Please clear one before adding the other.")
        
        # (Optional) Check if NEITHER is filled but it is set to active
        if self.is_active and not self.video_file and not self.youtube_url:
             raise ValidationError("Please provide either a Video File or a YouTube URL to make this section active.")

    def save(self, *args, **kwargs):
        self.full_clean() # Forces the clean method to run before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
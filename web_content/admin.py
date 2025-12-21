# web_content/admin.py
from django.contrib import admin
from .models import HeroSlide, PromoMessage, VideoSection

# This makes the "Hero Slide" table visible in Admin
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')

# This makes the "Promo Message" table visible in Admin
@admin.register(PromoMessage)
class PromoMessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'order', 'is_active')

# This makes the "Video Section" table visible in Admin
@admin.register(VideoSection)
class VideoSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
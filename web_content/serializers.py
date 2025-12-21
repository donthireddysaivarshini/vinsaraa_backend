from rest_framework import serializers
from .models import HeroSlide, PromoMessage, VideoSection

class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = ['id', 'title', 'subtitle', 'image', 'order']

class PromoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoMessage
        fields = ['id', 'text', 'order']

class VideoSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSection
        # Add 'youtube_url' to this list
        fields = ['id', 'title', 'video_file', 'youtube_url', 'description']
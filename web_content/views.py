from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import HeroSlide, PromoMessage, VideoSection
from .serializers import HeroSlideSerializer, PromoMessageSerializer, VideoSectionSerializer

class WebContentViewSet(viewsets.ViewSet):
    """
    A combined viewset to get all homepage content in one go, 
    or you can access them individually if preferred.
    """

    @action(detail=False, methods=['get'])
    def hero_slides(self, request):
        slides = HeroSlide.objects.filter(is_active=True).order_by('order')
        serializer = HeroSlideSerializer(slides, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def promos(self, request):
        promos = PromoMessage.objects.filter(is_active=True).order_by('order')
        serializer = PromoMessageSerializer(promos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def video(self, request):
        # Get the first active video configuration
        video = VideoSection.objects.filter(is_active=True).first()
        if video:
            serializer = VideoSectionSerializer(video, context={'request': request})
            return Response(serializer.data)
        return Response({})
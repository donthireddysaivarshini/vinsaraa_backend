import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from web_content.models import HeroSlide, PromoMessage, VideoSection

class Command(BaseCommand):
    help = 'Populates the website with default content and images'

    def handle(self, *args, **kwargs):
        self.stdout.write("Populating website content...")

        # --- 1. POPULATE PROMO MESSAGES ---
        promos = [
            "10% OFF YOUR FIRST PURCHASE! CODE: VINSARANEW",
            "MADE WITH LOVE AND PURE FABRICS",
            "FREE SHIPPING ON ORDERS OVER $100",
            "HANDCRAFTED TRADITIONAL ARTISTRY",
            "NEW COLLECTION JUST ARRIVED"
        ]

        if not PromoMessage.objects.exists():
            for index, text in enumerate(promos):
                PromoMessage.objects.create(text=text, order=index)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(promos)} promo messages."))
        else:
            self.stdout.write("ℹ️ Promo messages already exist.")

        # --- 2. POPULATE HERO SLIDES WITH IMAGES ---
        slides_data = [
            {
                "file": "hero-1.jpg",
                "title": "THE ART OF SHIBORI",
                "subtitle": "Hand-dyed pieces that carry the beauty of tradition in every fold"
            },
            {
                "file": "hero-2.jpg",
                "title": "TIMELESS ELEGANCE",
                "subtitle": "Discover our collection of handcrafted ethnic wear"
            },
            {
                "file": "hero-3.jpg",
                "title": "CONTEMPORARY TRADITIONS",
                "subtitle": "Where modern design meets traditional craftsmanship"
            },
            {
                "file": "hero-4.jpg",
                "title": "ARTISAN CREATIONS",
                "subtitle": "Each piece tells a story of heritage and skill"
            },
            {
                "file": "hero-5.jpg",
                "title": "LUXURY REDEFINED",
                "subtitle": "Experience the finest in traditional textiles"
            }
        ]

        # Path to where you pasted the images
        ASSET_DIR = os.path.join(settings.BASE_DIR, 'web_content', 'setup_assets')

        if not HeroSlide.objects.exists():
            created_count = 0
            for index, slide in enumerate(slides_data):
                image_path = os.path.join(ASSET_DIR, slide["file"])
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        hero_obj = HeroSlide(
                            title=slide["title"],
                            subtitle=slide["subtitle"],
                            order=index
                        )
                        # Save image to the model field
                        hero_obj.image.save(slide["file"], File(img_file), save=True)
                        created_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Image not found: {image_path}"))
            
            self.stdout.write(self.style.SUCCESS(f"✅ Created {created_count} hero slides with images."))
        else:
            self.stdout.write("ℹ️ Hero slides already exist.")

        # --- 3. POPULATE VIDEO SECTION ---
        if not VideoSection.objects.exists():
            VideoSection.objects.create(
                title="Main Homepage Video",
                # You can change this default URL to your specific video file if needed
                video_url="https://vinsaraa-assets.s3.ap-south-1.amazonaws.com/videos/home-banner.mp4"
            )
            self.stdout.write(self.style.SUCCESS("✅ Created default video section."))
        else:
            self.stdout.write("ℹ️ Video section already exists.")
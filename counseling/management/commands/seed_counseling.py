from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from counseling.models import PsychiatristProfile, AvailabilitySlot

class Command(BaseCommand):
    help = "Create a demo verified female psychiatrist and a few availability slots"

    def handle(self, *args, **options):
        # Create or get demo counselor user
        user, _ = User.objects.get_or_create(
            username="demo_counselor",
            defaults={"email": "demo.counselor@example.com"}
        )
        if not user.has_usable_password():
            user.set_password("demo1234")
            user.save()

        profile, created = PsychiatristProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": "Dr. Demo Counselor",
                "license_no": "DEMO-0001",
                "specialization": "Trauma & PTSD",
                "languages": "English, Hindi",
                "years_experience": 7,
                "bio": "Compassionate support for trauma recovery.",
                "is_verified": True,
                "is_female": True,
            }
        )

        # Create three upcoming 30-min slots
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        created_slots = 0
        for i in range(1, 4):
            start = now + timedelta(hours=i)
            end = start + timedelta(minutes=30)
            slot, made = AvailabilitySlot.objects.get_or_create(
                psychiatrist=profile,
                start=start,
                end=end,
            )
            if made:
                created_slots += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded counselor '{profile.full_name}' with {created_slots} new slot(s). Username: demo_counselor / Password: demo1234"
        ))

import uuid
from django.db import models
from django.conf import settings


class Hobby(models.Model):
    """Stores user interests/hobbies (e.g., Billiards, Coffee, Hiking, Photography)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True, help_text="FontAwesome or Tabler icon class name")
    description = models.TextField(blank=True)

    class Meta:
        db_table = "explore_hobbies"
        verbose_name_plural = "Hobbies"

    def __str__(self):
        return self.name


class Category(models.Model):
    """Categorizes listings (e.g., Food & Dining, Accommodations, Tourist Attraction, Transport Hub)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "explore_categories"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Place(models.Model):
    """Main model for venues, spots, and businesses in Kabankalan City."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_places",
        help_text="Tourism admin or verified business owner"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="places")
    hobbies = models.ManyToManyField(Hobby, related_name="places", blank=True)
    
    # Core Information
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed description of the venue/attraction")
    address = models.CharField(max_length=255, default="Kabankalan City, Negros Occidental")
    barangay = models.CharField(max_length=100, blank=True, help_text="e.g., Barangay 1, Tapi, Magballo")
    
    # Map & Spatial Data
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Details & Contact
    operating_hours = models.CharField(max_length=255, help_text="e.g., Mon-Sun: 8:00 AM - 10:00 PM")
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    facebook_page = models.URLField(blank=True)
    
    # AI Search & Recommendation Data
    ai_keywords = models.TextField(blank=True, help_text="Comma-separated AI tags or semantic keywords for search matching")
    
    # Meta Status
    is_verified = models.BooleanField(default=False, help_text="Verified by Kabankalan Tourism Office")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "explore_places"
        ordering = ["title"]

    def __str__(self):
        return self.title


class PlacePhoto(models.Model):
    """Stores multiple images for each place."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="places_photos/")
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "explore_place_photos"


class Review(models.Model):
    """User reviews and ratings for places."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_reviews"
        ordering = ["-created_at"]


class CityInformation(models.Model):
    """City-wide information (Events, Transport Guides, General Info)."""
    INFO_TYPES = (
        ("event", "Event / Festival"),
        ("transport", "Transport Guide"),
        ("general", "General Info / Guideline"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    info_type = models.CharField(max_length=20, choices=INFO_TYPES, default="general")
    content = models.TextField()
    event_date = models.DateField(null=True, blank=True, help_text="Applicable for events (e.g., Sinulog de Kabankalan)")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_city_information"
        verbose_name_plural = "City Information"


class Itinerary(models.Model):
    """AI-suggested or user-saved itineraries combining multiple places."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="itineraries")
    title = models.CharField(max_length=255, help_text="e.g., One Day Billiards & Coffee Trip")
    generated_by_ai = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_itineraries"


class ItineraryItem(models.Model):
    """Individual stops in a planned itinerary."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="items")
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True, help_text="e.g., Afternoon snack or evening activity")

    class Meta:
        db_table = "explore_itinerary_items"
        ordering = ["order"]
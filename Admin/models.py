from django.db import models
from django.core.exceptions import ValidationError
from Guest.models import *

# Create your models here.
class tbl_admin(models.Model):
    admin_name=models.CharField(max_length=20)
    admin_email=models.CharField(max_length=30)
    admin_password=models.CharField(max_length=30)

    class Meta:
        db_table = 'tbl_admin'  # <-- forces table name


# class tbl_pincode(models.Model):
#     pincode = models.CharField(max_length=10, unique=True)

#     class Meta:
#         db_table = 'tbl_pincode'

#     def __str__(self):
#         return self.pincode


# class tbl_place(models.Model):
#     place_name = models.CharField(max_length=100)
#     pincode = models.ForeignKey(tbl_pincode, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'tbl_place'

    
# class tbl_house(models.Model):
#     STATUS_CHOICES = [
#         ('1', 'Available'),
#         ('0', 'Not Available'),
#     ]

#     house_title = models.CharField(max_length=80)
#     house_description = models.CharField(max_length=300)
#     house_category = models.CharField(max_length=80)
#     house_price = models.IntegerField()
#     house_location = models.CharField(max_length=50)
#     house_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='1')
#     house_address  = models.TextField()
#     house_pincode  = models.ForeignKey(tbl_pincode, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'tbl_house'


# class tbl_room(models.Model):
#     STATUS_CHOICES = [
#         ('1', 'Available'),
#         ('0', 'Not Available'),
#     ]
#     room_title=models.CharField(max_length=80)
#     room_description=models.CharField(max_length=300)
#     room_category=models.CharField(max_length=80)
#     room_rate=models.IntegerField()
#     room_location=models.CharField(max_length=80)
#     room_status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='1')
#     room_address=models.TextField()
#     room_pincode=models.ForeignKey(tbl_pincode,on_delete=models.CASCADE)

#     class Meta:
#         db_table='tbl_room'

'''class tbl_gallery(models.Model):
    house = models.ForeignKey(tbl_house,on_delete=models.CASCADE,related_name="images",null=True,blank=True
    )

    room = models.ForeignKey(tbl_room,on_delete=models.CASCADE, related_name="images",null=True,blank=True
    )
    image = models.FileField(upload_to="HouseDocs/")

    class Meta:
        db_table = "tbl_gallery"'''




class tbl_property(models.Model):
    title = models.CharField(max_length=100)
    address = models.TextField()
    postcode = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=8, decimal_places=2)
    
    RENT_TYPE_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    rent_type = models.CharField(max_length=10, choices=RENT_TYPE_CHOICES)
    
    bills_included = models.BooleanField(default=False)
    available_from = models.DateField()
    available_to = models.DateField()
    min_stay = models.CharField(max_length=50)
    max_stay = models.CharField(max_length=50)
    days_available = models.CharField(max_length=100)
    short_term = models.BooleanField(default=False)

    PROPERTY_TYPE_CHOICES = [
        ('room_in_existing', 'Room in existing share'),
        ('studio', 'Studio/2 bed flats'),
        ('whole_property', 'Whole property'),
    ]
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)

    ROOM_SIZE_CHOICES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
    ]
    room_size = models.CharField(max_length=10, choices=ROOM_SIZE_CHOICES)

    ROOM_FURNISHED_CHOICES = [
        ('furnished', 'Furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    room_furnishing = models.CharField(max_length=15, choices=ROOM_FURNISHED_CHOICES)

    is_en_suite = models.BooleanField(default=False)
    no_of_rooms = models.PositiveIntegerField()

    SHARE_OCCUPATION_CHOICES = [
        ('professional', 'Professional'),
        ('student', 'Student'),
    ]
    share_occupation = models.CharField(max_length=20, choices=SHARE_OCCUPATION_CHOICES)

    ROOM_FOR_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('couple', 'Couple'),
    ]
    room_for = models.CharField(max_length=10, choices=ROOM_FOR_CHOICES)

    SHARE_GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('mixed', 'Mixed'),
    ]
    share_gender = models.CharField(max_length=10, choices=SHARE_GENDER_CHOICES)

    occupant_age = models.CharField(max_length=50)

    HOUSEHOLD_OPTIONS = [
        ('lgbt', 'LGBT'),
        ('veg', 'Vegetarian/Vegan preferred'),
    ]
    household_option = models.CharField(max_length=30, choices=HOUSEHOLD_OPTIONS)

    no_of_bedrooms = models.PositiveIntegerField()

    # Multi-select could be done using a TextField with comma-separated values or a ManyToManyField in a more advanced setup
    property_preference = models.CharField(max_length=100)

    PROPERTY_HABIT_CHOICES = [
        ('smoking', 'Smoking'),
        ('non_smoking', 'Non-smoking'),
    ]
    property_habit = models.CharField(max_length=20, choices=PROPERTY_HABIT_CHOICES)

    room_suitable_for = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
    ]
    current_status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        db_table = 'tbl_property'

    def _str_(self):
        return self.title


class tbl_gallery(models.Model):
    property = models.ForeignKey(tbl_property, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.FileField(upload_to='room_images/')

    class Meta:
        db_table = 'tbl_gallery'

    def _str_(self):
        return f"Image for {self.property.title}"
    


class tbl_message(models.Model):
    sender         = models.ForeignKey(tbl_newuser, on_delete=models.CASCADE,
                                       related_name='sent_messages',
                                       null=True, blank=True)
    is_from_admin  = models.BooleanField(default=False) 
    property       =models.ForeignKey (tbl_property, on_delete=models.SET_NULL,
                                        null=True, blank=True)   # True → admin
    '''house          = models.ForeignKey(tbl_house, on_delete=models.SET_NULL,
                                       null=True, blank=True)
    room           = models.ForeignKey(tbl_room,  on_delete=models.SET_NULL,
                                       null=True, blank=True)'''
    subject        = models.CharField(max_length=200, null=True, blank=True)
    body           = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True)
    is_read        = models.BooleanField(default=False)

    
    STATUS_CHOICES = [
        ('pending',  'Pending (Admin has NOT replied)'),
        ('replied',  'Replied (Admin has answered)'),
    ]
    status         = models.CharField(max_length=10,
                                      choices=STATUS_CHOICES,
                                      default='pending')

    class Meta:
        db_table  = 'tbl_message'
        ordering  = ['created_at']


class tbl_favourite(models.Model):
    user = models.ForeignKey(tbl_newuser, on_delete=models.CASCADE)
    property = models.ForeignKey(tbl_property, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.name} - {self.property.title}"

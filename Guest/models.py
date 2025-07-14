from django.db import models

class  tbl_newuser(models.Model):
    user_firstname=models.CharField(max_length=20)
    user_lastname=models.CharField(max_length=20)
    user_email=models.EmailField(unique=True) 
    user_phone = models.CharField(max_length=15, default='+0000000000') # Use EmailField for email validation
    user_password=models.CharField(max_length=150)
    verify_status = models.IntegerField(default=0)
    verification_time = models.DateTimeField(blank=True, null=True)
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user_gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES, # Choices are still good for model-level validation
    )

    class Meta:
        db_table = 'tbl_newuser' # <-- forces table name

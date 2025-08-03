from django.db import models
from Guest.models import*
from Admin.models import*
# Create your models here.
class tbl_review(models.Model):
    review=models.CharField(max_length=400)
    user=models.ForeignKey(tbl_newuser,on_delete=models.CASCADE)
    property=models.ForeignKey(tbl_property,on_delete=models.CASCADE)

    class Meta:
        db_table='tbl_review'
    
class tbl_complaint(models.Model):
    title=models.CharField(max_length=50)
    description=models.CharField(max_length=100)
    user=models.ForeignKey(tbl_newuser,on_delete=models.CASCADE)
    date=models.DateField(auto_now_add=True)
    status=models.IntegerField(default=0)
    reply=models.CharField(max_length=100)


class tbl_feedback(models.Model):
    user = models.ForeignKey(tbl_newuser, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='tbl_feedback'
    
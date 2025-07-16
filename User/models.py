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
    

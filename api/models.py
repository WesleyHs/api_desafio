from django.db import models

class bancoApi(models.Model):
    user_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=250)
    orders = models.JSONField()
        
    class Meta: 
        db_table = 'api'
from django.db import models

class BaseModel(models.Model):
    class Meta:
        app_label = 'web_shop'
        abstract =  True

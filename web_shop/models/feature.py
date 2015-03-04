from django.db import models
from common import BaseModel
from django.utils.translation import ugettext_lazy as _


class Feature(BaseModel):
    name = models.CharField(_("Name"), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = _('Feature')#'Caracteristica'
        verbose_name_plural = _('Features')#'Caracteristicas'
        ordering = ['name']

class FeatureSet(BaseModel):
    name = models.CharField(max_length=200)
    features = models.ManyToManyField(Feature)

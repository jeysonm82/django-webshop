from django.db import models
from common import BaseModel
from django.utils.translation import ugettext_lazy as _


class Attribute(BaseModel):
    """ A Product Attribute. Attribute is a product's property with various discrete values (AttributeValue) """
    name = models.CharField(_("Name"), max_length=100, unique=True)
    attr_type = models.IntegerField(_("Type"), choices = ((1, "Normal"), (2, "Color")), default=1)

    def __unicode__(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')

class AttributeValue(BaseModel):
    """ An specific value for a Product Attribute """
    value = models.CharField(_("Value"), max_length=100)
    color_extra = models.CharField("Color Hex", max_length=30, default='', blank=True) # Used only for a color attrib
    attribute = models.ForeignKey(Attribute)

    def __unicode__(self):
        return "(%s - %s)"%(self.attribute.name, self.value)

    class Meta(BaseModel.Meta):
        verbose_name = _('Attribute Value')
        verbose_name_plural = _('Attribute Values')
        ordering = ['attribute']

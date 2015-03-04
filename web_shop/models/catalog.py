from django.db import models
from saleor.product.models import Category
from common import BaseModel
from django_images.models import Image
from django.utils.html import mark_safe


class CategoryImage(BaseModel, Image):
    category = models.ForeignKey(Category, related_name='images')

    class Meta(BaseModel.Meta):
        verbose_name = "Imagen"
        verbose_name_plural = "Imagen"

    def get_by_size(self, size):
        if size == 'admin':
            size = 'admin_cat'
        t = [x for x in self.thumbnail_set.all() if x.size == size]
        if len(t):
            return t[0]
        else: 
            return self.thumbnail_set.get(size=size)

    def __unicode__(self):
        html = '<img src="%s" alt=""/>' % (
            self.get_absolute_url('admin'),)
        return mark_safe(html)

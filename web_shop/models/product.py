
#from saleor.product.models import Product, PhysicalProduct, StockedProduct
from saleor.product import models as saleor_models
from django_prices.models import PriceField
from django.conf import settings
from django.db import models
from attributes import AttributeValue
from common import BaseModel
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from collections import OrderedDict
import operator
from web_shop.models.feature import Feature
from django.utils.text import slugify

# Most saleor product models are extended by inheritance.

class Category(saleor_models.Category):
    order = models.SmallIntegerField("Order", default=0)

    class MPTTMeta:
        order_insertion_by = ['order']


class ProductImage(BaseModel, saleor_models.ProductImage):

    def get_by_size(self, size):
        t = [x for x in self.thumbnail_set.all() if x.size == size]
        if len(t):
            return t[0]
        else: 
            return self.thumbnail_set.get(size=size)

    def __str__(self):
        html = '<img src="%s" alt="">' % (
            self.get_absolute_url('admin'),)
        #html = 'im'
        return mark_safe(html)

    class Meta(BaseModel.Meta):
        proxy = True
        ordering = ['id']


class ProductManager(models.Manager):

    """ Product manager for product for table level operations """

    def get_products_from_cat(self, category):
        """ Gets products from category and child categories """
        if category is None:
            return self.get_queryset().prefetch_related('images', 'images__thumbnail_set')
        cats = [x.pk for x in [category] + list(category.get_children())]
        return self.get_queryset().filter(enabled=True,category__pk__in=cats).prefetch_related('images')
    
    def recommended(self, category=None, num=3):
        return self.get_products_from_cat(category).order_by('?')[:num]

    def featured(self, category=None):
        return self.get_products_from_cat(category).filter(featured=True)#.order_by('?')


class Product(BaseModel, saleor_models.StockedProduct, saleor_models.Product):
    objects = ProductManager()
    price = PriceField(
        _("Price"), currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=4, default=0.0)
    product_type = models.IntegerField(
        _("Product type"), choices=((0, "Physical"), (1, "Digital")), default=0)
    enabled = models.BooleanField(_("Enabled"), default=True)
    featured = models.BooleanField(_("Featured"), default=False) # Destacado
    features = models.ManyToManyField(Feature, through='ProductFeatureValue')
    order = models.SmallIntegerField(_("Order"), default=10)

    class Meta(BaseModel.Meta):
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['order']

    def get_slug(self):
        return slugify(self.name)

    def get_attributes(self, variants_qset=None):
        """ Returns unique list of attributesvalues for this product extracted from variants and a dictionary that relates attributevalues with product_variants"""
        attrs_variant_map = {}
        attrs_values = []
        # Iterate over  all variants and get attributevalues
        for p in self.variants.all():
            aname = []
            for a in p.attributes.all():
                aname.append(str(a))
                tuple2add = (a, a.attribute.pk, a.pk)
                if tuple2add not in attrs_values:
                    attrs_values.append(tuple2add)
            attr_combo = '+'.join(aname)
            attrs_variant_map[attr_combo] = p.pk

        # Sort attribute values
        # This line sorts attributevalues by attribute.pk and attributevalue.pk
        attrs_values = [x[0]
                        for x in sorted(attrs_values, key=operator.itemgetter(1, 2))]
        # Transform attrs_values to look like this:
        # attr_values = {Attribute_1: (attr_value_1, attr_value_2), Attribute_2: (attr_value_1, attr_value_2), ...}
        # Order is important that's why we sorted attrs_values and use and
        # OrderectDict below.
        hdict = OrderedDict()
        for value in attrs_values:
            hdict.setdefault(value.attribute, []).append(value)
        attributes = hdict

        return attributes, attrs_variant_map
    
    def get_features(self):
        return ProductFeatureValue.objects.filter(product=self).select_related('feature')

class ProductVariant(BaseModel, saleor_models.ProductVariant, saleor_models.StockedProduct):
    product = models.ForeignKey(Product, related_name='variants')
    custom_price = PriceField(
        _("Custom price"), currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=4)
    attributes = models.ManyToManyField(AttributeValue)
    images = models.ManyToManyField(
        saleor_models.ProductImage, blank=True, verbose_name=_('Images'))

    def __unicode__(self):
        return mark_safe("%s <small>%s</small>"%(self.product, ', '.join([str(x) for x in  self.attributes.all()])))
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')


class ProductFeatureValue(BaseModel):
    product = models.ForeignKey(Product)
    feature = models.ForeignKey(Feature, verbose_name=_("Feature"))
    value = models.CharField(_("Value"), max_length=200)
    order = models.SmallIntegerField(_("Order"), default=0)

    def __unicode__(self):
        return "%s: %s"%(self.feature.name, self.value)

    class Meta(BaseModel.Meta):
        verbose_name = _('Product Feature') #'Caracteristica de producto'
        verbose_name_plural = _('Product Features') #'Caracteristicas de productos'


class TestModel(BaseModel):
    name = models.CharField('campo', max_length=200)

from django.contrib import admin
from saleor.product.models import Bag, Shirt, Color, FixedProductDiscount
#from saleor.product.models import Category
from models import ProductVariant
from collections import OrderedDict
import json
from models import Attribute, AttributeValue, Product
from django.utils.safestring import mark_safe
from django.db import models
from widgets import MultiAttributeValueSelect
from forms import ProductVariantForm, ProductForm, ProductVariantFormInline
from mptt.admin import MPTTModelAdmin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from models import Feature, FeatureSet, ProductFeatureValue, CategoryImage, Category, ProductImage

from django_admin_bootstrapped.admin.models import TabPanelMixin # django_bootstraped with tabs

class ProductVariantAdmin(admin.ModelAdmin):

    """ Admin for ProductVariant . It's used only to admin pvariant images """
    form = ProductVariantForm
    fields = ('images',)

    # Override some views to disable listing and adding new entries
    def add_view(request, form_url='', extra_context=None):
        return redirect("/admin")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ overriding change view to not redirect to change_list_view """
        req = super(ProductVariantAdmin, self).change_view(
            request, object_id, form_url, extra_context)
        if request.method == 'POST':
            # TODO redir and close popup instead?
            # redir to same
            return redirect(reverse('admin:web_shop_productvariant_change', args=(object_id,)) + '?_popup=1')
        return req

    def changelist_view(request, extra_context=None):
        return redirect("/admin")

    def queryset(self, request):
        # We add some select and prefetch related to optimize db queries
        qs = super(ProductVariantAdmin, self).queryset(request).select_related('product').prefetch_related(
            'attributes', 'images__productimage', 'images__productimage__thumbnail_set')
        return qs

    def get_form(self, request, obj=None, **kwargs):
        self.obj = obj # Grab instance being edited
        return super(ProductVariantAdmin, self).get_form(
            request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Add custom queryset to images field to show only images from parent
        # product
        if db_field.name == 'images':
            kwargs['queryset'] = ProductImage.objects.select_related(
                'image').prefetch_related('thumbnail_set').all().filter(product=self.obj.product) # prefecth thumbnails
        formfield = super(ProductVariantAdmin, self).formfield_for_manytomany(
            db_field, **kwargs)
        return formfield


class ProductVariantInline(admin.StackedInline):

    """ A product variant is identified by an unique combination of AttributeValues.
    Constraints:
    1. A productvariant must have at least one AttributeValue. 
    2. A productvariant can only have one AttrValue for each Attribue (ej: One color, One size, etc.).
    3. A productvariant's set  of AttributeValues must be unique among the sets of other
    productvariants of the same product. #TODO
    """

    model = ProductVariant
    form = ProductVariantFormInline
    fields = ('sku', 'attributes', 'custom_price','stock', 'admin_images')
    readonly_fields = ('admin_images',)

    def __init__(self, *args, **kwargs):
        super(ProductVariantInline, self).__init__(*args, **kwargs)

    def admin_images(self, obj=None):
        """ Custom field for the inline tht shows a link to ProductVariant
        Admin to change images """
        if obj.pk:
            im_list = ""
            for im in obj.images.all():
                im_list += "<li>%s</li>"%(str(im))
            return mark_safe("<a target='_blank' onclick='return showAddAnotherPopup(this);' href='%s?_popup=1'>%s</a> <ul class='listim'>%s</ul>" % (reverse('admin:web_shop_productvariant_change', args=(obj.pk,)), "Administrar Im&aacute;genes", im_list))
        return ''
    admin_images.short_description = _('Admin Images')

    def queryset(self, request):
        qs = super(ProductVariantInline, self).queryset(
            request).prefetch_related('attributes', 'images', 'product', 'images__thumbnail_set')
        return qs


class ProductImagesInline(admin.TabularInline):
    """ Inline for Product's images """
    model = ProductImage
    extra = 1
    max_num = 1

    def queryset(self, request):
        qs = super(ProductImagesInline, self).queryset(request).prefetch_related(
            'thumbnail_set')  # .select_related('attributes__attributevalue')
        return qs


class ProductFeatureInline(admin.TabularInline):
    """ Inline for Product's features """
    model = ProductFeatureValue
    fields = ('feature', 'value')



class ProductAdmin(TabPanelMixin, admin.ModelAdmin):
    """ Product  admin. It has an inline for productvariants """
    list_display = ('name', 'category', 'featured')
    form = ProductForm
    fieldsets = (
        (None, {
            'fields': ('name', 'description','featured', 'order', 'price'),
        }),
        (_("Category") +'', {'fields': ('category',)}),

    )
    inlines = [ProductImagesInline, ProductFeatureInline, ProductVariantInline]

    tabs = (("General", (None, _("Category")+'')), (
        _("Images")+'', (ProductImagesInline,)), (_("Features")+'', (ProductFeatureInline,)))


class AttributeValueInline(admin.TabularInline):
    """ Inline for Attribute's Values """
    model = AttributeValue

    fields = ['value', 'color_extra', 'show_color']
    readonly_fields = ('show_color',)

    def __init__(self, *args, **kwargs):
        super(AttributeValueInline, self).__init__(*args, **kwargs)

    def show_color(self, obj):
        """ Custom field to show a color box """
        if obj.id is not None:
            return mark_safe("<div style='background: %s;width: 30px; height:30px; ' class='boxcolor'></div>" % (obj.color_extra))
        return ''

    @classmethod
    def show_colors(cls, value=True):
        if value:
            AttributeValueInline.fields = [
                'value', 'color_extra', 'show_color']
        else:
            AttributeValueInline.fields = ['value']


class AttributeAdmin(admin.ModelAdmin):
    """ Admin for attributes and its values """
    inlines = [AttributeValueInline]

    def __init__(self, *args, **kwargs):
        super(AttributeAdmin, self).__init__(*args, **kwargs)

    def get_inline_instances(self, request, obj=None):
        ''' Override to hide/show  color fields  according to attr_type '''
        AttributeValueInline.show_colors(
            obj is not None and obj.attr_type == 2)
        return super(AttributeAdmin, self).get_inline_instances(request, obj)


class FeatureAdmin(admin.ModelAdmin):
    model = Feature


class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 1
    max_entries = 1
    max_num = 1
    can_delete = False


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('tabbed_name', 'order')
    inlines = [CategoryImageInline]
    change_list_template = 'admin/change_list.html'

    def tabbed_name(self, obj):
        return 2 * '<i class="fa fa-minus "></i>' * obj.level + ' ' + obj.name
    tabbed_name.allow_tags = True
    tabbed_name.short_description = Category._meta.verbose_name


class WebShopAdminSite(admin.AdminSite):
    """ The web_shop admin site """
    site_title = 'Administrador de contenidos' #TODO didn't work
    site_header = 'Administrador de contenidos'
    #index_template = 'web_shop/admin/index.html'

webshop_admin = WebShopAdminSite('webshop')
# Register your models here.
webshop_admin.register(Product, ProductAdmin)
webshop_admin.register(Category, CategoryAdmin)
webshop_admin.register(ProductVariant, ProductVariantAdmin)
webshop_admin.register(Attribute, AttributeAdmin)
webshop_admin.register(Feature, FeatureAdmin)

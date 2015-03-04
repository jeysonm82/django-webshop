from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse
from web_shop.models import Product, ProductVariant
from saleor.product.models import Category
from saleor.cart.forms import AddToCartForm
from saleor.cart import Cart
from django import forms
import json
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

class ProductAddForm(AddToCartForm):
    """ Form in product_detail view used to add products to cart """
    variant = forms.ModelChoiceField(queryset=ProductVariant.objects.none(), required=False)
    
    def __init__(self, *args, **kwargs):
        product = kwargs['product']

        super(ProductAddForm, self).__init__(*args, **kwargs)
        self.fields['variant'].queryset = product.variants.all()
    
    def get_variant(self, cleaned_data):
        print "getting cleaned data"
        variant = cleaned_data['variant']
        if variant is None:
            variant = self.product
        return variant

class ProductDetail(DetailView):
    template_= "web_shop/product_detail.html"
    model = Product
    context_object_name = 'product'
    obj = None
    form = None

    def get_object(self, queryset=None):
        """ Caching object to reduce queries """
        if self.obj is None:
            self.obj = super(ProductDetail, self).get_object(queryset)
        return self.obj
    
    def get_form(self, data=None, cart=None):
       if self.form is None:
           self.form = ProductAddForm(product=self.get_object(),cart=cart, data=data)
       return self.form

    def post(self, request, *args, **kwargs):
        """ POST Request. Process Addtocart form """
        product = self.get_object()    
        cart = Cart.for_session_cart(request.cart, discounts=None)
        error = False
        try:
            form = self.get_form(data=request.POST, cart=cart)
            if form.is_valid():
                # Form valid
                form.save()
                msg = _('Successfully added product to cart.')
                messages.success(request, msg)

            else:
                error = True
                print "ERRORS ", form.errors
        except:
            error = True
        if error:
           msg = _('Error. Could not add product to cart.')
           messages.error(request, msg)

        if request.is_ajax():
            # Is ajax
            if error:
                return HttpResponse("ERROR")
            return HttpResponse("SUCCESS")
        return super(ProductDetail, self).get(request, *args, **kwargs)
    
    def get_queryset(self):
        p = super(ProductDetail, self).get_queryset().prefetch_related('images', 'variants', 'images__thumbnail_set', 'variants__attributes', 'variants__attributes__attribute')
        return p

    def get_context_data(self, **kwargs):
        print "getting context data product"
        context = super(ProductDetail, self).get_context_data(**kwargs)
        product = self.get_object()
        context['category'] = product.category
        context['category_list'] = Category.objects.all()
        attributes, attrs_variant = product.get_attributes()
        context['attributes'] = attributes
        context['attrs_variant'] = json.dumps(attrs_variant)
        context['form'] = self.get_form()
        context['recommended'] = Product.objects.recommended(product.category)
        return context

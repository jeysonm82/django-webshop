from django import forms
from models import ProductVariant, AttributeValue, Product
from mptt.forms import TreeNodeChoiceField
from saleor.product.models import Category, ProductImage
from django.utils.translation import ugettext_lazy as _

class ProductForm(forms.ModelForm):

    """ Form for Product """
    category = TreeNodeChoiceField(queryset=Category.objects.all(), label=_('Category'))

    class Meta:
        model = Product


class ProductVariantForm(forms.ModelForm):

    """ Form for Productvariant (image field only) """

    def __init__(self, *args, **kwargs):
        super(ProductVariantForm, self).__init__(*args, **kwargs)

        if 'images' in self.fields:
            self.fields['images'].widget.can_add_related = False
            self.fields['images'].cache_choices = True

    class Meta:
        model = ProductVariant
        fields = ('images',)
        # Custom widget for images
        widgets = {'images': forms.CheckboxSelectMultiple()}


class ProductVariantFormInline(ProductVariantForm):

    """ Form for productvariant (inline at productadmin """
    attributes = forms.ModelMultipleChoiceField(
        queryset=AttributeValue.objects.select_related('attribute').all(),
        widget=forms.SelectMultiple(attrs={'class': 'multiselect_attrs'}),
        label=_('Attributes'))

    def __init__(self, *args, **kwargs):
        super(ProductVariantForm, self).__init__(*args, **kwargs)
        self.reformat_attrvalue_choices()

    def reformat_attrvalue_choices(self):
        '''reformats self.fields['attributes'].choices to generate a select with optgroup with a group for each distinct Attribute related to AttributeValues from the queryset '''

        last_cat = None
        subchoices = []
        choices = []
        for a in self.fields['attributes'].queryset:
            aname = a.attribute.name
            if last_cat != aname:
                if last_cat is not None:
                    choices.append([last_cat, subchoices])
                subchoices = []
                last_cat = aname
            subchoices.append([a.pk, a])

        choices.append([last_cat, subchoices])
        self.fields['attributes'].choices = choices

    class Meta:
        model = ProductVariant
        fields = ('sku', 'attributes', 'custom_price')
        # Custom widget for images
        widgets = {'images': forms.CheckboxSelectMultiple()}

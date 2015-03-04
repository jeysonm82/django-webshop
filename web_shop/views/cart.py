from django.views.generic import TemplateView
from satchless.item import Partitioner
from saleor.cart import Cart
from saleor.cart.forms import ReplaceCartLineFormSet
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

class CartView(TemplateView):
    template_name = 'web_shop/cart.html'
    cart, formset = None, None
    
    def get(self, request, *args, **kwargs):

        return super(CartView, self).get(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        request = self.request
        cart = Cart.for_session_cart(request.cart, discounts=None)
        formset = ReplaceCartLineFormSet( request.POST or None,
                                     cart=cart)

        cart_partitioner = Partitioner(cart)
        context['cart'] = cart_partitioner
        context['formset'] = formset
        context['base_template'] = 'base.html'
        if 'popup' in request.GET:
            context['base_template'] = 'base_popup.html'
            context['popup'] = True

        return context


    def post(self, request, *args, **kwargs):
        cart = Cart.for_session_cart(request.cart, discounts=None)

        try:
            formset = ReplaceCartLineFormSet(request.POST or None,
                                         cart=cart)
            if formset.is_valid():
                msg = _('Successfully updated product quantities.')
                messages.success(request, msg)
                formset.save()
            else:
                msg = _('Error. Could not updated product quantities.')
                messages.error(request, msg)
        except Exception, e:
            msg = _('Error. Could not update product quantities.')
            print "Error", e
            messages.error(request, msg)
               
        self.cart = cart
        self.formset = formset

        if 'popup' in self.request.GET:
            response =  redirect("view_cart")
            response['Location'] += '?popup=1'
            return response
        else:
            return redirect("view_cart")
        #return super(CartView, self).get(request, *args, **kwargs)

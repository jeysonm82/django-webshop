from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from views import CatalogView, ProductDetail, CartView

urlpatterns = patterns('',

    url(r'images/', include('django_images.urls')),
    url(r'product/(?P<pk>[0-9]{1,5})/(?P<slug>[-_\w]+)', ProductDetail.as_view(), name='product_detail'),
    url(r'(?P<cat_id>[0-9]{1,5})/(?P<slug>[-_\w]+)', CatalogView.as_view(), name='catalog'),
    url(r'^$', CatalogView.as_view(), name='catalog-root'),
    url(r'cart', CartView.as_view(), name='view_cart'),
    )

from saleor import cart
from saleor.product.models import Product

class Cart(cart.Cart):

    @classmethod
    def for_session_cart(cls, session_cart, discounts=None):
        cart = Cart(session_cart, discounts=discounts)
        product_ids = [item.data['product_id'] for item in session_cart]
        products = Product.objects.filter(id__in=product_ids).prefetch_related('variants', 'variants__attributes', 'variants__attributes__attribute', 'variants__images__thumbnail_set')
        products = products.select_subclasses()
        product_map = dict((p.id, (p, list(p.variants.all()))) for p in products)
        for item in session_cart:
            try:
                product, variants = product_map[item.data['product_id']]
            except KeyError:
                # TODO: Provide error message
                continue
            else:
                variant = [x for x in variants if x.pk == item.data['variant_id']]
                # If product has no variant then register the product itself
                if not len(variant):
                    variant = product
                else:
                    variant = variant[0]

            quantity = item.quantity
            cart.add(variant, quantity=quantity, check_quantity=False,
                     skip_session_cart=True)
        return cart

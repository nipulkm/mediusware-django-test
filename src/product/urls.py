from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView, ListProductView, ProductView, UpdateProductView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', ListProductView.as_view(), name='list.product'),
    path('create-product/', ProductView.as_view(), name='create_product'),
    path('update-product-info/<int:id>/', CreateProductView.as_view(), name='update_product_info'),
    path('update-product/', UpdateProductView.as_view(), name='update_product'),
]

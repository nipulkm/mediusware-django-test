import datetime
from django.views import generic
from django.views.generic.list import ListView

from product.models import Product, Variant


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(ListView):
    paginate_by = 10
    template_name = 'products/list.html'

    def get_queryset(self, **kwargs):
        queryset = Product.objects.prefetch_related(
            'productvariantprice_set',
            'productvariantprice_set__product_variant_one',
            'productvariantprice_set__product_variant_two',
            'productvariantprice_set__product_variant_three'
        ).order_by('id')

        filter_datas = self.request.GET
        if filter_datas.get('title'):
            queryset = queryset.filter(title__icontains=filter_datas.get('title'))
        if filter_datas.get('price_from') and filter_datas.get('price_to'):
            queryset = queryset.filter(
                productvariantprice__price__gte=filter_datas.get('price_from'),
                productvariantprice__price__lte=filter_datas.get('price_to')
            )
        if filter_datas.get('date'):
            date = datetime.datetime.strptime(filter_datas.get('date'), "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__date=date)
        if filter_datas.get('variant'):
            queryset = queryset.filter(productvariant=filter_datas.get('variant'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variants'] = Variant.objects.prefetch_related('productvariant_set')
        return context
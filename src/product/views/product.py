import datetime
import json

from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.views.generic.list import ListView
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse

from product.models import Product, ProductVariant, ProductVariantPrice, Variant


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



class ProductView(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        # try:
        product = Product(
            title=data.get('title'), sku=data.get('sku'), description=data.get('description')
        )
        product.save()

        product_variant_data = []
        for item in data.get('product_variant', []):
            for tag in item.get('tags'):
                product_variant_data.append(ProductVariant(variant_title=tag, variant_id=item.get('option'), product=product))
        if len(product_variant_data):
            ProductVariant.objects.bulk_create(product_variant_data)

        product_variant_prices_data = []
        for item in data.get('product_variant_prices', []):
            product_variant_titles = item.get('title').split('/') if item.get('title') \
                else []
            product_variant_one = ProductVariant.objects.filter(variant_title=product_variant_titles[0]).first() if len(product_variant_titles) and ProductVariant.objects.filter(variant_title=product_variant_titles[0]).exists() else None
            product_variant_two = ProductVariant.objects.filter(variant_title=product_variant_titles[0]).first() if len(product_variant_titles) > 1 and ProductVariant.objects.filter(variant_title=product_variant_titles[1]).exists() else None
            product_variant_three = ProductVariant.objects.filter(variant_title=product_variant_titles[0]).first() if len(product_variant_titles) > 2 and ProductVariant.objects.filter(variant_title=product_variant_titles[2]).exists() else None
            product_variant_prices_data.append(ProductVariantPrice(
                product_variant_one=product_variant_one,
                product_variant_two=product_variant_two,
                product_variant_three=product_variant_three,
                price=item.get('price'),
                stock=item.get('stock'),
                product=product
            ))
        if len(product_variant_prices_data):
            ProductVariantPrice.objects.bulk_create(product_variant_prices_data)

        return JsonResponse({'message': 'Created!'})

        # except Exception as e:
        #     return JsonResponse({'error': str(e)})
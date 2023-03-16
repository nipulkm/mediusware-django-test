from django.contrib import admin
from django.apps import apps

depot_app_config = apps.get_app_config('product')
for model in depot_app_config.get_models():
    admin.site.register(model)
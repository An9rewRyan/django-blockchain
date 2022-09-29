from django.contrib import admin
from django.urls import path, re_path
from blockchain import views
from blockchain.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^get_chain$', views.get_chain, name="get_chain"),
    re_path('^create_block$', views.create_empty_block, name="create_block"),
    re_path('^mine_block$', views.mine_block, name="mine_block"),
    re_path('^is_valid$', views.is_valid, name="is_valid"),
]

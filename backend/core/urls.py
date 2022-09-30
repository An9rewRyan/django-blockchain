from django.contrib import admin
from django.urls import path, re_path
from blockchain import views
from blockchain.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^get_chain$', views.get_chain, name="get_chain"),
    re_path('^mine_block$', views.mine_block, name="mine_block"),
    re_path('^add_transaction$', views.add_transaction, name="add_transaction"),
    re_path('^is_valid$', views.is_valid, name="is_valid"),
    re_path('^connect_node$', views.connect_node, name="connect_node"), 
    re_path('^replace_chain$', views.replace_chain, name="replace_chain"), 

]

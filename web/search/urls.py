from django.urls import path

from . import views

app_name = 'search'

urlpatterns = [
    path('', views.connect_view, name='connect'),
    path('indices', views.indices_view, name='indices'),
    path('indices/create', views.create_index_view, name='create_index'),
    path('indices/<str:index_name>', views.index_info_view, name='index_info'),
    path('indices/<str:index_name>/delete', views.index_delete_view, name='index_delete'),
    path('indices/<str:index_name>/bulk', views.index_bulk_view, name='index_bulk'),
    path('indices/<str:index_name>/msearch', views.index_msearch_view, name='index_msearch'),
    path('indices/<str:index_name>/search', views.index_search_view, name='index_search'),
]

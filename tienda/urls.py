from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import catalogo, agregar_producto, editar_producto, pedir_personalizado


urlpatterns = [
    path('', catalogo, name='catalogo'),
    path('agregar/', agregar_producto, name='agregar_producto'),
    path('editar/<int:id>/', editar_producto, name='editar_producto'),
    path('personalizado/', pedir_personalizado, name='pedir_personalizado'),
    path('login/', LoginView.as_view(template_name='tienda/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='catalogo'), name='logout'),

]
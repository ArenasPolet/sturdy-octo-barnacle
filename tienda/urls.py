from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import catalogo, agregar_producto, editar_producto,cambiar_estado_venta, pedir_personalizado, ver_cotizaciones, panel_ventas,eliminar_producto, descontar_stock_rapido,detalle_producto





urlpatterns = [
    path('', catalogo, name='catalogo'),
    path('agregar/', agregar_producto, name='agregar_producto'),
    path('editar/<int:id>/', editar_producto, name='editar_producto'),
    path('eliminar-producto/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('personalizado/', pedir_personalizado, name='pedir_personalizado'),
    path('cambiar-estado-venta/<int:venta_id>/', cambiar_estado_venta, name='cambiar_estado_venta'),
    path('producto/<int:producto_id>/', detalle_producto, name='detalle_producto'),
    path('login/', LoginView.as_view(template_name='tienda/login.html'), name='login'),
    path('ventas/', panel_ventas, name='panel_ventas'),
    path('descontar-stock/<int:producto_id>/<str:talla>/', descontar_stock_rapido, name='descontar_stock_rapido'),
    path('cotizaciones/', ver_cotizaciones, name='ver_cotizaciones'),
    path('logout/', LogoutView.as_view(next_page='catalogo'), name='logout'),

]
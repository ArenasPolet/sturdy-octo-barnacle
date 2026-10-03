# ⚡ Store Poleras - E-commerce en Django

Una moderna tienda online para la venta de poleras, desarrollada con Python y Django. Incluye un sistema de gestión de inventario por tallas, un panel de administración integrado directamente en la interfaz de usuario, y conexión directa a WhatsApp para procesar pedidos y cotizar diseños personalizados.

## 🚀 Características Principales

* **Catálogo Moderno:** Interfaz responsiva en modo oscuro con tarjetas redondeadas y estilo flotante (Bootstrap 5).
* **Gestión de Stock por Tallas:** Control de inventario detallado (ej. S:5, M:2) que deshabilita automáticamente las opciones agotadas en la vista del cliente.
* **Pedidos por WhatsApp:** Generación de enlaces dinámicos que envían al vendedor el nombre del producto, la talla exacta seleccionada, el precio formateado y la foto.
* **Diseños Personalizados:** Formulario dedicado para que los clientes suban sus propias imágenes y soliciten estampados a medida, redirigiendo la imagen y los detalles vía WhatsApp.
* **Administración Front-end:** Sistema de login seguro que permite al administrador subir y editar productos directamente desde la página principal, sin utilizar el panel `/admin/` clásico de Django.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python, Django
* **Frontend:** HTML5, Bootstrap 5, JavaScript (Vanilla)
* **Base de Datos:** SQLite (Configuración por defecto)
* **Manejo de Imágenes:** Pillow

## ⚙️ Requisitos Previos

* Python 3.11+
* Git

## 📥 Instalación y Configuración Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/tienda-poleras.git](https://github.com/tu-usuario/tienda-poleras.git)
   cd tienda-poleras

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv

   # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate

3. **Instalar las dependencias:**
    ```bash
   pip install django pillow


4. **Aplicar las migraciones a la base de datos:**
    ```bash
   python manage.py makemigrations
   python manage.py migrate


5. **Crear un usuario administrador:**    
    ```bash
    python manage.py createsuperuser


6. **Ejecutar el servidor de desarrollo:**
    ```bash
   python manage.py runserver


## 📱 Uso del Sistema
Vista Cliente: Accede a http://127.0.0.1:8000/ para explorar el catálogo, elegir tallas y enviar pedidos.

Vista Administrador: Haz clic en "Iniciar Sesión (Admin)" en la barra de navegación e ingresa con tus credenciales de superusuario. Esto habilitará los botones ocultos para "➕ Subir Polera" y "✏️ Editar" en cada tarjeta del catálogo.

👩‍💻 Autor 
Polet Arenas
# API de Gestión de Inventarios

## Descripción
Esta API permite gestionar inventarios y realizar pedidos utilizando una arquitectura RESTful. Está implementada con **FastAPI**, usa **PostgreSQL** como base de datos, **SQLAlchemy** para la interacción con la base de datos, y **JWT** para la autenticación. La API proporciona funcionalidades como la gestión de productos, manejo de stock, procesamiento de pedidos y la generación de reportes básicos.

## Tecnologías Usadas
- **Python 3.9+**
- **FastAPI** para la creación de la API.
- **PostgreSQL** como sistema de base de datos.
- **SQLAlchemy** para la interacción con la base de datos.
- **Docker** para contenerizar la aplicación y facilitar su despliegue.
- **pytest** para pruebas automatizadas.
- **JWT (JSON Web Token)** para la autenticación.

---

## Instrucciones de Setup

#Clonar el repositorio

bash
git clone https://github.com/Hernandez-Javier/Python-FastAPI

# Navegar al directorio del proyecto

# Crear un entorno virtual
python -m venv .venv
source .venv/bin/activate  # Para Linux/MacOS
.venv\Scripts\activate     # Para Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar el archivo .env con las configuraciones necesarias

# Ejecutar migraciones
alembic upgrade head

# Levantar el servidor
uvicorn main:app --reload

-------------------------------------------------------------------------------
Documentación de la API
La API tiene los siguientes endpoints:

1. Gestión de Productos
GET /products
Obtiene todos los productos en el inventario.
Respuesta: Lista de productos con detalles.

POST /products
Crea un nuevo producto en el inventario.
Datos: { "nombre": "string", "precio": "float", "stock": "int" }
Respuesta: El producto creado.

GET /products/{id}
Obtiene un producto por su ID.
Parámetros: id (ID del producto).
Respuesta: Detalles del producto.

PUT /products/{id}
Actualiza los detalles de un producto.
Parámetros: id (ID del producto).
Datos: { "nombre": "string", "precio": "float", "stock": "int" }
Respuesta: El producto actualizado.

DELETE /products/{id}
Elimina un producto del inventario.
Parámetros: id (ID del producto).
Respuesta: Confirmación de eliminación.

2. Gestión de Órdenes
GET /orders
Descripción: Obtiene todas las órdenes realizadas.
Respuesta:Lista de ordenes

POST /orders
Descripción: Crea una nueva orden para un producto.
Datos:
{
  "status": "string",
  "total_amount": 0,
  "items": [
    {
      "product_id": 0,
      "quantity": 0,
      "price": 0
    }
  ]
}
Respuesta: Nueva orden

GET /orders/{id}
Descripción: Obtiene los detalles de una orden específica.
Parámetros: id (ID de la orden).
Respuesta:Muestra la orden con el id proporcionado


PUT /orders/{id}/status
Descripción: Actualiza el estado de una orden.
Parámetros: id (ID de la orden).
{
    "estado": "Completada"
}
Respuesta:Orden modificada

3. Reportes
GET /reports/low-stock
Descripción: Genera un reporte de stock bajos.
Respuesta:Lista de inventarios bajos


GET /reports/sales
Descripción: Genera un reporte de las órdenes realizadas en un rango de fechas.
Parámetros: fecha_inicio, fecha_fin (formato YYYY-MM-DD).
Respuesta:Muestra unlistado de productos, cantidad y montos en esa fecha


4. Gestión de Inventarios

GET /inventarios
Descripción: Obtiene todos los registros de inventarios.
Respuesta: Registros de entradas a inventario

GET /inventarios/{id}
Descripción: Obtiene los detalles de un registro de inventario específico.
Parámetros: id (ID del producto).
Respuesta:Muestra el stocl del producto deseado

PUT /inventarios/{id}
Descripción: Actualiza los detalles de un registro de inventario.
Parámetros: id (ID del producto).
Datos:
{
    "cantidad": 75,
    "ubicacion": "Bodega A"
}
Respuesta: Inventario modificado

****Autenticación y Seguridad****
POST /login
Obtiene un token JWT para autenticación.
Para efectos practicos se queman datos, estos datos se agregan al endpoint 
post /token para obtener un token de acceso

Datos: { "username": "admin", "password": "123456" }
Respuesta: { "access_token": "jwt_token" }
Estos datos se envían como body en el endpoint login para obtener un token
de acceso.
Para acceder a los demás endpoints, debes incluir el token en el encabezado
Authorization de la solicitud como Bearer {token}. O si se usa Swagger se debe
agregar en authorization


----------------------------------------------------------------------------

Decisiones de Diseño
Arquitectura
La aplicación sigue una arquitectura modular para una mejor escalabilidad y 
mantenimiento. Está dividida en las siguientes capas:

Capa de presentación (FastAPI): Maneja las solicitudes HTTP y la validación de datos.
Capa de lógica de negocio: Controla el flujo de la aplicación y la validación 
interna.
Capa de persistencia (SQLAlchemy): Se encarga de la interacción con la base de datos.

Autenticación con JWT
Para garantizar la seguridad de la API, se ha implementado autenticación 
utilizando JWT. Los tokens son generados cuando el usuario inicia sesión y 
se deben incluir en el encabezado de las solicitudes.

Gestión de Errores
La API maneja errores de manera centralizada utilizando excepciones personalizadas 
para devolver respuestas significativas y comprensibles en caso de fallos. 
Esto facilita la detección de problemas para los usuarios de la API.
----------------------------------------------------------------------------

Mejoras Propuestas
A continuación, se detallan algunas mejoras que podrían implementarse:

Soporte para múltiples usuarios: Actualmente, la API no tiene un sistema de usuarios 
implementado. Sería útil agregar una funcionalidad de autenticación completa con 
roles y permisos.

Optimización de consultas: Las consultas a la base de datos podrían mejorarse 
utilizando índices y optimizando las relaciones entre tablas para mejorar el 
rendimiento en grandes volúmenes de datos.

Gestión avanzada de inventario: Implementar funcionalidades como la notificación 
de bajo stock, alertas por productos próximos a vencer, y la integración con 
sistemas externos de gestión de inventarios.
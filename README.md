# website Rostisería Sabores Caseros

## Descripción Técnica del Proyecto
Este repositorio aloja el código fuente de una solución **Full Stack** diseñada bajo una arquitectura de software desacoplada para la transformación digital de *Rostisería SC*.

El sistema integra una **API RESTful** de alto rendimiento desarrollada en **Python (FastAPI)** y una interfaz de usuario **Frontend** ligera basada en estándares web (HTML5/JS/Bootstrap). La persistencia de datos se gestiona en la nube mediante **MongoDB Atlas**, asegurando escalabilidad y alta disponibilidad. El proyecto prioriza la seguridad de la información (autenticación JWT, encriptación Bcrypt) y optimiza la experiencia de usuario mediante técnicas de renderizado dinámico y simulación de procesos transaccionales.

## Arquitectura e Implementación

El proyecto se estructura siguiendo patrones de diseño de software por capas, garantizando una estricta separación de responsabilidades entre la presentación, la lógica de negocio y el acceso a datos.

### Backend (API REST)
El núcleo lógico del sistema fue construido utilizando el framework **FastAPI**, seleccionado por su eficiencia en el manejo de concurrencia y tipado estático.

* **Validación de Datos y Esquemas:** Se implementó **Pydantic** para la definición rigurosa de modelos de datos (Productos, Pedidos, Usuarios). Esto asegura la integridad referencial y el rechazo automático de solicitudes malformadas (Error 422) antes de interactuar con la base de datos.
* **Seguridad Perimetral:** El sistema opera bajo un modelo *stateless* mediante autenticación por **Tokens JWT** (JSON Web Tokens). Las credenciales de usuario se almacenan utilizando algoritmos de hashing robustos (**Bcrypt**) y las variables sensibles se gestionan mediante entorno (`.env`).
* **Estandarización de Interfaz:** La API genera automáticamente su documentación bajo el estándar **OpenAPI**, facilitando la integración y el consumo de servicios.

### Frontend (Cliente Web)
La interfaz de usuario fue desarrollada bajo el paradigma *Mobile First*, utilizando **Bootstrap 5** y **Vanilla JavaScript (ES6+)** para minimizar la carga de recursos.

* **Arquitectura de Servicios:** Se abstrajo la comunicación HTTP en un módulo interno (`api_utils.js`). Este componente centraliza las peticiones `fetch`, la inyección de cabeceras de seguridad y la gestión del ciclo de vida del token de autenticación.
* **Gestión de Estado (State Management):** Se utiliza `LocalStorage` para la persistencia del carrito de compras y la sesión del usuario en el navegador, garantizando la continuidad de la experiencia ante recargas de página.
* **Optimización de Rendimiento:** Se implementaron algoritmos de paginación y filtrado en el cliente (*Client-Side Pagination*), reduciendo la latencia de red y la carga en el servidor durante la exploración del catálogo.

### Módulo de Pagos (Sandbox Webpay)
Se desarrolló un entorno de simulación de alta fidelidad para la pasarela de pagos, replicando el comportamiento de un proveedor real en un entorno seguro de desarrollo:

* **Validación de Entrada:** Restricción de caracteres en tiempo real para asegurar la integridad de los datos financieros.
* **Lógica de Transacción:** Implementación de algoritmos de verificación de longitud y formato (16 dígitos) para simular escenarios de rechazo bancario.
* **Asincronía:** Emulación de latencia de red y procesamiento asíncrono para la confirmación de órdenes.

### Capa de Persistencia
* **Base de Datos:** MongoDB Atlas (NoSQL).
* **Modelado de Datos:** Se utiliza un modelo documental JSON, optimizado para estructuras variables como los detalles de un pedido gastronómico.
* **Seguridad en Tránsito:** La conexión con el clúster en la nube se establece exclusivamente mediante túneles encriptados TLS 1.2.



Usuario de prueba:
ana@example.com
A1b2c3d4e5







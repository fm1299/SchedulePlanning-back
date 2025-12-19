# SchedulePlanning-back

Backend API para el Sistema de Asignación de Aulas UNSA

## Requisitos Previos
- Python 3.9 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio
```sh
git clone https://github.com/fm1299/SchedulePlanning-back.git
cd SchedulePlanning-back
```

### 2. Crear un entorno virtual (recomendado)
```sh
python -m venv env
source env/bin/activate  # En Mac/Linux
env\Scripts\activate     # En Windows
```

### 3. Instalar dependencias
```sh
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copie el archivo `.env.example` a `.env` y configure las variables:

```sh
cp .env.example .env
```

Edite el archivo `.env` con sus configuraciones:

```env
# Database Configuration
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_bd

# Security Settings - IMPORTANTE: Generar una clave segura
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Database Echo (opcional)
DB_ECHO=False
```

**⚠️ IMPORTANTE - Generar SECRET_KEY:**
```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copie el resultado y úselo como `SECRET_KEY` en su archivo `.env`.

### 5. Configurar la base de datos
Asegúrese de que PostgreSQL esté ejecutándose y cree la base de datos:

```sql
CREATE DATABASE proyecto;
```

## Ejecución

### Modo Desarrollo
Para iniciar la aplicación en modo desarrollo con recarga automática:
```sh
uvicorn main:app --reload
```

### Modo Producción
```sh
uvicorn main:app --host localhost --port 8000
```

## Documentación de API

Una vez en ejecución, puede acceder a la documentación interactiva:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/api/v1/openapi.json

## Estructura del Proyecto

```
SchedulePlanning-back/
├── api/
│   ├── endpoints/      # Endpoints de la API
│   └── router.py       # Configuración de rutas principales
├── core/
│   ├── auth.py        # Autenticación JWT
│   ├── config.py      # Configuración de la aplicación
│   └── database.py    # Configuración de base de datos
├── models/            # Modelos SQLAlchemy
├── schemas/           # Schemas Pydantic
├── services/          # Lógica de negocio
├── repositories/      # Acceso a datos
├── .env.example       # Plantilla de variables de entorno
├── main.py           # Punto de entrada de la aplicación
└── requirements.txt  # Dependencias del proyecto
```

## Endpoints Principales

### Autenticación
- `POST /api/v1/auth/token` - Obtener token JWT
- `POST /api/v1/auth/admins` - Crear administrador (bootstrap)
- `GET /api/v1/auth/me` - Obtener usuario actual

### Aulas
- `GET /api/v1/aulas/` - Listar aulas
- `POST /api/v1/aulas/` - Crear aula
- `GET /api/v1/aulas/{id}` - Obtener aula por ID
- `PUT /api/v1/aulas/{id}` - Actualizar aula
- `DELETE /api/v1/aulas/{id}` - Eliminar aula

### Tipos de Aula
- `GET /api/v1/tipos-aula/` - Listar tipos de aula
- `POST /api/v1/tipos-aula/` - Crear tipo de aula

### Reservas
- `GET /api/v1/reservas/` - Listar reservas
- `POST /api/v1/reservas/` - Crear reserva
- `DELETE /api/v1/reservas/{id}` - Eliminar reserva

## Seguridad

### Variables de Entorno Sensibles
- ✅ El archivo `.env` está en `.gitignore` y no se sube al repositorio
- ✅ Use `.env.example` como plantilla
- ✅ Genere una `SECRET_KEY` fuerte y única para cada entorno
- ✅ Cambie la contraseña de base de datos por defecto

### Mejores Prácticas
- Nunca exponga credenciales en el código
- Use contraseñas fuertes para la base de datos
- Mantenga las dependencias actualizadas
- Configure CORS apropiadamente para producción

## Desarrollo

### Activar modo debug de SQL
Para ver las consultas SQL ejecutadas, configure en `.env`:
```env
DB_ECHO=True
```

### Instalar nuevas dependencias
```sh
pip install nombre-paquete
pip freeze > requirements.txt
```

## Licencia
Este proyecto está bajo la Licencia MIT.
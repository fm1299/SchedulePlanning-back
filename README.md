# SchedulePlanning-back

## Instalación
1. **Clonar el repositorio**
   ```sh
   git clone https://github.com/fm1299/SchedulePlanning-back.git
   cd SchedulePlanning-back
   ```
2. **Crear un entorno virtual (opcional)**
   ```sh
   python -m venv env
   source env/bin/activate  # En Mac/Linux
   env\Scripts\activate     # En Windows
   ```
3. **Instalar dependencias**
   ```sh
   pip install -r requirements.txt
   ```

## Ejecución
Para iniciar la aplicación, ejecute el siguiente comando:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```
Si está en modo de desarrollo y desea recargar automáticamente los cambios:
```sh
uvicorn main:app --reload
```

## Pruebas y Documentación de Endpoints
Una vez en ejecución, se puede acceder a la documentación interactiva de los endpoints en Swagger UI:
```
http://127.0.0.1:8000/docs
```
O en formato OpenAPI:
```
http://127.0.0.1:8000/redoc
```
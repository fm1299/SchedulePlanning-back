# services/docente_service.py
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from repositories.docente_repository import DocenteRepository
from schemas.docente import DocenteCreate, DocenteUpdate


class DocenteService:
    """
    Servicio de dominio para lógica relacionada con Docentes.
    Aquí centralizamos:
    - Reglas de negocio (validaciones, restricciones)
    - Cálculo de puntajes/ranking
    - Orquestación de operaciones del repositorio
    """

    def __init__(self, db: Session):
        # En esta versión sencilla, el service crea internamente el repositorio.
        self.repo = DocenteRepository(db)

    # ================== LÓGICA DE RANKING ==================

    @staticmethod
    def peso_categoria(nombre: str | None) -> int:
        tabla = {
            "principal": 100,
            "asociado": 80,
            "auxiliar": 60,
            "contratado": 40,
            "invitado": 20,
        }
        return tabla.get((nombre or "").lower(), 0)

    @staticmethod
    def bono_regimen(regimen: str | None) -> int:
        tabla = {
            "tiempo_completo": 20,
            "medio_tiempo": 10,
            "parcial": 0,
        }
        return tabla.get((regimen or "").lower(), 0)

    @staticmethod
    def bono_grado(grado: str | None) -> int:
        tabla = {
            "doctor": 15,
            "magister": 10,
            "segunda_especialidad": 5,
        }
        return tabla.get((grado or "").lower(), 0)

    @staticmethod
    def puntos_experiencia(fecha_inicio) -> int:
        if not fecha_inicio:
            return 0

        años = date.today().year - fecha_inicio.year

        if años >= 20:
            return 20
        if años >= 15:
            return 15
        if años >= 10:
            return 10
        if años >= 5:
            return 5
        return 0

    def calcular_puntaje(self, docente: Any) -> Dict[str, Any]:
        p_categoria = self.peso_categoria(
            getattr(getattr(docente, "tipo_docente", None), "nombre", None)
        )
        p_regimen = self.bono_regimen(getattr(docente, "regimen", None))
        p_grado = self.bono_grado(getattr(docente, "grado_academico", None))
        p_exp = self.puntos_experiencia(getattr(docente, "fecha_inicio", None))

        total = p_categoria + p_regimen + p_grado + p_exp

        return {
            "id_docente": getattr(docente, "id_docente"),
            "puntaje": total,
            "detalle": {
                "categoria": p_categoria,
                "regimen": p_regimen,
                "grado": p_grado,
                "experiencia": p_exp,
            },
        }

    # ================== OPERACIONES CRUD / CONSULTAS ==================

    def listar_docentes(
        self,
        skip: int,
        limit: int,
        #departamento_id: Optional[int] = None,
        tipo_docente_id: Optional[int] = None,
    ) -> Tuple[List[Any], int]:
        """
        Devuelve una tupla (docentes, total) con filtros y paginación.
        """
        docentes = self.repo.get_multi(
            skip=skip,
            limit=limit,
            #departamento_id=departamento_id,
            tipo_docente_id=tipo_docente_id,
        )
        # ORDENAR POR PUNTAJE
        docentes_ordenados = sorted(
            docentes,
            key=lambda d: self.calcular_puntaje(d)["puntaje"],
            reverse=True
        )
        
        total = self.repo.get_count()
        return docentes_ordenados, total

    def get_docente(self, docente_id: int) -> Optional[Any]:
        """
        Obtiene un docente por ID (incluyendo relaciones necesarias).
        """
        return self.repo.get(docente_id)

    def crear_docente(self, docente_in: DocenteCreate) -> Any:
        """
        Crea un nuevo docente y lo devuelve con sus relaciones (departamento, tipo_docente, etc.).
        """
        nuevo = self.repo.create(docente_in)
        # Recarga con relaciones completas
        return self.repo.get(nuevo.id_docente)

    def actualizar_docente(self, docente_id: int, docente_in: DocenteUpdate) -> Any:
        """
        Actualiza un docente existente.
        """
        return self.repo.update(docente_id, docente_in)

    def eliminar_docente(self, docente_id: int) -> None:
        """
        Elimina un docente tras verificar condiciones de negocio simples.
        (Detalle de validaciones adicionales se puede agregar aquí.)
        """
        self.repo.delete(docente_id)

    def docente_tiene_usuario(self, docente_id: int) -> bool:
        """
        Verifica si el docente tiene un usuario asociado.
        """
        return self.repo.docente_tiene_usuario(docente_id)

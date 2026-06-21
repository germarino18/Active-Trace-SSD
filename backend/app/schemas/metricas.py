from pydantic import BaseModel, ConfigDict


class MetricasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_alumnos: int = 0
    alumnos_activos: int = 0
    porcentaje_riesgo: float = 0.0
    promedio_progreso: float = 0.0
    total_docentes: int = 0
    total_materias_activas: int = 0
    total_carreras_activas: int = 0

from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ParametrosCotizacion(BaseModel):
    """Parámetros para solicitar una cotización de corte láser."""
    tiempo_seg: float = Field(..., gt=0, description="Tiempo de corte en segundos")
    material_cm2: float = Field(..., gt=0, description="Área de material en cm²")
    energia_kwh: float = Field(..., gt=0, description="Energía consumida en kWh")

    @validator('tiempo_seg', 'material_cm2', 'energia_kwh')
    def validar_positivo(cls, v):
        if v <= 0:
            raise ValueError('Debe ser mayor que cero')
        return v


class RespuestaCotizacion(BaseModel):
    """Respuesta de una cotización."""
    id_cotizacion: str
    costo_produccion: float
    precio_al_detal: float
    parametros: ParametrosCotizacion
    margen_aplicado: float
    timestamp: str
    status: str = "calculado"


class ErrorRespuesta(BaseModel):
    """Respuesta de error."""
    error: str
    detalle: Optional[str] = None
    timestamp: str


class EstadisticasServicio(BaseModel):
    """Estadísticas del servicio."""
    total_cotizaciones: int
    cotizaciones_exitosas: int
    errores: int
    inicio_servicio: str
    uptime_segundos: float


class SolicitudLote(BaseModel):
    """Solicitud de múltiples cotizaciones."""
    cotizaciones: List[ParametrosCotizacion] = Field(..., max_items=50)


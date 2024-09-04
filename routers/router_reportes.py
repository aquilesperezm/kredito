from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database.database import get_session
from classes.models import Exportacion, ExportacionRead, ExportacionResult
from classes.models import Usuario
from utils.manage_user import user_mgr

router_reportes = APIRouter(prefix='/reportes', tags=['Reportes'])


@router_reportes.get('/list')
async def reportes(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[ExportacionRead]:
    return session.query(Exportacion).all()

    """
     Con respecto a este metodo... existia un error en la consulta SQL, donde se consultaba
     a users (esta tabla no existe), lo otro es que debe pasarse el parametro de la consulta
     en forma de dicionario {"usuario_id":"4"}
    """
@router_reportes.post('/obtener_reporte_by_codigo/{codigo}')
async def reporte(codigo: str, params: dict, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> ExportacionResult:
    
    
    try:
        
        exportacion: Exportacion = session.query(
            Exportacion).where(Exportacion.codigo == codigo).first()
        resultados = session.execute(exportacion.sql_reporte, params).all()
        
        return ExportacionResult(error='', resultados=resultados)
    except Exception as e:
        
        return ExportacionResult(error=str(e), resultados={})

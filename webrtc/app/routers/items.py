from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.database import get_session
from app.models.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.services.crud_service import CRUDService
import asyncio

router = APIRouter(prefix="/api/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Crea un nuevo item
    """
    try:
        new_item = await CRUDService.create_item(db, item)
        return new_item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear item: {str(e)}"
        )


@router.get("/", response_model=List[ItemResponse])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, regex="^(active|inactive|pending)$"),
    db: AsyncSession = Depends(get_session)
):
    """
    Obtiene lista de items con paginación y filtros
    """
    items = await CRUDService.get_items(db, skip=skip, limit=limit, status=status)
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    Obtiene un item específico por ID
    """
    item = await CRUDService.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado"
        )
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Actualiza un item existente
    """
    updated_item = await CRUDService.update_item(db, item_id, item_update)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado"
        )
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    Elimina un item
    """
    deleted = await CRUDService.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado"
        )


@router.post("/bulk", response_model=List[ItemResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_items(
    items: List[ItemCreate],
    db: AsyncSession = Depends(get_session)
):
    """
    Crea múltiples items en paralelo (demuestra concurrencia)
    """
    if len(items) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 100 items por request"
        )

    try:
        new_items = await CRUDService.bulk_create_items(db, items)
        return new_items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear items: {str(e)}"
        )


@router.patch("/bulk/status", status_code=status.HTTP_200_OK)
async def bulk_update_status(
    item_ids: List[int],
    new_status: str = Query(..., regex="^(active|inactive|pending)$"),
    db: AsyncSession = Depends(get_session)
):
    """
    Actualiza el status de múltiples items en paralelo
    """
    if len(item_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 100 items por request"
        )

    updated_count = await CRUDService.bulk_update_status(db, item_ids, new_status)
    return {
        "updated_count": updated_count,
        "status": new_status
    }


async def background_task_example(item_id: int):
    """
    Ejemplo de tarea en background (paralelismo)
    """
    await asyncio.sleep(2)
    print(f"Tarea en background completada para item {item_id}")


@router.post("/{item_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_item_background(
    item_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session)
):
    """
    Procesa un item en background (demuestra paralelismo con BackgroundTasks)
    """
    item = await CRUDService.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado"
        )

    # Agregar tarea en background
    background_tasks.add_task(background_task_example, item_id)

    return {
        "message": "Item procesándose en background",
        "item_id": item_id
    }

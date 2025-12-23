from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from app.models.database import Item
from app.models.schemas import ItemCreate, ItemUpdate
from typing import List, Optional
import asyncio
from datetime import datetime


class CRUDService:
    """Servicio CRUD con operaciones asíncronas para concurrencia"""

    @staticmethod
    async def create_item(db: AsyncSession, item_data: ItemCreate) -> Item:
        """Crea un nuevo item de forma asíncrona"""
        new_item = Item(
            title=item_data.title,
            description=item_data.description,
            status=item_data.status
        )
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        return new_item

    @staticmethod
    async def get_item(db: AsyncSession, item_id: int) -> Optional[Item]:
        """Obtiene un item por ID"""
        result = await db.execute(select(Item).filter(Item.id == item_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_items(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Item]:
        """Obtiene múltiples items con paginación"""
        query = select(Item)

        if status:
            query = query.filter(Item.status == status)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_item(
        db: AsyncSession,
        item_id: int,
        item_data: ItemUpdate
    ) -> Optional[Item]:
        """Actualiza un item existente"""
        # Verificar que el item existe
        item = await CRUDService.get_item(db, item_id)
        if not item:
            return None

        # Actualizar solo los campos proporcionados
        update_data = item_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()

        await db.execute(
            update(Item).where(Item.id == item_id).values(**update_data)
        )
        await db.commit()

        # Refrescar y retornar el item actualizado
        await db.refresh(item)
        return item

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: int) -> bool:
        """Elimina un item"""
        item = await CRUDService.get_item(db, item_id)
        if not item:
            return False

        await db.execute(delete(Item).where(Item.id == item_id))
        await db.commit()
        return True

    @staticmethod
    async def bulk_create_items(
        db: AsyncSession,
        items_data: List[ItemCreate]
    ) -> List[Item]:
        """
        Crea múltiples items en paralelo usando asyncio.gather
        Demuestra manejo de concurrencia
        """
        tasks = []
        for item_data in items_data:
            # Creamos tareas concurrentes
            new_item = Item(
                title=item_data.title,
                description=item_data.description,
                status=item_data.status
            )
            db.add(new_item)
            tasks.append(new_item)

        await db.commit()

        # Refrescar todos los items en paralelo
        await asyncio.gather(*[db.refresh(item) for item in tasks])
        return tasks

    @staticmethod
    async def bulk_update_status(
        db: AsyncSession,
        item_ids: List[int],
        new_status: str
    ) -> int:
        """
        Actualiza el status de múltiples items en paralelo
        Retorna el número de items actualizados
        """
        result = await db.execute(
            update(Item)
            .where(Item.id.in_(item_ids))
            .values(status=new_status, updated_at=datetime.utcnow())
        )
        await db.commit()
        return result.rowcount

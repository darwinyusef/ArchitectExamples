"""
User Service - CRUD operations for users (temporal).

NOTE: Este servicio es temporal. En producción, los usuarios serán manejados
por el microservicio principal en /proyectos/aquicreamos_2025/aqc/app
"""

from typing import Optional
from datetime import datetime
import uuid
import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user_schemas import UserCreate, UserUpdate


class UserService:
    """Service for managing users (temporal POC)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user
        """
        user_id = str(uuid.uuid4())

        user = User(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=self._hash_password(user_data.password),
            is_active=True,
            preferences=user_data.preferences or {},
            metadata=user_data.metadata or {}
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate
    ) -> Optional[User]:
        """Update user."""
        user = await self.get_user(user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        # Hash password if being updated
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def verify_password(
        self,
        user_id: str,
        password: str
    ) -> bool:
        """Verify user password."""
        user = await self.get_user(user_id)
        if not user:
            return False

        return user.hashed_password == self._hash_password(password)

    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login timestamp."""
        user = await self.get_user(user_id)
        if not user:
            return None

        user.last_login = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate user account."""
        user = await self.get_user(user_id)
        if not user:
            return None

        user.is_active = False
        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def activate_user(self, user_id: str) -> Optional[User]:
        """Activate user account."""
        user = await self.get_user(user_id)
        if not user:
            return None

        user.is_active = True
        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

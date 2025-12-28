"""
Code Snapshot Service - CRUD operations for code snapshots.
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CodeSnapshot, Embedding
from app.schemas.code_snapshot_schemas import CodeSnapshotCreate, CodeSnapshotUpdate
from app.agents.tools.rag_tools import RAGTools


class CodeSnapshotService:
    """Service for managing code snapshots."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = RAGTools()

    async def create_snapshot(
        self,
        user_id: str,
        snapshot_data: CodeSnapshotCreate,
        generate_embedding: bool = True
    ) -> CodeSnapshot:
        """
        Create a new code snapshot.

        Args:
            user_id: User ID
            snapshot_data: Snapshot creation data
            generate_embedding: Whether to generate embedding for RAG

        Returns:
            Created code snapshot
        """
        snapshot_id = str(uuid.uuid4())

        snapshot = CodeSnapshot(
            id=snapshot_id,
            task_id=snapshot_data.task_id,
            user_id=user_id,
            file_path=snapshot_data.file_path,
            language=snapshot_data.language,
            code_content=snapshot_data.code_content,
            diff_from_previous=snapshot_data.diff_from_previous,
            metadata=snapshot_data.metadata or {}
        )

        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)

        # Generate embedding for RAG
        if generate_embedding:
            await self._create_embedding(snapshot)

        return snapshot

    async def get_snapshot(
        self,
        snapshot_id: str,
        user_id: str
    ) -> Optional[CodeSnapshot]:
        """Get code snapshot by ID."""
        result = await self.db.execute(
            select(CodeSnapshot).where(
                CodeSnapshot.id == snapshot_id,
                CodeSnapshot.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_snapshots(
        self,
        user_id: str,
        task_id: Optional[str] = None,
        language: Optional[str] = None,
        validated_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[CodeSnapshot]:
        """List code snapshots with filters."""
        query = select(CodeSnapshot).where(CodeSnapshot.user_id == user_id)

        if task_id:
            query = query.where(CodeSnapshot.task_id == task_id)

        if language:
            query = query.where(CodeSnapshot.language == language)

        if validated_only:
            query = query.where(CodeSnapshot.validation_passed == True)

        query = query.order_by(CodeSnapshot.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_snapshot(
        self,
        snapshot_id: str,
        user_id: str,
        snapshot_update: CodeSnapshotUpdate
    ) -> Optional[CodeSnapshot]:
        """Update code snapshot (mainly for validation results)."""
        snapshot = await self.get_snapshot(snapshot_id, user_id)
        if not snapshot:
            return None

        update_data = snapshot_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(snapshot, field, value)

        snapshot.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(snapshot)

        return snapshot

    async def delete_snapshot(
        self,
        snapshot_id: str,
        user_id: str
    ) -> bool:
        """Delete code snapshot."""
        result = await self.db.execute(
            delete(CodeSnapshot).where(
                CodeSnapshot.id == snapshot_id,
                CodeSnapshot.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def update_validation_result(
        self,
        snapshot_id: str,
        user_id: str,
        validation_passed: bool,
        validation_score: float,
        validation_feedback: str,
        issues_found: Optional[List[dict]] = None
    ) -> Optional[CodeSnapshot]:
        """
        Update validation results for a code snapshot.

        Args:
            snapshot_id: Snapshot ID
            user_id: User ID
            validation_passed: Whether validation passed
            validation_score: Score 0-1
            validation_feedback: AI feedback text
            issues_found: List of issues detected

        Returns:
            Updated snapshot
        """
        snapshot = await self.get_snapshot(snapshot_id, user_id)
        if not snapshot:
            return None

        snapshot.validation_passed = validation_passed
        snapshot.validation_score = validation_score
        snapshot.validation_feedback = validation_feedback
        snapshot.issues_found = issues_found or []
        snapshot.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(snapshot)

        return snapshot

    async def get_latest_for_task(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[CodeSnapshot]:
        """Get the latest code snapshot for a task."""
        result = await self.db.execute(
            select(CodeSnapshot)
            .where(
                CodeSnapshot.task_id == task_id,
                CodeSnapshot.user_id == user_id
            )
            .order_by(CodeSnapshot.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _create_embedding(self, snapshot: CodeSnapshot) -> None:
        """Create embedding for code snapshot (for RAG)."""
        # Include language and file path in embedding content
        content = f"""
File: {snapshot.file_path}
Language: {snapshot.language}

Code:
{snapshot.code_content}
"""

        embedding_vector = await self.rag._generate_embedding(content)

        embedding = Embedding(
            id=str(uuid.uuid4()),
            user_id=snapshot.user_id,
            entity_type="code_snapshot",
            entity_id=snapshot.id,
            content=content,
            embedding=embedding_vector,
            model="text-embedding-3-small",
            metadata={
                "language": snapshot.language,
                "file_path": snapshot.file_path,
                "validation_passed": snapshot.validation_passed,
                "validation_score": snapshot.validation_score
            }
        )

        self.db.add(embedding)
        await self.db.commit()

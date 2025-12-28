"""
Course Service - CRUD operations for courses (temporal).

NOTE: Este servicio es temporal. En producción, los cursos serán manejados
por el microservicio principal en /proyectos/aquicreamos_2025/aqc/app
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course, CourseStatus, Embedding
from app.schemas.course_schemas import CourseCreate, CourseUpdate
from app.agents.tools.rag_tools import RAGTools


class CourseService:
    """Service for managing courses (temporal POC)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = RAGTools()

    async def create_course(
        self,
        user_id: str,
        course_data: CourseCreate,
        generate_embedding: bool = True
    ) -> Course:
        """
        Create a new course.

        Args:
            user_id: User ID (instructor)
            course_data: Course creation data
            generate_embedding: Whether to generate embedding for RAG

        Returns:
            Created course
        """
        course_id = str(uuid.uuid4())

        course = Course(
            id=course_id,
            user_id=user_id,
            title=course_data.title,
            description=course_data.description,
            status=CourseStatus.DRAFT,
            syllabus=course_data.syllabus or {},
            metadata=course_data.metadata or {},
            start_date=course_data.start_date,
            end_date=course_data.end_date
        )

        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)

        # Generate embedding for RAG
        if generate_embedding and course.description:
            await self._create_embedding(course)

        return course

    async def get_course(self, course_id: str) -> Optional[Course]:
        """Get course by ID."""
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def list_courses(
        self,
        status: Optional[CourseStatus] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:
        """List courses with filters."""
        query = select(Course)

        if status:
            query = query.where(Course.status == status)

        if user_id:
            query = query.where(Course.user_id == user_id)

        query = query.order_by(Course.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_course(
        self,
        course_id: str,
        course_update: CourseUpdate
    ) -> Optional[Course]:
        """Update course."""
        course = await self.get_course(course_id)
        if not course:
            return None

        update_data = course_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(course, field, value)

        course.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(course)

        # Update embedding if description changed
        if course_update.description:
            await self._update_embedding(course)

        return course

    async def publish_course(self, course_id: str) -> Optional[Course]:
        """Publish a course (change status to ACTIVE)."""
        course = await self.get_course(course_id)
        if not course:
            return None

        course.status = CourseStatus.ACTIVE
        course.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def archive_course(self, course_id: str) -> Optional[Course]:
        """Archive a course."""
        course = await self.get_course(course_id)
        if not course:
            return None

        course.status = CourseStatus.ARCHIVED
        course.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def _create_embedding(self, course: Course) -> None:
        """Create embedding for course (for RAG)."""
        # Combine title, description, and syllabus for embedding
        syllabus_text = ""
        if course.syllabus:
            syllabus_text = f"\n\nSyllabus: {str(course.syllabus)}"

        content = f"Course: {course.title}\n\nDescription: {course.description}{syllabus_text}"

        embedding_vector = await self.rag._generate_embedding(content)

        embedding = Embedding(
            id=str(uuid.uuid4()),
            user_id=course.user_id,
            entity_type="course",
            entity_id=course.id,
            content=content,
            embedding=embedding_vector,
            model="text-embedding-3-small",
            metadata={
                "course_status": course.status.value
            }
        )

        self.db.add(embedding)
        await self.db.commit()

    async def _update_embedding(self, course: Course) -> None:
        """Update embedding when course description changes."""
        from sqlalchemy import delete

        # Delete old embedding
        await self.db.execute(
            delete(Embedding).where(
                Embedding.entity_type == "course",
                Embedding.entity_id == course.id
            )
        )

        # Create new embedding
        await self._create_embedding(course)

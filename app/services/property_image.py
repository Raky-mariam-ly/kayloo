"""Service for handling property image uploads and gallery management."""
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, select

from core.files import PropertyImageFile
from models.property import Property
from models.property_gallery import PropertyGallery
from models.property_image import PropertyImage
from repositories.property_image import PropertyImageRepository
from services.base import BaseService


class PropertyImageService(BaseService[PropertyImage]):
    """Original service for PropertyImage CRUD."""
    
    def __init__(self, repository: PropertyImageRepository):
        super().__init__(repository)

    async def get_by_property_id(self, property_id: UUID) -> List[PropertyImage]:
        return await self.repository.get_by_property_id(property_id)


class PropertyUploadService:
    """Manages property cover and gallery image uploads."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_agency_name(self, property_id: UUID) -> Optional[str]:
        """Fetch agency name for a property without lazy-loading issues."""
        result = await self.session.execute(
            select(Property)
            .where(Property.id == property_id)
            .options(selectinload(Property.agency))
        )
        prop = result.unique().scalar_one_or_none()
        
        if prop and prop.agency:
            return prop.agency.name
        return None

    def unpack_cover_image(
        self, 
        raw: Any, 
        agency_name: Optional[str] = None, 
        property_id: Optional[UUID] = None
    ) -> Tuple[Optional[PropertyImageFile], bool]:
        """
        Extract PropertyImageFile from parsed ImageField data.
        Returns (PropertyImageFile, should_delete).
        """
        if raw is None:
            return None, False

        # Handle tuple (value, should_delete) format from form
        if isinstance(raw, tuple) and len(raw) == 2:
            val, should_delete = raw
            if should_delete:
                return None, True
            if val is None:
                return None, False
            
            return PropertyImageFile(
                content=val.file,
                filename=val.filename,
                content_type=val.content_type,
                agency_name=agency_name,
                property_id=property_id,
            ), False

        return None, False

    def unpack_gallery_images(
        self,
        raw: Any,
        agency_name: Optional[str] = None,
        property_id: Optional[UUID] = None
    ) -> Tuple[List[PropertyImageFile], bool]:
        """
        Extract PropertyImageFile list from parsed ImageField data.
        Returns (list of PropertyImageFile, should_delete).
        """
        if raw is None:
            return [], False

        # Handle tuple (value, should_delete) format from form
        if isinstance(raw, tuple) and len(raw) == 2:
            files, should_delete = raw
            if should_delete:
                return [], True
            if not files:
                return [], False
            
            # Ensure files is a list
            files = files if isinstance(files, list) else [files]
            
            return [
                PropertyImageFile(
                    content=f.file,
                    filename=f.filename,
                    content_type=f.content_type,
                    agency_name=agency_name,
                    property_id=property_id,
                )
                for f in files
            ], False

        return [], False

    async def process_images(
        self,
        property_id: UUID,
        raw_cover: Any,
        raw_gallery: Any,
        force_agency_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process cover and gallery images for a property.
        
        Returns dict with:
        - cover_file: PropertyImageFile or None
        - cover_deleted: bool
        - gallery_files: list of PropertyImageFile
        - gallery_deleted: bool
        - agency_name: str or None
        """
        # Get agency name if not provided
        agency_name = force_agency_name
        if not agency_name:
            agency_name = await self.get_agency_name(property_id)

        # Unpack cover image
        cover_file, cover_deleted = self.unpack_cover_image(
            raw_cover,
            agency_name=agency_name,
            property_id=property_id
        )

        # Unpack gallery images
        gallery_files, gallery_deleted = self.unpack_gallery_images(
            raw_gallery,
            agency_name=agency_name,
            property_id=property_id
        )

        return {
            "cover_file": cover_file,
            "cover_deleted": cover_deleted,
            "gallery_files": gallery_files,
            "gallery_deleted": gallery_deleted,
            "agency_name": agency_name,
        }

    async def apply_cover_image(
        self,
        prop: Property,
        cover_file: Optional[PropertyImageFile],
        delete_cover: bool = False
    ) -> None:
        """Apply cover image to a property instance."""
        if delete_cover:
            prop.image_url = None
        elif cover_file:
            prop.image_url = cover_file

    async def apply_gallery_images(
        self,
        property_id: UUID,
        gallery_files: List[PropertyImageFile],
        delete_gallery: bool = False
    ) -> None:
        """Apply gallery images to a property."""
        if delete_gallery:
            await self.session.execute(
                delete(PropertyGallery)
                .where(PropertyGallery.property_id == property_id)
            )
        elif gallery_files:
            # Create or update gallery
            prop_gallery = await self.session.execute(
                select(PropertyGallery)
                .where(PropertyGallery.property_id == property_id)
            )
            gallery = prop_gallery.scalar_one_or_none()

            if gallery:
                gallery.images = gallery_files
            else:
                gallery = PropertyGallery(
                    property_id=property_id,
                    images=gallery_files
                )
                self.session.add(gallery)

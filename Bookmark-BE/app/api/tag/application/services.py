# Third-party imports
from fastapi import Depends, status

# Local application imports
from app.api.tag.domain.services import TagDomainServices, TagDataClass
from app.schema.tag.request_schema import TagCreateRequestSchema
from app.api.auth.domain.models import User
from app.utils.custom_exception import CustomException
from app.utils.messages.custom_response_messages import get_response_message


class TagAppServices:
    def __init__(
        self,
        tag_domain_services: TagDomainServices = Depends(TagDomainServices),
    ) -> None:
        self.tag_domain_services = tag_domain_services

    async def get_tags_by_user(self, current_user: User) -> list:
        """
        Get all tags created by the current user.
        """
        tags = await self.tag_domain_services.get_tags_by_user(current_user.id)
        return tags

    async def create_tag(
        self, current_user: User, tag_data: TagCreateRequestSchema
    ) -> None:
        """
        Create a new custom tag for the current user.
        """
        existing = await self.tag_domain_services.get_tag_by_name_and_user(
            current_user.id, tag_data.name
        )
        if existing:
            raise CustomException(
                message=get_response_message("tag_already_exists", tag_data.name),
                status_code=status.HTTP_409_CONFLICT,
            )

        data = TagDataClass(user_id=current_user.id, name=tag_data.name)
        await self.tag_domain_services.create_tag(data)
        
        return None

    async def get_tag_cloud(self, current_user: User) -> list:
        """
        Retrieve tag cloud data (tag names mapped to usage counts) for the current user.
        """
        return await self.tag_domain_services.get_tag_cloud(current_user.id)

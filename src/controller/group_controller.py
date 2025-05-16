from typing import Optional
from fastapi import status
from fastapi.responses import JSONResponse

from models.errors.errors import ValidationError
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.response import CustomResponse
from service.group_service import GroupService, IGroupService


def _validate_empty_string(value: str, **kwargs) -> None:
    if not value:
        raise ValidationError(
            title="Empty value",
            detail=f"{kwargs['name']} cannot be empty"
        )


def _validate_group(group: GroupDTO) -> None:
    _validate_empty_string(group.name, name="Group name")
    _validate_empty_string(group.description, name="Group description")
    _validate_empty_string(group.owner_id, name="Group owner id")


class GroupController:
    def __init__(self, service: Optional[IGroupService] = None):
        self.service = service or GroupService()

    def post_group(self, group: GroupDTO) -> CustomResponse[GroupReturn]:
        _validate_group(group)

        _group = self.service.save_group(group)

        return CustomResponse(data=_group)

    def get_group(self, group_id: str) -> CustomResponse[GroupReturn]:
        _validate_empty_string(group_id, name="Group id")

        group = self.service.get_group(group_id)

        return CustomResponse(data=group)

    def get_user_groups(self, user_id: str) -> CustomResponse[list[GroupReturn]]:
        _validate_empty_string(user_id, name="User id")

        groups = self.service.get_user_groups(user_id)

        return CustomResponse(data=groups)

    def post_member(self, group_id: str, user_id: str) -> CustomResponse[list[Member]]:
        _validate_empty_string(group_id, name="Group id")
        _validate_empty_string(user_id, name="User id")

        members = self.service.save_member(group_id, user_id)

        return CustomResponse(data=members)

    def get_group_members(self, group_id: str) -> CustomResponse[list[Member]]:
        _validate_empty_string(group_id, name="Group id")

        members = self.service.get_group_members(group_id)

        return CustomResponse(data=members)

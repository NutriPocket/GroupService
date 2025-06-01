from typing import Optional

from models.errors.errors import ValidationError
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.response import CustomResponse
from models.routine import PostRoutineParams, RoutineDTO, RoutineReturn
from service.group_service import GroupService, IGroupService


class GroupController:
    def __init__(self, service: Optional[IGroupService] = None):
        self.service = service or GroupService()

    def post_group(self, group: GroupDTO) -> CustomResponse[GroupReturn]:
        _group = self.service.save_group(group)

        return CustomResponse(data=_group)

    def get_group(self, group_id: str) -> CustomResponse[GroupReturn]:
        group = self.service.get_group(group_id)

        return CustomResponse(data=group)

    def get_user_groups(self, user_id: str) -> CustomResponse[list[GroupReturn]]:
        groups = self.service.get_user_groups(user_id)

        return CustomResponse(data=groups)

    def post_member(self, group_id: str, user_id: str) -> CustomResponse[list[Member]]:
        members = self.service.save_member(group_id, user_id)

        return CustomResponse(data=members)

    def get_group_members(self, group_id: str) -> CustomResponse[list[Member]]:
        members = self.service.get_group_members(group_id)

        return CustomResponse(data=members)

    def post_group_routine(self, group_id: str, routine: RoutineDTO, params: PostRoutineParams) -> CustomResponse[list[RoutineReturn]]:
        group = self.service.save_routine(group_id, routine, params)

        return CustomResponse(data=group)
    
    def get_group_routines(self, group_id: str) -> CustomResponse[list[RoutineReturn]]:
        routines = self.service.get_routines(group_id)

        return CustomResponse(data=routines)
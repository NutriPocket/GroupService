from fastapi import APIRouter, status

from controller.group_controller import GroupController
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.response import CustomResponse

router = APIRouter()


@router.post(
    "/groups",
    summary="Create a new group",
    status_code=status.HTTP_201_CREATED
)
def post_group(group: GroupDTO) -> CustomResponse[GroupReturn]:
    return GroupController().post_group(group)


@router.get(
    "/groups/{group_id}",
    summary="Get the group by id: {group_id}",
    status_code=status.HTTP_200_OK
)
def get_group(group_id: str) -> CustomResponse[GroupReturn]:
    return GroupController().get_group(group_id)


@router.get(
    "/users/{user_id}/groups",
    summary="Get all groups for the user: {user_id}",
    status_code=status.HTTP_200_OK
)
def get_user_groups(user_id: str) -> CustomResponse[list[GroupReturn]]:
    return GroupController().get_user_groups(user_id)


@router.post(
    "/groups/{group_id}/users/{user_id}",
    summary="Add the user {user_id} to the group: {group_id}",
    status_code=status.HTTP_201_CREATED
)
def post_member(group_id: str, user_id: str) -> CustomResponse[list[Member]]:
    return GroupController().post_member(group_id, user_id)


@router.get(
    "/groups/{group_id}/users",
    summary="Get all members of the group: {group_id}",
    status_code=status.HTTP_200_OK
)
def get_group_members(group_id: str) -> CustomResponse[list[Member]]:
    return GroupController().get_group_members(group_id)

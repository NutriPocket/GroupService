from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from controller.group_controller import GroupController
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.response import CustomResponse, ErrorDTO

router = APIRouter()


@router.post(
    "/groups",
    summary="Create a new group",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": CustomResponse[GroupReturn],
            "description": "Group created successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDTO,
            "description": "Bad request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorDTO,
            "description": "User unauthorized"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorDTO,
            "description": "No authorization provided"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorDTO,
            "description": "Unprocessable entity, body must match the schema"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorDTO,
            "description": "Internal server error"
        },
    }
)
def post_group(group: GroupDTO) -> CustomResponse[GroupReturn]:
    return GroupController().post_group(group)


@router.get(
    "/groups/{group_id}",
    summary="Get the group by id: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[GroupReturn],
            "description": "Group retrieved successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDTO,
            "description": "Bad request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorDTO,
            "description": "User unauthorized"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorDTO,
            "description": "No authorization provided"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorDTO,
            "description": "Group with id {group_id} not found"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorDTO,
            "description": "Unprocessable entity, body must match the schema"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorDTO,
            "description": "Internal server error"
        },
    }
)
def get_group(group_id: str) -> CustomResponse[GroupReturn]:
    return GroupController().get_group(group_id)


@router.get(
    "/users/{user_id}/groups",
    summary="Get all groups for the user: {user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[list[GroupReturn]],
            "description": "Groups retrieved successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDTO,
            "description": "Bad request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorDTO,
            "description": "User unauthorized"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorDTO,
            "description": "No authorization provided"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorDTO,
            "description": "Unprocessable entity, body must match the schema"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorDTO,
            "description": "Internal server error"
        },
    }
)
def get_user_groups(user_id: str) -> CustomResponse[list[GroupReturn]]:
    return GroupController().get_user_groups(user_id)


@router.post(
    "/groups/{group_id}/users/{user_id}",
    summary="Add the user {user_id} to the group: {group_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[list[Member]],
            "description": "Member added successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDTO,
            "description": "Bad request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorDTO,
            "description": "User unauthorized"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorDTO,
            "description": "No authorization provided"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorDTO,
            "description": "Group with id {group_id} not found"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorDTO,
            "description": "Unprocessable entity, body must match the schema"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorDTO,
            "description": "Internal server error"
        },
    }
)
def post_member(group_id: str, user_id: str) -> CustomResponse[list[Member]]:
    return GroupController().post_member(group_id, user_id)


@router.get(
    "/groups/{group_id}/users",
    summary="Get all members of the group: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[list[Member]],
            "description": "Members retrieved successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDTO,
            "description": "Bad request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorDTO,
            "description": "User unauthorized"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorDTO,
            "description": "No authorization provided"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorDTO,
            "description": "Group with id {group_id} not found"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorDTO,
            "description": "Unprocessable entity, body must match the schema"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorDTO,
            "description": "Internal server error"
        },
    }
)
def get_group_members(group_id: str) -> CustomResponse[list[Member]]:
    return GroupController().get_group_members(group_id)

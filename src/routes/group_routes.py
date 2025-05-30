from typing import Optional
from fastapi import APIRouter, Path, Query, status
from fastapi.responses import JSONResponse

from controller.group_controller import GroupController
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.response import CustomResponse, ErrorDTO
from models.routine import PostRoutineParams, RoutineDTO, RoutineReturn

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
def get_group(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[GroupReturn]:
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
def get_user_groups(
        user_id: str = Path(
            ...,
            description="ID of the user",
            examples=["123e4567-e89b-12d3-a456-426614174000"],
            title="UUID",
            min_length=36, max_length=36,
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )) -> CustomResponse[list[GroupReturn]]:
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
def post_member(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ), user_id: str = Path(
        ...,
        description="ID of the user",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[list[Member]]:
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
def get_group_members(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[list[Member]]:
    return GroupController().get_group_members(group_id)


@router.post(
    "/groups/{group_id}/routines",
    summary="Post a new routine for group: {group_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": CustomResponse[list[RoutineReturn]],
            "description": "Routine posted successfully for group {group_id}"
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
def post_group_routine(
    routine: RoutineDTO,
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
    forceMembers: bool = Query(
        False,
        description="""
            This parameter is used to ignore schedules 
            that are incompatible with individual members' routines.
            In other words, if this parameter is true, this service does not check
            whether all members can meet this new schedule.
        """)
) -> CustomResponse[list[RoutineReturn]]:
    params: PostRoutineParams = PostRoutineParams(forceMembers=forceMembers)

    return GroupController().post_group_routine(group_id, routine, params)


@router.get(
    "/groups/{group_id}/routines",
    summary="Get all routines for group: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[list[RoutineReturn]],
            "description": "Group {group_id} routines retrieved successfully"
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
def get_group_routines(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
) -> CustomResponse[list[RoutineReturn]]:
    return GroupController().get_group_routines(group_id)

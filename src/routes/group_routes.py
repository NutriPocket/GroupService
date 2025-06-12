from typing import Optional
from fastapi import APIRouter, Path, Query, Request, status
from fastapi.responses import JSONResponse

from controller.group_controller import GroupController
from models.event import EventDTO, EventReturn
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.poll import PollReturn, VoteDTO
from models.response import CustomResponse, ErrorDTO
from models.routine import PostRoutineParams, RoutineDTO, RoutineReturn
from tests.test_jwt import auth_header

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
        status.HTTP_409_CONFLICT: {
            "model": ErrorDTO,
            "description": "Members have conflicting schedules with the new routine"
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
    request: Request,
    routine: RoutineDTO,
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
    force_members: bool = Query(
        False,
        description="""
            This parameter is used to ignore schedules 
            that are incompatible with individual members' routines.
            In other words, if this parameter is true, this service does not check
            whether all members can meet this new schedule.
        """)
) -> CustomResponse[list[RoutineReturn]]:
    params: PostRoutineParams = PostRoutineParams(
        force_members=force_members, auth_header=getattr(
            request.state, "auth_header", "")
    )

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


@router.post(
    "/groups/{group_id}/events",
    summary="Post an event for group: {group_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": CustomResponse[EventReturn],
            "description": "Group {group_id} created event"
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
def post_group_event(
    event: EventDTO,
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[EventReturn]:
    return GroupController().post_group_event(group_id, event)


@router.patch(
    "/groups/{group_id}/events/{event_id}",
    summary="Update an event for group: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[EventReturn],
            "description": "Event updated successfully"
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
            "description": "Event or group not found"
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
def patch_group_event(
    event: EventDTO,
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
    event_id: str = Path(
        ...,
        description="ID of the event",
        examples=["123e4567-e89b-12d3-a456-426614174001"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[EventReturn]:
    return GroupController().patch_group_event(group_id, event_id, event)


@router.get(
    "/groups/{group_id}/events",
    summary="Get all events for group: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[list[EventReturn]],
            "description": "Events retrieved successfully"
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
def get_group_events(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[list[EventReturn]]:
    return GroupController().get_group_events(group_id)


@router.get(
    "/groups/{group_id}/events/{event_id}",
    summary="Get an event by id for group: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[EventReturn],
            "description": "Event retrieved successfully"
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
            "description": "Event or group not found"
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
def get_group_event(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
    event_id: str = Path(
        ...,
        description="ID of the event",
        examples=["123e4567-e89b-12d3-a456-426614174001"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[EventReturn]:
    return GroupController().get_group_event(group_id, event_id)


@router.delete(
    "/groups/{group_id}/events/{event_id}",
    summary="Delete an event by id for group: {group_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Event deleted successfully"
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
            "description": "Event or group not found"
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
def delete_group_event(
    group_id: str = Path(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
    event_id: str = Path(
        ...,
        description="ID of the event",
        examples=["123e4567-e89b-12d3-a456-426614174001"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
) -> CustomResponse[None]:
    return GroupController().delete_group_event(group_id, event_id)


@router.put(
    "/polls/{poll_id}",
    summary="Vote on poll: {poll_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomResponse[EventReturn],
            "description": "Event voted successfully"
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
            "description": "Event or group not found"
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
def put_vote(
    vote: VoteDTO,
    poll_id: str = Path(
        ...,
        description="ID of the poll",
        examples=["123e4567-e89b-12d3-a456-426614174001"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ),
) -> CustomResponse[PollReturn]:
    return GroupController().put_vote(vote, poll_id)

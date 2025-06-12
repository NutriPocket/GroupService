from abc import ABCMeta, abstractmethod
from datetime import date
import datetime
import logging
from os import getenv
from typing import Optional

from models.errors.errors import AuthenticationError, BadGatewayError, ConflictError, NotFoundError, ValidationError
from models.event import EventDTO, EventReturn
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.poll import PollReturn, VoteDTO
from models.routine import PostRoutineParams, RoutineDTO, RoutineReturn, Schedule
from repository.group_repository import GroupRepository, IGroupRepository
import requests

class IGroupService(metaclass=ABCMeta):
    @abstractmethod
    def save_group(self, group: GroupDTO) -> GroupReturn:
        pass

    @abstractmethod
    def get_group(self, group_id: str) -> GroupReturn:
        pass

    @abstractmethod
    def get_user_groups(self, user_id: str) -> list[GroupReturn]:
        pass

    @abstractmethod
    def save_member(self, group_id: str, user_id: str) -> list[Member]:
        pass

    @abstractmethod
    def get_group_members(self, group_id: str) -> list[Member]:
        pass

    @abstractmethod
    def save_routine(self, group_id: str, routine: RoutineDTO, params: PostRoutineParams) -> list[RoutineReturn]:
        pass

    @abstractmethod
    def get_routines(self, group_id: str) -> list[RoutineReturn]:
        pass

    @abstractmethod
    def save_event(self, group_id: str, event: EventDTO) -> EventReturn:
        pass

    @abstractmethod
    def update_event(self, group_id: str, event_id: str, event: EventDTO) -> EventReturn:
        pass

    @abstractmethod
    def get_events(self, group_id: str) -> list[EventReturn]:
        pass

    @abstractmethod
    def get_event(self, group_id: str, event_id: str) -> EventReturn:
        pass

    @abstractmethod
    def delete_event(self, group_id: str, event_id: str) -> None:
        pass

    @abstractmethod
    def put_vote(self, vote: VoteDTO) -> PollReturn:
        pass


class GroupService(IGroupService):
    def __init__(self, repository: Optional[IGroupRepository] = None):
        self.repository = repository or GroupRepository()
        self.PROGRESS_SERVICE_URI = getenv(
            "PROGRESS_SERVICE_URI", "http://0.0.0.0:8082"
        )

    def save_group(self, group: GroupDTO) -> GroupReturn:
        ret = self.repository.save_group(group)

        if not ret:
            raise Exception("Failed to save group")

        return ret

    def get_group(self, group_id: str) -> GroupReturn:
        ret = self.repository.get_group(group_id)

        if not ret:
            raise NotFoundError(f"Group with id {group_id} not found")

        ret.routines = self.repository.get_routines(group_id)

        return ret

    def get_user_groups(self, user_id: str) -> list[GroupReturn]:
        return self.repository.get_user_groups(user_id)

    def save_member(self, group_id: str, user_id: str) -> list[Member]:
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        self.repository.save_member(group_id, user_id)
        return self.repository.get_group_members(group_id)

    def get_group_members(self, group_id: str) -> list[Member]:
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        return self.repository.get_group_members(group_id)

    def get_free_schedules(self, members: list[str], auth_header: str) -> list[Schedule]:
        query_param = "?users=" + "&users=".join(members)

        response = requests.get(
            f"{self.PROGRESS_SERVICE_URI}/users/freeSchedules/{query_param}",
            headers={"Authorization": auth_header}
        )

        match response.status_code:
            case 200:
                r: dict = response.json()
                data = r.get("data", None)
                if not data:
                    raise BadGatewayError()

                schedules = data.get("schedules", [])

                return [Schedule(**schedule) for schedule in schedules]
            case _:
                logging.error(response.json())
                raise BadGatewayError()

    def check_member_individual_routines_collision(self, member_ids: list[str], routine: RoutineDTO, auth_header: str) -> None:
        member_free_schedules = self.get_free_schedules(
            member_ids, auth_header
        )

        no_conflictive_schedules_with_new_routine = [
            schedule for schedule in member_free_schedules
            if schedule.day == routine.day and
            schedule.start_hour <= routine.start_hour
            and schedule.end_hour >= routine.end_hour
        ]

        if len(no_conflictive_schedules_with_new_routine) == 0:
            raise ConflictError(
                title="Conflict in routine schedules",
                detail="There are members with conflicting routines",
            )

    def check_member_group_routines_collision(self, member_ids: list[str], routine: RoutineDTO) -> None:
        members_group_routines_schedules = self.repository.get_user_groups_routines_schedules(
            member_ids
        )

        for s in members_group_routines_schedules:
            if s.day == routine.day and \
                s.end_hour > routine.start_hour and \
                    s.start_hour < routine.end_hour:
                raise ConflictError(
                    title="Conflict in routine schedules",
                    detail=f"Conflicting member routine on {s.day} from {s.start_hour} to {s.end_hour}"
                )

    def save_routine(self, group_id: str, routine: RoutineDTO, params: PostRoutineParams) -> list[RoutineReturn]:
        members = self.repository.get_group_members(group_id)

        if not members:
            raise NotFoundError(f"Group with id {group_id} not found")

        member_ids = [member.user_id for member in members]

        if routine.creator_id not in member_ids:
            raise AuthenticationError(
                f"User with id {routine.creator_id} is not a member of group {group_id}"
            )

        if not params.force_members:
            self.check_member_group_routines_collision(
                member_ids, routine
            )

            self.check_member_individual_routines_collision(
                member_ids, routine, params.auth_header
            )

        self.repository.save_routine(group_id, routine)

        return self.repository.get_routines(group_id)

    def get_routines(self, group_id: str) -> list[RoutineReturn]:
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        return self.repository.get_routines(group_id)

    def save_event(self, group_id: str, event: EventDTO) -> EventReturn:
        """
        Create a new event for a group
        """
        # Check if group exists
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        # Check if event creator is a member of the group
        members = self.repository.get_group_members(group_id)
        member_ids = [member.user_id for member in members]

        if event.creator_id not in member_ids:
            raise AuthenticationError(
                f"User with id {event.creator_id} is not a member of group {group_id}"
            )

        if event.date < datetime.datetime.now():
            raise ValidationError(
                title="Invalid event date",
                detail="Event date cannot be in the past"
            )

        # Check for colliding events
        colliding_events = self.repository.find_group_colliding_events(
            group_id, event.date, event.start_hour, event.end_hour
        )

        if colliding_events:
            raise ConflictError(
                title="Conflict in event schedules",
                detail=f"Event collides with existing events: {colliding_events}"
            )

        # Save event and return it
        ret = self.repository.save_event(group_id, event)

        if not ret:
            raise Exception("Failed to group event")

        if not event.poll:
            return ret

        poll_id: str = self.repository.save_poll(
            group_id, event.creator_id, ret.id, event.poll)

        ret.poll = self.repository.get_poll(poll_id)
        if not ret.poll:
            raise Exception("Failed to save event poll")

        return ret

    def update_event(self, group_id: str, event_id: str, event: EventDTO) -> EventReturn:
        """
        Update an existing event in a group
        """
        # Check if group exists
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        # Check if event exists
        existing_event = self.repository.get_event(group_id, event_id)

        if not existing_event:
            raise NotFoundError(
                f"Event with id {event_id} not found in group {group_id}")

        # Check if event updater is a member of the group
        members = self.repository.get_group_members(group_id)
        member_ids = [member.user_id for member in members]

        if event.creator_id not in member_ids:
            raise AuthenticationError(
                f"User with id {event.creator_id} is not a member of group {group_id}"
            )

        if existing_event.date != event.date:
            if event.date < datetime.datetime.now():
                raise ValidationError(
                    title="Invalid event date",
                    detail="Event date cannot be in the past"
                )

        # Check for colliding events
        colliding_events = self.repository.find_group_colliding_events(
            group_id, event.date, event.start_hour, event.end_hour
        )

        colliding_events = [e for e in colliding_events if e.id != event_id]

        if colliding_events:
            raise ConflictError(
                title="Conflict in event schedules",
                detail=f"Event collides with existing events: {colliding_events}"
            )

        # Update event and return it
        ret = self.repository.update_event(group_id, event_id, event)

        if not ret:
            raise Exception("Failed to update group event")

        return ret

    def get_events(self, group_id: str) -> list[EventReturn]:
        """
        Get all events for a group
        """
        # Check if group exists
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        # Return all events for the group
        return self.repository.get_events(group_id)

    def get_event(self, group_id: str, event_id: str) -> EventReturn:
        """
        Get a specific event from a group
        """
        # Check if group exists
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        # Get event
        event = self.repository.get_event(group_id, event_id)

        if not event:
            raise NotFoundError(
                f"Event with id {event_id} not found in group {group_id}")

        event.poll = self.repository.get_poll_by_event_id(event_id)

        return event

    def delete_event(self, group_id: str, event_id: str) -> None:
        """
        Delete an event from a group
        """
        # Check if group exists
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        # Check if event exists
        event = self.repository.get_event(group_id, event_id)

        if not event:
            raise NotFoundError(
                f"Event with id {event_id} not found in group {group_id}")

        # Delete event
        self.repository.delete_event(group_id, event_id)

    def put_vote(self, vote: VoteDTO) -> PollReturn:
        """
        Save a vote for a poll option
        """
        poll = self.repository.get_poll(vote.poll_id)
        if not poll:
            raise NotFoundError(f"Poll with id {vote.poll_id} not found")

        self.repository.delete_poll_vote(vote.poll_id, vote.user_id)
        self.repository.save_poll_vote(vote)

        poll.votes = self.repository.get_poll_votes(vote.poll_id)

        return poll

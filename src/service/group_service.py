from abc import ABCMeta, abstractmethod
import logging
from os import getenv
from typing import Optional

from models.errors.errors import AuthenticationError, BadGatewayError, ConflictError, NotFoundError
from models.group import GroupDTO, GroupReturn
from models.member import Member
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

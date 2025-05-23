from abc import ABCMeta, abstractmethod
from typing import Optional

from models.errors.errors import NotFoundError
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.routine import RoutineDTO, RoutineReturn
from repository.group_repository import GroupRepository, IGroupRepository


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
    def save_routine(self, group_id: str, routine: RoutineDTO) -> list[RoutineReturn]:
        pass
    
    @abstractmethod
    def get_routines(self, group_id: str) -> list[RoutineReturn]:
        pass


class GroupService(IGroupService):
    def __init__(self, repository: Optional[IGroupRepository] = None):
        self.repository = repository or GroupRepository()

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


    def save_routine(self, group_id: str, routine: RoutineDTO) -> list[RoutineReturn]:
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        self.repository.save_routine(group_id, routine)
        
        return self.repository.get_routines(group_id)

    
    def get_routines(self, group_id: str) -> list[RoutineReturn]:
        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        return self.repository.get_routines(group_id)

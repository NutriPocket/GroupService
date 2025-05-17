from abc import ABCMeta, abstractmethod
from typing import Optional

from models.errors.errors import NotFoundError, ValidationError
from models.group import GroupDTO, GroupReturn
from models.member import Member
from repository.group_repository import GroupRepository, IGroupRepository
from uuid import UUID


def _validate_uuid(uuid: str, **kwargs) -> None:
    def throw() -> None:
        raise ValidationError(
            title=f"Invalid UUID",
            detail=f"{kwargs['name']} must be a valid UUID version 4"
        )

    if len(uuid) != 36:
        throw()

    try:
        UUID(uuid, version=4)
    except ValueError:
        throw()


def _validate_group(group: GroupDTO) -> None:
    if len(group.name) > 64:
        raise ValidationError(
            title="Group name is too long",
            detail="Group name must be less than 64 characters"
        )

    if len(group.description) > 512:
        raise ValidationError(
            title="Group description is too long",
            detail="Group description must be less than 512 characters"
        )

    _validate_uuid(group.owner_id, name="Group owner id")


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


class GroupService(IGroupService):
    def __init__(self, repository: Optional[IGroupRepository] = None):
        self.repository = repository or GroupRepository()

    def save_group(self, group: GroupDTO) -> GroupReturn:
        _validate_group(group)

        ret = self.repository.save_group(group)

        if not ret:
            raise Exception("Failed to save group")

        return ret

    def get_group(self, group_id: str) -> GroupReturn:
        _validate_uuid(group_id, name="Group id")

        ret = self.repository.get_group(group_id)

        if not ret:
            raise NotFoundError(f"Group with id {group_id} not found")

        return ret

    def get_user_groups(self, user_id: str) -> list[GroupReturn]:
        _validate_uuid(user_id, name="User id")

        return self.repository.get_user_groups(user_id)

    def save_member(self, group_id: str, user_id: str) -> list[Member]:
        _validate_uuid(user_id, name="User id")
        _validate_uuid(group_id, name="Group id")

        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        self.repository.save_member(group_id, user_id)
        return self.repository.get_group_members(group_id)

    def get_group_members(self, group_id: str) -> list[Member]:
        _validate_uuid(group_id, name="Group id")

        group = self.get_group(group_id)

        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")

        return self.repository.get_group_members(group_id)

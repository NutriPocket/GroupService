from abc import ABCMeta, abstractmethod
from typing import Any, Optional
from uuid import uuid4
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError
from database.database import engine
from models.errors.errors import EntityAlreadyExistsError
from models.group import GroupDTO, GroupReturn
from models.member import Member


class IGroupRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_group(self, group: GroupDTO) -> Optional[GroupReturn]:
        pass

    @abstractmethod
    def get_group(self, group_id: str) -> Optional[GroupReturn]:
        pass

    @abstractmethod
    def get_user_groups(self, user_id: str) -> list[GroupReturn]:
        pass

    @abstractmethod
    def save_member(self, group_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    def get_group_members(self, group_id: str) -> list[Member]:
        pass


class GroupRepository(IGroupRepository):
    def __init__(self, engine_: Optional[Engine] = None):
        self.engine = engine_ or engine

    def save_group(self, group: GroupDTO) -> Optional[GroupReturn]:
        query = text(
            """
            INSERT INTO groups (id, name, description, owner_id)
            VALUES (:id, :name, :description, :owner_id)
            RETURNING id, name, description, owner_id, created_at, updated_at
            """
        )

        params: dict[str, Any] = {
            "id": str(uuid4()),
            "name": group.name,
            "description": group.description,
            "owner_id": group.owner_id
        }

        ret = None

        with self.engine.begin() as connection:
            ret = connection.execute(query, params).fetchone()

        self.save_member(params["id"], group.owner_id)

        if ret:
            return GroupReturn(**ret._mapping)

    def get_group(self, group_id: str) -> Optional[GroupReturn]:
        query = text(
            """
            SELECT id, name, description, owner_id, created_at, updated_at
            FROM groups
            WHERE id = :group_id
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchone()

        if result:
            return GroupReturn(**result._mapping)

    def get_user_groups(self, user_id: str) -> list[GroupReturn]:
        query = text(
            """
            SELECT g.id, g.name, g.description, g.owner_id, g.created_at, g.updated_at
            FROM groups g
            JOIN group_members m ON g.id = m.group_id
            WHERE m.user_id = :user_id
            """
        )

        params: dict[str, Any] = {
            "user_id": user_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        return [GroupReturn(**row._mapping) for row in result]

    def save_member(self, group_id: str, user_id: str) -> None:
        query = text(
            """
            INSERT INTO group_members (group_id, user_id)
            VALUES (:group_id, :user_id)
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id
        }

        try:
            with self.engine.begin() as connection:
                connection.execute(query, params)

        except IntegrityError:
            raise EntityAlreadyExistsError(
                title="Member already exists",
                detail=f"User {user_id} is already a member of group {group_id}"
            )

    def get_group_members(self, group_id: str) -> list[Member]:
        query = text(
            """
            SELECT user_id
            FROM group_members
            WHERE group_id = :group_id
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        return [Member(**row._mapping) for row in result]

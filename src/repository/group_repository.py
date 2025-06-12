from abc import ABCMeta, abstractmethod
from tkinter import W
from typing import Any, Optional
from uuid import uuid4
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError
from database.database import engine
from models.errors.errors import EntityAlreadyExistsError, NotFoundError
from models.event import EventDTO, EventReturn
from models.group import GroupDTO, GroupReturn
from models.member import Member
from models.routine import RoutineDTO, RoutineReturn, Schedule
from models.poll import Option, PollDTO, PollReturn, VoteDTO
from datetime import datetime


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

    @abstractmethod
    def save_routine(self, group_id: str, routine: RoutineDTO) -> None:
        pass

    @abstractmethod
    def get_routines(self, group_id: str) -> list[RoutineReturn]:
        pass

    @abstractmethod
    def get_user_groups_routines_schedules(self, users: list[str]) -> list[Schedule]:
        pass

    @abstractmethod
    def save_event(self, group_id: str, event: EventDTO) -> Optional[EventReturn]:
        pass

    @abstractmethod
    def get_event(self, group_id: str, event_id: str) -> Optional[EventReturn]:
        pass

    @abstractmethod
    def update_event(self, group_id: str, event_id: str, event: EventDTO) -> Optional[EventReturn]:
        pass

    @abstractmethod
    def get_events(self, group_id: str) -> list[EventReturn]:
        pass

    @abstractmethod
    def delete_event(self, group_id: str, event_id: str) -> None:
        pass

    @abstractmethod
    def find_group_colliding_events(self, group_id: str, date: datetime, start_hour: int, end_hour: int) -> list[EventReturn]:
        pass

    @abstractmethod
    def save_poll(self, group_id: str, creator_id: str, event_id: str, poll: PollDTO) -> str:
        """Create a new poll for a group and return the poll ID"""
        pass

    @abstractmethod
    def save_poll_vote(self, vote: VoteDTO) -> None:
        """Save a user's vote for a poll option"""
        pass

    @abstractmethod
    def delete_poll_vote(self, poll_id: str, user_id: str) -> None:
        """Delete a user's vote for a poll option"""
        pass

    @abstractmethod
    def get_poll_votes(self, poll_id: str) -> dict[int, int]:
        """Get vote counts for each option in a poll"""
        pass

    @abstractmethod
    def get_poll(self, poll_id: str) -> Optional[PollReturn]:
        """Get a poll with its options and votes"""
        pass

    @abstractmethod
    def get_poll_by_event_id(self, event_id: str) -> Optional[PollReturn]:
        """Get a poll associated with a specific event"""
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
            SELECT user_id, created_at
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

    def save_routine(self, group_id: str, routine: RoutineDTO) -> None:
        query = text(
            """
            INSERT INTO group_routines (id, group_id, name, description, day, start_hour, end_hour, creator_id)
            VALUES (:id, :group_id, :name, :description, :day, :start_hour, :end_hour, :creator_id)
            """
        )

        params: dict[str, Any] = {
            "id": str(uuid4()),
            "group_id": group_id,
            "name": routine.name,
            "description": routine.description,
            "day": routine.day,
            "start_hour": routine.start_hour,
            "end_hour": routine.end_hour,
            "creator_id": routine.creator_id
        }

        with self.engine.begin() as connection:
            connection.execute(query, params)

    def get_routines(self, group_id: str) -> list[RoutineReturn]:
        query = text(
            """
            SELECT id, group_id, name, description, day, start_hour, end_hour, created_at, updated_at, creator_id
            FROM group_routines
            WHERE group_id = :group_id
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        return [RoutineReturn(**row._mapping) for row in result]

    def get_user_groups_routines_schedules(self, users: list[str]) -> list[Schedule]:
        query = text(
            """
            SELECT day, start_hour, end_hour
            FROM group_members gm
            JOIN group_routines gr ON gm.group_id = gr.group_id
            WHERE creator_id IN :users
            """
        )

        params: dict[str, Any] = {
            "users": tuple(users)
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        return [Schedule(**row._mapping) for row in result]

    def save_event(self, group_id: str, event: EventDTO) -> Optional[EventReturn]:
        """Save a new event for a group"""
        query = text(
            """
            INSERT INTO group_events (id, group_id, creator_id, name, description, date, start_hour, end_hour)
            VALUES (:id, :group_id, :creator_id, :name, :description, :date, :start_hour, :end_hour)
            RETURNING id, group_id, creator_id, name, description, date, start_hour, end_hour, created_at, updated_at
            """
        )

        params: dict[str, Any] = {
            "id": str(uuid4()),
            "group_id": group_id,
            "creator_id": event.creator_id,
            "name": event.name,
            "description": event.description,
            "date": event.date,
            "start_hour": event.start_hour,
            "end_hour": event.end_hour
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchone()

        if result:
            return EventReturn(**result._mapping)

    def get_event(self, group_id: str, event_id: str) -> Optional[EventReturn]:
        """Get a specific event by ID for a group"""
        query = text(
            """
            SELECT id, group_id, creator_id, name, description, date, start_hour, end_hour, created_at, updated_at
            FROM group_events
            WHERE group_id = :group_id AND id = :event_id
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id,
            "event_id": event_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchone()

        if result:
            return EventReturn(**result._mapping)
        return None

    def update_event(self, group_id: str, event_id: str, event: EventDTO) -> Optional[EventReturn]:
        """Update an existing event"""
        query = text(
            """
            UPDATE group_events
            SET name = :name,
                description = :description,
                date = :date,
                start_hour = :start_hour,
                end_hour = :end_hour,
                updated_at = CURRENT_TIMESTAMP
            WHERE group_id = :group_id AND id = :event_id
            RETURNING id, group_id, creator_id, name, description, date, start_hour, end_hour, created_at, updated_at
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id,
            "event_id": event_id,
            "name": event.name,
            "description": event.description,
            "date": event.date,
            "start_hour": event.start_hour,
            "end_hour": event.end_hour
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchone()

        if result:
            return EventReturn(**result._mapping)
        return None

    def get_events(self, group_id: str) -> list[EventReturn]:
        """Get all events for a group"""
        query = text(
            """
            SELECT id, group_id, creator_id, name, description, date, start_hour, end_hour, created_at, updated_at
            FROM group_events
            WHERE group_id = :group_id
            ORDER BY date, start_hour
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        return [EventReturn(**row._mapping) for row in result]

    def delete_event(self, group_id: str, event_id: str) -> None:
        """Delete an event from a group"""
        query = text(
            """
            DELETE FROM group_events
            WHERE group_id = :group_id AND id = :event_id
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id,
            "event_id": event_id
        }

        with self.engine.begin() as connection:
            connection.execute(query, params)

    def find_group_colliding_events(self, group_id: str, date: datetime, start_hour: int, end_hour: int) -> list[EventReturn]:
        """Find events that collide with a new event being created"""
        query = text(
            """
            SELECT id, group_id, creator_id, name, description, date, start_hour, end_hour, created_at, updated_at
            FROM group_events
            WHERE group_id = :group_id AND date = :date
            AND (
                (start_hour <= :end_hour AND end_hour >= :start_hour)
            )
            """
        )

        params: dict[str, Any] = {
            "group_id": group_id,
            "date": date,
            "start_hour": start_hour,
            "end_hour": end_hour
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        return [EventReturn(**row._mapping) for row in result] if result else []

    def save_poll(self, group_id: str, creator_id: str, event_id: str, poll: PollDTO) -> str:
        """Create a new poll for a group and return the poll ID"""
        # Insert the poll
        query = text(
            """
            INSERT INTO poll (id, group_id, creator_id, event_id, question)
            VALUES (:id, :group_id, :creator_id, :event_id, :question)
            RETURNING id
            """
        )

        poll_id = str(uuid4())
        params: dict[str, Any] = {
            "id": poll_id,
            "group_id": group_id,
            "creator_id": creator_id,
            "question": poll.question,
            "event_id": event_id
        }

        option_query = text(
            """
            INSERT INTO poll_options (id, poll_id, option_text)
            VALUES (:id, :poll_id, :option_text)
            """
        )

        with self.engine.begin() as connection:
            connection.execute(query, params)

            # Insert options
            for option in poll.options:
                option_params: dict[str, Any] = {
                    "id": option.id,
                    "poll_id": poll_id,
                    "option_text": option.text
                }

                connection.execute(option_query, option_params)

        return poll_id

    def save_poll_vote(self, vote: VoteDTO) -> None:
        """Save a user's vote for a poll option"""
        query = text(
            """
            INSERT INTO poll_votes (poll_id, user_id, option_id)
            VALUES (:poll_id, :user_id, :option_id)
            ON CONFLICT (poll_id, user_id, option_id) 
            DO UPDATE SET created_at = CURRENT_TIMESTAMP
            """
        )

        params: dict[str, Any] = {
            "poll_id": vote.poll_id,
            "user_id": vote.user_id,
            "option_id": vote.option_id
        }

        with self.engine.begin() as connection:
            connection.execute(query, params)

    def delete_poll_vote(self, poll_id: str, user_id: str) -> None:
        """Delete a user's vote for a poll option"""
        query = text(
            """
            DELETE FROM poll_votes
            WHERE poll_id = :poll_id AND user_id = :user_id
            """
        )

        params: dict[str, Any] = {
            "poll_id": poll_id,
            "user_id": user_id
        }

        with self.engine.begin() as connection:
            connection.execute(query, params)

    def get_poll_votes(self, poll_id: str) -> dict[int, int]:
        """Get vote counts for each option in a poll"""
        query = text(
            """
            SELECT option_id, COUNT(*) as vote_count
            FROM poll_votes
            WHERE poll_id = :poll_id
            GROUP BY option_id
            """
        )

        params: dict[str, Any] = {
            "poll_id": poll_id
        }

        with self.engine.begin() as connection:
            result = connection.execute(query, params).fetchall()

        # Convert to dictionary of option_id -> count
        return {int(row.option_id): row.vote_count for row in result}

    def get_poll(self, poll_id: str) -> Optional[PollReturn]:
        """Get a poll with its options and votes"""
        query = text(
            """
            SELECT id, group_id, creator_id, question, created_at
            FROM poll
            WHERE id = :poll_id
            """
        )

        params: dict[str, Any] = {
            "poll_id": poll_id
        }

        options_query = text(
            """
                SELECT id, option_text, created_at
                FROM poll_options
                WHERE poll_id = :poll_id
                """
        )

        with self.engine.begin() as connection:
            poll_result = connection.execute(query, params).fetchone()

            if not poll_result:
                return None

            # Get options

            options_result = connection.execute(
                options_query, {"poll_id": poll_id}).fetchall()

            options = [
                Option(
                    id=row.id,
                    text=row.option_text,
                    created_at=row.created_at
                ) for row in options_result
            ]

            # Get vote counts
            votes = self.get_poll_votes(poll_id)

            # Construct the PollReturn object
            return PollReturn(
                id=poll_result.id,
                question=poll_result.question,
                options=options,
                votes=votes,
                created_at=poll_result.created_at
            )

    def get_poll_by_event_id(self, event_id: str) -> Optional[PollReturn]:
        """Get a poll associated with a specific event"""
        # First, find the poll_id for this event
        poll_id_query = text(
            """
            SELECT id
            FROM poll
            WHERE event_id = :event_id
            """
        )

        params: dict[str, Any] = {
            "event_id": event_id
        }

        poll_id: str = ""
        with self.engine.begin() as connection:
            poll_id_result = connection.execute(
                poll_id_query, params).fetchone()

            if not poll_id_result:
                return None

            poll_id = poll_id_result.id

        # Now get the poll details using the existing get_poll method
        return self.get_poll(poll_id)

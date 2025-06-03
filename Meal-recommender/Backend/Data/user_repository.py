from .base_repository import BaseRepository
from .database import DatabaseManager
from typing import List, Optional
from ..models.user import User

class UserRepository(BaseRepository):
    """Repository for managing user data in the database."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_all(self) -> List[User]:
        """Retrieve all users from the database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute ("SELECT * FROM users")

            rows = cursor.fetchall()
            return [User(
                id=row['id'],
                prefered_flavors=row['prefered_flavors'].split(',') if row['prefered_flavors'] else [],
                prefered_types=row['prefered_types'].split(',') if row['prefered_types'] else [],
                dietary_restrictions=row['dietary_restrictions'].split(',') if row['dietary_restrictions'] else []
            ) for row in rows]

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))

            row = cursor.fetchone()
            if row:
                return User(
                    id=row['id'],
                    prefered_flavors=row['prefered_flavors'].split(',') if row['prefered_flavors'] else [],
                    prefered_types=row['prefered_types'].split(',') if row['prefered_types'] else [],
                    dietary_restrictions=row['dietary_restrictions'].split(',') if row['dietary_restrictions'] else []
                )
            return None

    def add(self, user: User) -> int:
        """Add a new user to the database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (id, prefered_flavors, prefered_types, dietary_restrictions) VALUES (?, ?, ?, ?)",
                (user.id, ','.join(user.prefered_flavors) if user.prefered_flavors else None,
                 ','.join(user.prefered_types) if user.prefered_types else None,
                 ','.join(user.dietary_restrictions) if user.dietary_restrictions else None)
            )
            conn.commit()
            return user.id

    def update(self, user: User) -> bool:
        """Update an existing user in the database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "UPDATE users SET prefered_flavors = ?, prefered_types = ?, dietary_restrictions = ? WHERE id = ?",
                (','.join(user.prefered_flavors) if user.prefered_flavors else None,
                 ','.join(user.prefered_types) if user.prefered_types else None,
                 ','.join(user.dietary_restrictions) if user.dietary_restrictions else None,
                 user.id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
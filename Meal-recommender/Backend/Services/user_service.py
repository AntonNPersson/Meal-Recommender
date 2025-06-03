from Backend.Data.base_repository import BaseRepository
from Backend.Data.user_repository import UserRepository
from Backend.Data.database import DatabaseManager
from Backend.models.user import User
import uuid
import os

class UserService:
    def __init__(self, user_repository: BaseRepository = None):
        if user_repository is None:
            db_manager = DatabaseManager()
            user_repository = UserRepository(db_manager)
        self.user_repository = user_repository

    def get_or_create_cli_user(self) -> User:
        """
        Retrieve a user by ID or create a new one if it doesn't exist.
        """
        user_id = self._get_or_create_cli_device_id()
        user = self.user_repository.get_by_id(user_id)
        if not user:
            user = User(id=user_id, prefered_flavors=[], prefered_types=[], dietary_restrictions=[])
            self.user_repository.add(user)
        return user
    
    def update_user_preferences(self, user_id: int, prefered_flavors: list = None, 
                             prefered_types: list = None, dietary_restrictions: list = None) -> User:
        """
        Update user preferences and return the updated user.
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")
        
        if prefered_flavors is not None:
            user.prefered_flavors = prefered_flavors
        if prefered_types is not None:
            user.prefered_types = prefered_types
        if dietary_restrictions is not None:
            user.dietary_restrictions = dietary_restrictions
        
        self.user_repository.update(user)
        return user
    
    def _get_or_create_cli_device_id(self) -> int:
        device_file = "device_id.txt"
        
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                return int(f.read().strip())
        else:
            device_id = uuid.uuid4().int & (1 << 31) - 1
            with open(device_file, 'w') as f:
                f.write(str(device_id))
            return device_id
        
    def has_cli_device_id(self) -> bool:
        """
        Check if the CLI device ID file exists.
        """
        return os.path.exists("device_id.txt")
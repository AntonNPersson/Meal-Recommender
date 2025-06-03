from abc import ABC, abstractmethod

class BaseRepository(ABC):
    """
    Abstract base class for repository pattern.
    Defines the interface for data access operations.
    """

    @abstractmethod
    def get_all(self):
        """
        Retrieve all records from the repository.
        """
        pass

    @abstractmethod
    def get_by_id(self, id):
        """
        Retrieve a record by its ID.
        """
        pass

    @abstractmethod
    def add(self, item):
        """
        Add a new record to the repository.
        """
        pass

    @abstractmethod
    def update(self, item):
        """
        Update an existing record in the repository.
        """
        pass

    @abstractmethod
    def delete(self, id):
        """
        Delete a record by its ID.
        """
        pass
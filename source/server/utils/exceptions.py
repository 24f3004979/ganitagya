class DependencyClash(Exception):
    """Raised for Dependency issues with root node"""

    pass  # Simple exception modeling


class UserExists(Exception):
    pass  # Modify for reasoning inside the application


class UserDoesNotExist(Exception):
    pass  # Raised for login proceeding example with non-existing user


class NotValidQuestion(Exception):
    pass  # Not Valid questions


class WrongInputProvided(Exception):
    pass

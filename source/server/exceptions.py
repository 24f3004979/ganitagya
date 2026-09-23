'''
Custom Excpetion Listing for this application
'''

class DependencyClash(Exception):
    '''Raised for Dependency issues with root node'''
    pass  # Simple exception modeling

class UserExists(Exception):
    pass # Modify for reasoning inside the application

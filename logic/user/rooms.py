from .__init__ import *


# application user
class Room:
    """
    Rooms manipulation class.

    * profile - Login profile.
    * target_account - Room user account
    """
    def __init__(self, profile: dict, target_account: dict):
        self.profile = profile
        self.target_account = target_account

    def new(self):
        pass

    def privacy(self):
        pass

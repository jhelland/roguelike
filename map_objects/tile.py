
class Tile:
    """
    Map tile. May or may not be blocked, block player view, etc.
    """
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # default: if tile is blocked, it blocks fov sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        self.explored = False

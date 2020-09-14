
class Transform:

    def __init__( self, position, rotation, scale):
        """
                            2D    or   3D
        :param position:    Vector2 or Vector3 position
        :param rotation:    float   or Vector3 rotation
        :param scale:       Vector2 or Vector3 scale
        """
        self.position = position
        self.rotation = rotation
        self.scale = scale

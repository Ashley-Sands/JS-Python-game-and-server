
class Rect:

    def __init__( self, left, right, top, bottom ):

        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

        self.width = 0
        self.height = 0

        self.set(left, right, top, bottom)

    def set( self, left, right, top, bottom ):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        self.width = abs( right - left )
        self.height = abs( top - bottom )

    def set_vect2( self, top_left, bottom_right ):
        self.set( top_left.x, bottom_right.x, top_left.y, bottom_right.y )

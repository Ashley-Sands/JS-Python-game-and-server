
export class Bounds
{
    constructor(left = -1, right = 1, top = 1, bottom = -1)
    {
        this.left = left
        this.top = top
        this.bottom = bottom
        this.right = right
    }

    Contains( position )
    {
        return position.x >= this.left && position.x <= this.right &&
               position.y >= this.bottom && position.y <= this.top
    }

    SetBounds( left, right, top, bottom )
    {
        this.left = left
        this.top = top
        this.bottom = bottom
        this.right = right
    }
}
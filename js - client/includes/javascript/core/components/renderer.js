
export class Renderer
{
    constructor()
    {
        this.renderFunct = null
    }

    Render(ctx)
    {
        if ( this.renderFunct == null )
            return
            
        this.renderFunct( ctx )

    }

}
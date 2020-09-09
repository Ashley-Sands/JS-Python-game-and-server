
export class Renderer
{
    constructor()
    {
        this.preRenderFunct = null
        this.renderFunct = null
    }

    Render(ctx)
    {
        if ( this.renderFunct == null )
            return

        if ( this.preRenderFunct != null )
            this.preRenderFunct( ctx )

        this.renderFunct( ctx )

    }

}

// Im not sure why but if i import this outside the function i get 
// Cannot access 'ManagerObject' be for initialization.
export class Imports
{
    static __viewport = null;

    static get Viewport(){ return Imports.__viewport }

    static async Load()
    {
        var viewport = await import("./core/managers/viewport.js");

        await viewport

        Imports.__viewport = viewport.Viewport

    }

}

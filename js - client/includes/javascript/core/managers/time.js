import {ManagerObject} from "../objects/baseObject.js"

export class Time extends ManagerObject
{
    constructor( fps )
    {
        super( "timeManager" )

        this.__lastTickTime = 0         // ms
        
        this.__delta = 0                // ms
        this.__timeSinceStartUp = 0     // ms

        this.targetFPS = fps
        this.targetUpdateIntervals = 1000 / fps

        this.frameTime = -1
        this.nextFrameTime = -1

        // FPS counter
        this.rawFPS = 0              
        this.FPS = 0                

        this.fpsSampleIntervals = 100   // ms
        this.fpsCurrentTime = 0
        this.fpsAccum = 0

        // min and max FPS are both based on the raw fps.
        this.minFPS = Infinity
        this.maxFPS = -Infinity

    }
    
    get MS_IN_SEC() { return 1000 }

    get deltaMs()
    {
        return this.__delta
    }

    get delta()
    {
        return this.__delta / this.MS_IN_SEC
    }

    get nowMs()
    {
        return Date.now()
    }

    get now()
    {
        return Date.now() / this.MS_IN_SEC 
    }

    get timeSinceStartUpMs()
    {
        return this.__timeSinceStartUp
    }

    get timeSinceStartUp()
    {
        return this.__timeSinceStartUp / this.MS_IN_SEC
    }

    get timeTillNextUpdate()
    {
        
        return this.nextFrameTime - Date.now()
    }

    SetFPS( fps )
    {
        this.targetFPS = fps
        this.targetUpdateIntervals = 1000 / fps
    }

    PreTick(){

        if ( this.frameTime == -1 )
            this.frameTime = Date.now()
        else
            this.frameTime = this.nextFrameTime

        this.nextFrameTime = this.frameTime + this.targetUpdateIntervals
        
    }

    Tick()
    {

        var now = Date.now()

        // prevent an extreamly high delta on the first tick.
        if ( this.__lastTickTime != 0 )
        {
            this.__delta = now - this.__lastTickTime
            this.rawFPS = 1000 / this.__delta
        
            this.fpsAccum++
            this.fpsCurrentTime += this.__delta

            if ( this.fpsCurrentTime >= this.fpsSampleIntervals )
            {
                this.FPS = this.fpsAccum / (this.fpsCurrentTime / 1000)
                this.fpsCurrentTime = this.fpsAccum = 0
            }

            this.minFPS = Math.min( this.minFPS, this.rawFPS )
            this.maxFPS = Math.max( this.maxFPS, this.rawFPS )
        }

        this.__lastTickTime = now
        this.__timeSinceStartUp += this.__delta

    }

    PostTick(){}

}

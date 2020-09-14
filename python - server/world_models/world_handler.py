import threading
import time

import common.DEBUG as DEBUG

_print = DEBUG.LOGS.print


class WorldHandler:

    def __init__( self, world, target_fps=30 ):

        self.thr_lock  = threading.Lock()
        self.main_loop = threading.Thread()

        self.__world = world

        self.__target_fps = 0
        self.__target_intervals = 0
        self.set_target_fps( target_fps )

        self.running = False

    def start( self ):

        with self.thr_lock:
            if self.running:
                return

        self.main_loop = threading.Thread( target=self.main, args=[ self.__target_intervals, self.__world ] )

        with self.thr_lock:
            self.running = True

    def set_target_fps( self, target_fps ):

        with self.thr_lock:
            if self.running:
                _print("Unable to set target fps. Scene running")
                return

        self.__target_fps = target_fps
        self.__target_intervals = 1.0 / target_fps

    def tick( self, delta_time ):
        pass

    def main( self, target_intervals, world ):
        """Main World Update Loop"""

        with self.thr_lock:
            running = self.running

        last_frame_time = 0
        delta_time = 0

        while running:

            if last_frame_time != 0:
                delta_time = time.time() - last_frame_time

            last_frame_time = time.time()

            with self.thr_lock:
                running = self.running

            self.tick( delta_time )

            if running:
                time.sleep( target_intervals )

import threading
import time
import world_models.world_client as world_client
import message_objects.send_data_raw_payload as raw_payload
import json

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


# TODO: Add not about make this support multiple worlds
class WorldHandler:

    __shared_received_queue = None      # servers received message queue
    __shared_send_data_queue = None     # servers send data queue (pre packet/message)

    def __init__( self, world, target_fps=30 ):

        self.running = False

        self.thr_lock  = threading.RLock()      # RLock allows the same thread access with out unlocking but blocks any other thread.
        self.main_loop = None
        self.apply_loop = None

        self.__world_lock = threading.Lock()    # used to prevent any data being applied during tick.
        self.__world = world

        self.__target_fps = 0
        self.__target_intervals = 0
        self.set_target_fps( target_fps )

    @staticmethod
    def set_shared_queue( recv_msg_queue, snd_msg_queue ):
        """Set the shared received message queue"""
        if WorldHandler.__shared_received_queue is None:
            WorldHandler.__shared_received_queue = recv_msg_queue
        else:
            _print( "unable to set receive queue, already set!", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

        if WorldHandler.__shared_send_data_queue is None:
            WorldHandler.__shared_send_data_queue = snd_msg_queue
        else:
            _print( "unable to set send queue, already set!", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

    def start( self ):

        with self.thr_lock:
            if self.running:
                return

        self.main_loop = threading.Thread( target=self.main, args=[ self.__target_intervals, self.__world ] )
        self.apply_loop = threading.Thread( target=self.apply_data, args=[ self.__world ] )

        with self.thr_lock:
            self.running = True

        self.__world.start()

        self.main_loop.start()
        self.apply_loop.start()

    def set_target_fps( self, target_fps ):

        with self.thr_lock:
            if self.running:
                _print("Unable to set target fps. Scene running")
                return

        self.__target_fps = target_fps
        self.__target_intervals = 1.0 / target_fps

    def client_join( self, base_socket ):

        _world_client = world_client.WorldClient( base_socket.client_socket, base_socket.client_id, f"Client {base_socket.client_id}",  )
        _world_client.set_world( self.__world )

    def client_exit( self, base_socket ):
        """ Completely removes the client from the simulation """
        w_client = self.__world.get_world_client( base_socket.client_socket )

        if w_client is None:
            return

        self.__world.client_leave( w_client )

    def tick_world( self, world, delta_time, tick, frame_time ): # tick is temp.
        """Ticks the world"""
        # 1. Receive data -> Apply data
        # 2. Lock World -> Tick frame -> collect data -> unlock world
        # 3. Send delta data to all clients, (that have kept to there agreement. TODO: <<)

        world.tick( delta_time )
        data = world.collect_data()

        raw_payload_obj = raw_payload.SendDataRawPayload( data, json.dumps, tick, frame_time )
        WorldHandler.__shared_send_data_queue.put( raw_payload_obj )

    def main( self, target_interval, world ):
        """Main World Update Loop"""

        with self.thr_lock:
            running = self.running

        # TODO: Add Time module
        last_frame_time = 0
        delta_time = 0
        tick = -1

        while running:

            tick += 1
            # _print("TICK", tick, "t", time.time() )

            with self.__world_lock: # Lock the world so that data is not applied during tick.

                this_tick_time = time.time()
                next_tick_time = this_tick_time + target_interval

                if last_frame_time != 0:
                    delta_time = this_tick_time - last_frame_time
                last_frame_time = this_tick_time

                self.tick_world( world, delta_time, tick, this_tick_time )  # tick is temp

            with self.thr_lock:
                running = self.running

            if running:
                sleep_length = next_tick_time - time.time()
                if sleep_length > 0:
                    time.sleep( sleep_length )

    def apply_data( self, world ):
        """Applies world frame data while world is not ticking."""

        with self.thr_lock:
            running = self.running

        while running:

            frame_data = WorldHandler.__shared_received_queue.get()

            with self.__world_lock:  # Wait until the word is not ticking to apply frame data.
                world.apply_data( frame_data.from_socket, frame_data.get() )

            with self.thr_lock:
                running = self.running

import socket
import asyncio



class ServerSocket:
    def __init__(self,server_addr):
        pass

    def __enter__(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        return self

    def __exit__(self):
        self._socket.close()

    async def __aenter__(self):
        return self.__aenter__()

    async def __aexit__(self):
        self.__exit__()

    async def send_data(self,data:bytes,address):
        # Try to eagerly send the data.
        num_sent = 0
        try:
            num_sent = self._socket.sendto(data,address)
            assert num_sent==len(data), "Datagram protocol forbids partial send."
            return
        except (BlockingIOError, InterruptedError) as e:
            pass

        # Could not send the data because socket is busy currently.
        # Add a callback when it becomes writeable.
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        handle = loop.add_writer(self._socket,self._send_data_writer_cb,fut,data,address)
        fut.add_done_callback(lambda _: loop.remove_writer(self._socket))

        await fut

    def _send_data_writer_cb(self,future:asyncio.Future,data,address):
        # If  remove_writer was not called quickly enough.
        if future.done():
            return
        try:
            self._socket.sendto(data,address)
        except (BlockingIOError, InterruptedError):
            # Wait until the socket become writeable again
            return
        except (SystemExit, KeyboardInterrupt):
            # Do not catch these exceptions.
            raise
        except BaseException as exc:
            # Other socket errors.
            future.set_exception(exc)
            return

        future.set_result(None)

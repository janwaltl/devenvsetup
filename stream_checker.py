#!/usr/bin/env python3
from __future__ import print_function, annotations
from collections import deque

import dataclasses

from typing import DefaultDict, Dict, Iterable, Deque, List

from utils import Color, colored


@dataclasses.dataclass(frozen=True)
class Packet:
    msg: bytes
    timestamp_ms: int


class StreamChecker:
    """Class capable of comparing two streams for equality with time constraints.

    Online algorithm.
    """

    def __init__(self, timeout_ms: int = 1_000) -> None:
        """Construct a new checker.

        Parameters
        ----------
        timeout_ms : int
            Timeout in milliseconds in which each expected datagram must be received.
        """

        self._expected: Deque[Packet] = deque()
        """Expected datagrams, indexed by the message, list of timestamps is kept sorted."""
        self._timeout_ms = timeout_ms
        """How much can expected and received timestamps differ, milliseconds."""
        self._confirmed: List[Packet] = []
        """Confirmed stream, filled from self._expected after confirmation."""

    def add_expected(self, packet: Packet):
        """Add to the expected stream with its send timestamp.

        Parameters
        ----------
        packet : Packet
            Stream packet expected to be received in
            `datagram.timestamp_ms+self._timeout_ms`.
        """
        exp = self._expected
        if len(exp) > 0 and exp[-1].timestamp_ms > packet.timestamp_ms:
            # See discussing in self.add_received()
            raise AssertionError("OUT OF ORDER STREAM PACKETS ARE NOT SUPPORTED.")

        exp.append(packet)

    def add_received(self, packet: Packet):
        """Add received datagram

        Parameters
        ----------
        packet : Packet
            Received datagram packet.

        Returns
        -------
        bool:
            Whether the received packet has been expected and is in time.
        """

        recv_time = packet.timestamp_ms
        to_confirm = packet.msg
        while len(to_confirm) > 0:
            expected = self._expected.popleft()

            if recv_time - expected.timestamp_ms > self._timeout_ms:
                raise NotImplementedError("Stream late")

            e_n = len(expected.msg)
            r_n = len(to_confirm)

            if e_n == r_n:
                if expected.msg != to_confirm:
                    raise NotImplementedError("Stream differs")
                to_confirm = []
            elif e_n > r_n:  # expected is longer stream->almost done
                if expected.msg[:r_n] != to_confirm:
                    raise NotImplementedError("Stream differs")
                self._expected.appendleft(
                    Packet(expected.msg[r_n:], expected.timestamp_ms)
                )
                to_confirm = []
            else:
                if expected.msg != to_confirm[:e_n]:
                    raise NotImplementedError("Stream differs")
                to_confirm = to_confirm[e_n:]

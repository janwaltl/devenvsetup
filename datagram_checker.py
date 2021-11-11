#!/usr/bin/env python3
from __future__ import annotations

import dataclasses

from typing import DefaultDict, Dict, Iterable, List

from utils import Color, colored


@dataclasses.dataclass(frozen=True)
class Packet:
    msg: bytes
    timestamp_ms: int


def _report_packet(packet: Packet, packet_type: str = "Packet") -> str:
    return "\n".join(
        [
            80 * "=",
            f"{packet_type}({packet.timestamp_ms}ms), payload:",
            80 * "-",
            packet.msg.decode("unicode_escape"),
            80 * "=",
        ]
    )


def _report_packets(packets: Iterable[Packet], packet_type: str = "Packet"):
    return "\n".join(map(lambda p: _report_packet(p, packet_type), packets))


class OnlineDatagramChecker:
    """Class capable of comparing two datagram streams for equality with time constraints.

    Compares two datagrams whether all expected and received telegrams can be matched
    with each other within a given timeout interval.
    If not, AssertionError is thrown with log of all datagrams.

    Online algorithm.

    """

    def __init__(self, timeout_ms: int = 1_000) -> None:
        """Construct a new checker.

        Parameters
        ----------
        timeout_ms : int
            Timeout in milliseconds in which each expected datagram must be received.
        """

        self._received: Dict[bytes, List[int]] = DefaultDict(lambda: [])
        """Received datagrams, indexed by the message, list of timestamps is kept sorted."""
        self._expected: Dict[bytes, List[int]] = DefaultDict(lambda: [])
        """Expected datagrams, indexed by the message, list of timestamps is kept sorted."""
        self._timeout_ms = timeout_ms
        """How much can expected and received timestamps differ, milliseconds."""
        self._confirmed: List[Packet] = []
        """Confirmed datagrams, unordered, filled from self._expected after confirmation."""

    def add_expected(self, packet: Packet):
        """Add expected datagram with its send timestamp.

        Parameters
        ----------
        packet : Packet
            Datagram packet expected to be received in
            `datagram.timestamp_ms+self._timeout_ms`.
        """
        exp = self._expected[packet.msg]
        if len(exp) > 0 and exp[-1] > packet.timestamp_ms:
            # See discussing in self.add_received()
            raise AssertionError("OUT OF ORDER DATAGRAMS ARE NOT SUPPORTED.")

        exp.append(packet.timestamp_ms)

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

        rcv = self._received[packet.msg]

        # There is no reasonable way how to check the stream if some packets
        # might arrive out of order.
        #   - Online algorithm is required.
        #   - We need a concept of "now" at the server,
        #     unordered UDP cannot provide that.
        if len(rcv) > 0 and rcv[-1] > packet.timestamp_ms:
            raise AssertionError("OUT OF ORDER DATAGRAMS ARE NOT SUPPORTED.")

        rcv.append(packet.timestamp_ms)
        return self._confirm_expected(packet.msg)

    def _reconstruct_packets(
        self, stored_packets: Dict[bytes, List[int]]
    ) -> Iterable[Packet]:
        for k, ts in stored_packets.items():
            yield from (Packet(k, t) for t in ts)

    def _report_failure(self, main_msg: str):
        raise AssertionError(
            "\n".join(
                [
                    "",  # Start on new line
                    colored(main_msg, Color.FAIL),
                    colored(
                        _report_packets(self._confirmed, "Confirmed packet"),
                        Color.OKGREEN,
                    ),
                    colored(
                        _report_packets(
                            self._reconstruct_packets(self._expected),
                            "Unconfirmed, still expected packet",
                        ),
                        Color.OKCYAN,
                    ),
                    colored(
                        _report_packets(
                            self._reconstruct_packets(self._received),
                            "Unconfirmed, received packet",
                        ),
                        Color.OKCYAN,
                    ),
                ]
            )
        )

    def _confirm_expected(self, msg: bytes):
        """Confirm all received packets so far, the must match

        The timestamps belong to send and received messages of the same content.
        Checks whether each message in `expected` can be matched with a
        separate message in `received` such that the timestamps are within
        `self._timeout_ms` of each other.
        Note, that each `received` msg must be used exactly once.

        Parameters
        ----------
        msg : bytes
            Message
        received : List[int]
            Received timestamps, sorted ascending.
        expected : List[int]
            Expected timestamps, sorted ascending.
        now : int
            Timestamp of now.
        Returns
        -------
        bool
            Whether the timestamps were matched with each other.
        """
        received = self._received[msg]
        expected = self._expected[msg]
        if len(received) > len(expected):
            self._report_failure(
                _report_packet(Packet(msg, received[-1]), "Unexpected Packet")
            )

        # Simple algorithm
        # Just sort the timestamps and match them from the start.
        #   = This greedy algorithm is correct and fast.
        #   = Lists are assumed to be sorted.
        for i, r in enumerate(received):
            e = expected[i]
            if (r - e) > self._timeout_ms:
                self._report_failure(_report_packet(Packet(msg, r), "Late Packet"))

        # Move all confirmed entries
        self._confirmed.extend(Packet(msg, t) for t in received)
        self._expected[msg] = expected[len(received) :]
        self._received[msg].clear()

    def check(self):
        """Whether all expected and received datagrams can be matched."""

        expected_counts = {k: len(v) for k, v in self._expected.items()}
        received_counts = {k: len(v) for k, v in self._received.items()}

        if expected_counts != received_counts:
            self._report_failure("MISSING Packets")

        for msg in expected_counts.keys():
            self._confirm_expected(msg)

#!/usr/bin/env python3

from dataclasses import dataclass
from enum import IntEnum, unique
from abc import ABC, abstractclassmethod, abstractmethod

from ipaddress import IPv4Address
import struct
from typing import ClassVar, Dict, Type

from __future__ import annotations

# Protocol:
#   - Type of packet, irrespective of direction
#   - Response type does not have to match request type
@unique
class PacketType(IntEnum):
#   - Reset the card
#   - Send setup data
#   - confirmed with Status - OK running or Error
    RESET_SETUP = 2
#   - Send Serial data
#       - contains channel field
#   - Confirmed only after full send
    SERIAL_DATA = 2
#   - Send UDP data
#   - Has src/dest IP,port pair
#   - Missing src indications DPRAM src
#   - Missing dest indicates DPRAM dest
    UDP_UNICAST = 3
#   - Think about support for this.
    UDP_BROADCAST = 3
    TCP_CONNECT = 3
    TCP_DISCONNECT = 3
    TCP_UNICAST = 3
#   - Response for received evens
#   - Has number of waiting events
    EVENT_SERIAL = 2
    EVENT_UDP_UNICAST = 2
    EVENT_TCP_CONNECT = 2
    EVENT_TCP_UNICAST = 2
    EVENT_TCP_DISCONNECT = 2
#   - Request Events
#   - Option to limit the answers
    REQ_EVENTS = 2
# Generic error response to a request
    ERROR = 2
# Generic OK message response to a request
# Contains timestamp
    OK = 2


# Request layout:
#   Header:
#   - reference
#   - enum type denoting the next bytes
#   Payload:
#   - just bytes

# At what stage are what types:
#   - ServerConnection
#       -send:
#           - accepts Typed request
#           - which can serialize itself into payload, has .ID
#           - adds ref
#       -receive:
#           - Receives bytes
#           - decode into a Response
#   - ServerConnection can pair request to responses through ref.
#       - Store a dict of ref->future that send waits on.
#       - response contains timestamp

class Request(ABC):
    _requests:Dict[Type,PacketType]=dict()

    def __init_subclass__(cls,req_type:PacketType,**kwargs) -> None:
        super().__init_subclass__(**kwargs)

        Request._requests[cls]=req_type

    @abstractmethod
    def serialize(self)->bytes:
        pass

    @classmethod
    def packet_type(cls)->PacketType:
        return Request._requests[cls]

class Response(ABC):
    _responses:Dict[PacketType,Type]=dict()

    def __init_subclass__(cls,req_type:PacketType,**kwargs) -> None:
        super().__init_subclass__(**kwargs)

        # Otherwise deserialization is ambiguous
        assert cls not in Response._responses, "Responses must have unique PacketType"

        Response._responses[req_type]=cls

    @abstractclassmethod
    def deserialize(cls)->Response:
        raise NotImplementedError("Subsclasses must implement their own deserialization")

class EventReq(Request,req_type=PacketType.REQ_EVENTS):
    def serialize(self) -> bytes:
        return  bytes() # Empty

class SerialDataReq(Request,req_type=PacketType.SERIAL_DATA):
    def __init__(self,msg:bytes,channel:int) -> None:
        assert channel>=0 and channel<=2, "0(DPRAM), 1, 2 channels are supported."

        super().__init__()

        self.channel=channel
        self.msg=msg

    def serialize(self) -> bytes:
        return struct.pack("<is",self.channel,self.msg)


@dataclass(eq=True,order=True,frozen=True)
class IpEndpoint:
    ip: IPv4Address | None
    port: int

    @staticmethod
    def backplane(port:int):
        return IpEndpoint(ip=None,port=port)

    def is_backplane(self):
        return self.ip is None

@dataclass(eq=True,order=True,frozen=True)
class Event:
    waiting_events:int

@dataclass(eq=True,order=True,frozen=True)
class EventSerial(Event):
    channel: int
    data: bytes

@dataclass(eq=True,order=True,frozen=True)
class EventIP(Event):
    src: IpEndpoint
    dest: IpEndpoint

@dataclass(eq=True,order=True,frozen=True)
class EventUDPUnicast(EventIP):
    data: bytes

@dataclass(eq=True,order=True,frozen=True)
class EventTCPConnect(EventIP):
    pass

@dataclass(eq=True,order=True,frozen=True)
class EventTCPUnicast(EventIP):
    data: bytes

@dataclass(eq=True,order=True,frozen=True)
class EventTCPDisconnect(EventIP):
    pass

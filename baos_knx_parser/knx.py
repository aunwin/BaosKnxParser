
from datetime import datetime

from . import struct  # precompiled bitstructs
from .const import TelegramType, TelegramPriority, APCI, TPCI


class KnxAddress(object):
    PHYSICAL_DELIMITER = '.'
    GROUP_DELIMITER = '/'

    def __init__(self, str=None, area=None, line=None, device=None, group=False):

        if str and (area or line or device):
            raise TypeError("Either set the address as string or as separated fields. Not both")

        if str:
            segments = str.split(KnxAddress.PHYSICAL_DELIMITER if not group else KnxAddress.GROUP_DELIMITER)
            self.area = segments[0]
            self.line = segments[1]
            self.device = segments[2]
        else:
            self.area = area
            self.line = line
            self.device = device

        self.group = group

    def __str__(self):
        return "{area}{delim}{line}{delim}{device}".format(
            area=self.area, line=self.line, device=self.device,
            delim=KnxAddress.PHYSICAL_DELIMITER if not self.group else KnxAddress.GROUP_DELIMITER
        )


class KnxBaseTelegram(object):

    def __init__(self, telegram_type=TelegramType.DATA, repeat=False, ack=False, priority=TelegramPriority.NORMAL, confirm=True, src=None, dest=None, hop_count=0, timestamp=None):
        self.timestamp = timestamp if timestamp else datetime.now()
        self.telegram_type = TelegramType(telegram_type)
        self.repeat = repeat
        self.ack = ack
        self.priority = TelegramPriority(priority)
        self.confirm = confirm
        self.src = src
        self.dest = dest
        self.hop_count = hop_count

    def __repr__(self):
        return """KnxExtendedTelegram(src='{src}', dest='{dest}', telegram_type={tt},
    repeat={repeat}, ack={ack}, priority={prio}, hop_count=0, timestamp={timestamp})""".format(tt=repr(self.telegram_type), prio=repr(self.priority), **self.__dict__)

    @property
    def tpdu(self):
        if self.payload:
            return self.payload[0]
        else:
            return None

    @property
    def apci(self):
        if not self.payload:
            return None

        apci_num, = struct.KNX_APCI.unpack(self.payload[0:3])
        return APCI(apci_num)

    @property
    def tpci(self):
        if not self.payload:
            return None

        tpci_num, = struct.KNX_TPCI.unpack(self.payload[0:2])
        return TPCI(tpci_num)

    @property
    def packet_count(self):
        if not self.payload:
            return None

        count, = struct.KNX_PACKET_NUMBER.unpack(self.payload[0:2])
        return count


class KnxStandardTelegram(KnxBaseTelegram):

    def __init__(self, payload_length=None, payload=bytes(), *args, **kwargs):
        super(KnxStandardTelegram, self).__init__(*args, **kwargs)

        if payload_length is not None and not len(payload) == payload_length:
            raise TypeError("Payload length mismatch")

        self.payload = payload
        self.payload_length = payload_length if payload_length is not None else len(payload)

    def __repr__(self):
        p = self.payload.hex()
        return """KnxStandardTelegram(src='{src}', dest='{dest}', telegram_type={tt},
    repeat={repeat}, ack={ack}, priority={prio}, hop_count=0, timestamp='{timestamp}',
    payload_length={payload_length}, payload=payload=bytes.fromhex('{p}'))""".format(tt=repr(self.telegram_type), prio=repr(self.priority), p=p, **self.__dict__)


class KnxExtendedTelegram(KnxBaseTelegram):

    def __init__(self, eff=bytes(), payload_length=None, payload=bytes(), *args, **kwargs):
        super(KnxExtendedTelegram, self).__init__(*args, **kwargs)
        self.eff = eff

        if payload_length is not None and not len(payload) == payload_length:
            raise TypeError("Payload length mismatch")

        self.payload = payload
        self.payload_length = payload_length if payload_length is not None else len(payload)

    def __repr__(self):
        eff = hex(self.eff)
        p = self.payload.hex()
        return """KnxExtendedTelegram(src='{src}', dest='{dest}', telegram_type={tt},
    repeat={repeat}, ack={ack}, priority={prio}, hop_count=0, timestamp='{timestamp}',
    eff=bytes.fromhex('{eff_hex}'), payload_length={payload_length}, payload=bytes.fromhex('{p}'))""".format(tt=repr(self.telegram_type), prio=repr(self.priority), p=p, eff_hex=eff, **self.__dict__)

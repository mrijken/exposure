import decimal
import logging
from fractions import Fraction
import decimal
import math
from typing import Dict, Literal, Optional, Union


logger = logging.getLogger(__name__)


def floor(n, signficant_digits):
    """
    >>> floor(1234, 2)
    1200
    >>> floor(0.1234, 3)
    0.123
    >>> floor(1.40010292921234, 2)
    1.4
    >>> floor(1234, 5)
    1234.0
    """
    x = math.floor(math.log10(n))
    n1 = n * 10 ** (signficant_digits - 1 - x)
    n2 = math.floor(n1)
    n3 = n2 * 10 ** -(signficant_digits - 1 - x)
    return round(n3, signficant_digits)


class Av:
    def __init__(self, stop: Fraction):
        self.precise = self.stop_to_fstop_precise(stop)
        self.fstop = self.stop_to_fstop(stop)
        self.stop = stop

    @classmethod
    def from_fstop(cls, fstop: Union[float, decimal.Decimal]):
        """
        >>> Av.from_fstop(decimal.Decimal("1.4"))
        Av f/1.4
        >>> Av.from_fstop(decimal.Decimal("1.4")).stop
        Fraction(1, 1)
        >>> Av.from_fstop(decimal.Decimal("22")).stop
        Fraction(9, 1)
        """
        return cls(stop=cls.fstop_to_stop(fstop))

    @classmethod
    def from_stop(cls, stop: Fraction):
        """
        >>> Av.from_stop(1)
        Av f/1.4
        >>> Av.from_stop(9)
        Av f/22
        """
        return cls(stop=stop)

    @classmethod
    def from_focal_length_and_diameter(cls, focal_length_in_mm: float, diameter_in_mm: float):
        """
        >>> Av.from_focal_length_and_diameter(10, 5)
        Av f/2.0

        """
        return cls.from_fstop(focal_length_in_mm / diameter_in_mm)

    @staticmethod
    def fstop_to_stop(fstop: Union[float, decimal.Decimal]) -> Fraction:
        """
        >>> Av.fstop_to_stop(1.4)
        Fraction(1, 1)
        >>> Av.fstop_to_stop(22)
        Fraction(9, 1)
        >>> Av.fstop_to_stop(1.7)
        Fraction(3, 2)
        >>> Av.fstop_to_stop(1.6)
        Fraction(4, 3)
        >>> Av.fstop_to_stop(1.8)
        Fraction(5, 3)
        >>> Av.fstop_to_stop(decimal.Decimal("1.8"))
        Fraction(5, 3)
        """
        stop = 2 * math.log(fstop, 10) / math.log(2, 10)
        return Fraction(stop).limit_denominator(3)

    @classmethod
    def stop_to_fstop(cls, stop: Fraction) -> decimal.Decimal:
        """
        >>> Av.stop_to_fstop(1)
        Decimal('1.4')
        >>> Av.stop_to_fstop(Fraction(5, 3))
        Decimal('1.7')
        >>> Av.stop_to_fstop(9)
        Decimal('22')
        """
        fstop_precise = cls.stop_to_fstop_precise(stop)
        return decimal.Decimal(str(floor(fstop_precise, 2)))

    @staticmethod
    def stop_to_fstop_precise(stop: Fraction) -> float:
        """
        >>> Av.stop_to_fstop_precise(1)
        1.4142135623730951
        """
        return math.sqrt(2) ** float(stop)

    def __repr__(self):
        return f"Av f/{self.fstop}"


class Sv:
    """
    >>> Sv.from_iso(100)
    Sv 100 ISO
    >>> Sv.from_iso(100).stop
    Fraction(0, 1)
    >>> Sv.from_stop(Fraction(0, 1))
    Sv 100 ISO
    >>> Sv.from_stop(Fraction(0, 1)).stop
    Fraction(0, 1)
    """

    def __init__(self, stop: Fraction):
        self.iso = 100 * 2 ** stop
        self.stop = stop.limit_denominator(3)

    @property
    def precise(self):
        return self.iso

    @classmethod
    def from_stop(cls, stop: Fraction):
        """
        >>> Sv.from_stop(Fraction(1, 1))
        Sv 200 ISO
        >>> Sv.from_stop(Fraction(2, 1))
        Sv 400 ISO
        """
        return cls(stop=stop)

    @classmethod
    def from_iso(cls, iso: Union[int, float]):
        """
        >>> Sv.from_iso(100)
        Sv 100 ISO
        >>> Sv.from_iso(400)
        Sv 400 ISO
        >>> Sv.from_iso(400).stop
        Fraction(2, 1)
        """
        return cls(stop=Fraction(math.log(iso / 100, 2)).limit_denominator(3))

    def __repr__(self) -> str:
        return f"Sv {self.iso} ISO"


class Tv:
    all_nominal_third_stops_from_min15 = [
        Fraction(1, 32000),
        Fraction(1, 25600),
        Fraction(1, 20000),
        Fraction(1, 16000),
        Fraction(1, 12800),
        Fraction(1, 10000),
        Fraction(1, 8000),
        Fraction(1, 6400),
        Fraction(1, 5000),
        Fraction(1, 4000),
        Fraction(1, 3200),
        Fraction(1, 2500),
        Fraction(1, 2000),
        Fraction(1, 1600),
        Fraction(1, 1250),
        Fraction(1, 1000),
        Fraction(1, 800),
        Fraction(1, 640),
        Fraction(1, 500),
        Fraction(1, 400),
        Fraction(1, 320),
        Fraction(1, 250),
        Fraction(1, 200),
        Fraction(1, 160),
        Fraction(1, 125),
        Fraction(1, 100),
        Fraction(1, 80),
        Fraction(1, 60),
        Fraction(1, 50),
        Fraction(1, 40),
        Fraction(1, 30),
        Fraction(1, 25),
        Fraction(1, 20),
        Fraction(1, 15),
        Fraction(1, 13),
        Fraction(1, 10),
        Fraction(1, 8),
        Fraction(1, 6),
        Fraction(1, 5),
        Fraction(1, 4),
        Fraction(1, 3),
        Fraction(10, 25),
        Fraction(1, 2),
        Fraction(10, 16),
        Fraction(10, 13),
        Fraction(1, 1),
        Fraction(13, 10),
        Fraction(16, 10),
        Fraction(2, 1),
        Fraction(25, 10),
        Fraction(3, 1),
        Fraction(4, 1),
        Fraction(5, 1),
        Fraction(6, 1),
        Fraction(8, 1),
        Fraction(10, 1),
        Fraction(13, 1),
        Fraction(15, 1),
        Fraction(20, 1),
        Fraction(25, 1),
        Fraction(30, 1),
    ]

    stop2time = {Fraction(-15) + Fraction(idx, 3): v for idx, v in enumerate(all_nominal_third_stops_from_min15)}
    time2stop = {v: Fraction(-15) + Fraction(idx, 3) for idx, v in enumerate(all_nominal_third_stops_from_min15)}

    def __init__(
        self,
        stop: Fraction,
    ):
        """"""
        self.stop = stop
        self.precise = 2 ** stop
        self.time = self.stop2time[stop]

    @classmethod
    def from_stop(cls, stop: Fraction):
        """
        >>> Tv.from_stop(1)
        Tv 2 sec
        >>> Tv.from_stop(Fraction(-1, 3))
        Tv 10/13 sec
        """
        return cls(stop=stop)

    @classmethod
    def from_time(cls, duration_in_sec: Fraction):
        """
        >>> Tv.from_time(Fraction(10, 13))
        Tv 10/13 sec
        >>> Tv.from_time(Fraction(10, 13)).stop
        Fraction(-1, 3)
        """

        return cls(cls.time2stop[duration_in_sec])

    def __repr__(self) -> str:
        return f"Tv {self.time} sec"


class Bv:
    """
    >>> Bv.from_foot_lamberts(1).stop
    Fraction(0, 1)
    >>> Bv.from_foot_lamberts(1)
    Bv 3.4 cd/m2
    >>> Bv.from_stop(3)
    Bv 27.4 cd/m2
    >>> Bv.from_candelas(109)
    Bv 109.6 cd/m2
    >>> Bv.from_candelas(109).stop
    Fraction(5, 1)
    """

    def __init__(self, stop: Fraction):
        self.stop = stop
        self.candelas = self.candelas_from_stop(stop)
        self.foot_lamberts = self.foot_lamberts_from_stop(stop)

    @classmethod
    def candelas_from_stop(cls, stop: Fraction):
        """
        >>> Bv.candelas_from_stop(0)
        3.4
        >>> Bv.candelas_from_stop(1)
        6.9
        """
        return round(2 ** stop * 3.4262591, 1)

    @classmethod
    def foot_lamberts_from_stop(cls, stop: Fraction):
        """
        >>> Bv.foot_lamberts_from_stop(0)
        1
        >>> Bv.foot_lamberts_from_stop(1)
        2
        """
        return 2 ** stop

    @classmethod
    def from_candelas(cls, candelas):
        """
        >>> Bv.from_candelas(3.4)
        Bv 3.4 cd/m2
        """
        K = 11.4
        stop = math.log2(candelas / (0.3 * K))
        return cls(Fraction(stop).limit_denominator(3))

    @classmethod
    def from_foot_lamberts(cls, foot_lamberts):
        """
        >>> Bv.from_foot_lamberts(1)
        Bv 3.4 cd/m2
        """
        stop = math.log2(foot_lamberts)
        return cls(Fraction(stop).limit_denominator(3))

    @classmethod
    def from_stop(cls, stop: Union[int, float, Fraction]):
        """
        >>> Bv.from_stop(Fraction(1, 1))
        Bv 6.9 cd/m2
        >>> Bv.from_stop(Fraction(2, 1))
        Bv 13.7 cd/m2
        """
        return cls(stop=stop)

    def __repr__(self) -> str:
        return f"Bv {self.candelas} cd/m2"


class Iv:
    """
    >>> Iv.from_foot_candles(25).stop
    Fraction(2, 1)
    >>> Iv.from_foot_candles(25)
    Iv 268.8 lux
    >>> Iv.from_stop(3)
    Iv 537.6 lux
    >>> Iv.from_lux(1076)
    Iv 1075.2 lux
    >>> Iv.from_lux(1076).stop
    Fraction(4, 1)
    """

    def __init__(self, stop: Fraction):
        self.stop = stop
        self.candles = self.foot_candles_from_stop(stop)
        self.lux = self.lux_from_stop(stop)

    @classmethod
    def foot_candles_from_stop(cls, stop: Fraction):
        """
        >>> Iv.foot_candles_from_stop(0)
        6.2
        >>> Iv.foot_candles_from_stop(1)
        12.5
        """
        return round(2 ** stop * 0.3 * 20.8, 1)

    @classmethod
    def lux_from_stop(cls, stop: Fraction):
        """
        >>> Iv.lux_from_stop(0)
        67.2
        >>> Iv.lux_from_stop(1)
        134.4
        """
        return round(2 ** stop * 0.3 * 224, 1)

    @classmethod
    def from_foot_candles(cls, foot_candled):
        """
        >>> Iv.from_foot_candles(25)
        Iv 268.8 lux
        """
        K = 20.8
        stop = math.log2(foot_candled / (0.3 * K))
        return cls(Fraction(stop).limit_denominator(3))

    @classmethod
    def from_lux(cls, lux):
        """
        >>> Iv.from_lux(269)
        Iv 268.8 lux
        """
        stop = math.log2(lux / (0.3 * 224))
        return cls(Fraction(stop).limit_denominator(3))

    @classmethod
    def from_stop(cls, stop: Union[int, float, Fraction]):
        """
        >>> Iv.from_stop(Fraction(1, 1))
        Iv 134.4 lux
        >>> Iv.from_stop(Fraction(2, 1))
        Iv 268.8 lux
        """
        return cls(stop=stop)

    def __repr__(self) -> str:
        return f"Iv {self.lux} lux"


class Exposure:
    """
    Exposure is a combination of the sensity of the sensor (Sv), the shutterspeed and the
    aperture of the lens (fstop).

    http://www.fredparker.com/ultexp1.htm#evfclux

    >>> Exposure(Av.from_fstop(decimal.Decimal("1.4")), Tv.from_time(Fraction(4, 1)), Sv.from_iso(100))
    EV -1.0 (Av f/1.4, Tv 4 sec, Sv 100 ISO)
    >>> Exposure(Av.from_fstop(decimal.Decimal("22")), Tv.from_time(Fraction(4, 1)), Sv.from_iso(100))
    EV 7.0 (Av f/22, Tv 4 sec, Sv 100 ISO)
    >>> Exposure(Av.from_fstop(decimal.Decimal("22")), Tv.from_time(Fraction(1, 15)), Sv.from_iso(100))
    EV 13.0 (Av f/22, Tv 1/15 sec, Sv 100 ISO)
    >>> Exposure(Av.from_fstop(decimal.Decimal("22")), Tv.from_time(Fraction(1, 15)), Sv.from_iso(800))
    EV 10.0 (Av f/22, Tv 1/15 sec, Sv 800 ISO)
    """

    def __init__(self, fstop: Av, shutter: Tv, iso: Sv) -> None:
        self.fstop = fstop
        self.shutter = shutter
        self.iso = iso

        self.ev100 = math.log(fstop.precise ** 2 / shutter.precise, 2)
        self.ev = self.ev100 - math.log(iso.precise / 100, 2)

    def __repr__(self) -> str:
        return f"EV {self.ev:.5} ({self.fstop}, {self.shutter}, {self.iso})"


# https://www.scantips.com/lights/fstop2.html

"""
Exposure classes to compute with exposure settings and metrics
"""
import decimal
import math
from decimal import Decimal
from fractions import Fraction
from typing import Type, Union

from exposure.utils import floor


class Exposure:
    """
    Base class for all Exposures
    """

    stop: Fraction

    def __init__(self, stop: Fraction):
        self.stop = stop.limit_denominator(3)

    def __add__(self, other: "Exposure"):
        if not isinstance(other, Exposure):
            raise TypeError("Exposure expected")
        return Exposure(self.stop + other.stop)

    def __sub__(self, other: "Exposure"):
        if not isinstance(other, Exposure):
            raise TypeError("Exposure expected")
        return Exposure(self.stop - other.stop)

    def __eq__(self, other: object):
        if not isinstance(other, Exposure):
            raise TypeError("Exposure expected")
        return self.stop == other.stop

    @classmethod
    def from_stop(cls, stop: Union[float, Fraction]):
        """
        Exposure Factory from `stop` parameter.

        >>> Iv.from_stop(Fraction(1, 1))
        Iv 134.4 lux
        >>> Tv.from_stop(1)
        Tv 2 sec
        """
        if not isinstance(stop, Fraction):
            stop = Fraction(stop)

        return cls(stop=stop)

    @classmethod
    def from_exposures(cls, *exposures: "Exposure"):
        """
        Calculate a setting

        >>> av = Av.from_stop(2)
        >>> sv = Sv.from_stop(2)
        >>> bv = Bv.from_stop(1)

        >>> Tv.from_exposures(sv, bv, av)
        Tv 2 sec

        """
        exp_classes = {i.__class__ for i in exposures}
        if len(exp_classes) != 3 and not exp_classes.intersection({Bv, Iv}):
            raise TypeError("3 different items from Tv, Sv, Av and Iv/Bv needed")

        if cls in exp_classes:
            raise TypeError(f"Can not compute {cls} as it is also given as parameter")

        ex = Exposure.from_stop(0)
        for exposure in exposures:
            ex = ex + exposure if exposure.__class__ in {Sv, Bv, Iv} else ex - exposure
        return cls.from_stop(ex.stop if cls in {Av, Tv} else -ex.stop)


class Av(Exposure):
    """
    Aperture value (Av) represents the aperture in its “relative aperture”
    (f/number), form (e.g., f/3.5). A larger Av represents a smaller
    aperture (larger f/number) and thus less exposure.
    """

    def __init__(self, stop: Fraction):
        super().__init__(stop)
        self.precise = self._stop_to_fstop_precise(self.stop)
        self.fstop = self._stop_to_fstop(self.stop)

    @classmethod
    def from_fstop(cls, fstop: Union[float, decimal.Decimal]):
        """
        Av Factory with a `fstop` as parameter.

        >>> Av.from_fstop(Decimal("1.4"))
        Av f/1.4
        >>> Av.from_fstop(Decimal("1.4")).stop
        Fraction(1, 1)
        >>> Av.from_fstop(Decimal("22")).stop
        Fraction(9, 1)
        """
        return cls(stop=cls._fstop_to_stop(fstop))

    @classmethod
    def from_focal_length_and_diameter(cls, focal_length_in_mm: float, diameter_in_mm: float):
        """
        Av Factory with a `focal_length_in_mm` and `diameter_in_mm` as parameter.

        >>> Av.from_focal_length_and_diameter(10, 5)
        Av f/2.0

        """
        return cls.from_fstop(focal_length_in_mm / diameter_in_mm)

    @staticmethod
    def _fstop_to_stop(fstop: Union[float, decimal.Decimal]) -> Fraction:
        """
        >>> Av._fstop_to_stop(1.4)
        Fraction(1, 1)
        >>> Av._fstop_to_stop(22)
        Fraction(9, 1)
        >>> Av._fstop_to_stop(1.7)
        Fraction(3, 2)
        >>> Av._fstop_to_stop(1.6)
        Fraction(4, 3)
        >>> Av._fstop_to_stop(1.8)
        Fraction(5, 3)
        >>> Av._fstop_to_stop(Decimal("1.8"))
        Fraction(5, 3)
        """
        stop = 2 * math.log(fstop, 10) / math.log(2, 10)
        return Fraction(stop).limit_denominator(3)

    @classmethod
    def _stop_to_fstop(cls, stop: Fraction) -> decimal.Decimal:
        """
        >>> Av._stop_to_fstop(1)
        Decimal('1.4')
        >>> Av._stop_to_fstop(Fraction(5, 3))
        Decimal('1.7')
        >>> Av._stop_to_fstop(9)
        Decimal('22')
        """
        fstop_precise = cls._stop_to_fstop_precise(stop)
        return Decimal(str(floor(fstop_precise, 2)))

    @staticmethod
    def _stop_to_fstop_precise(stop: Fraction) -> float:
        """
        >>> Av._stop_to_fstop_precise(1)
        1.4142135623730951
        """
        return math.sqrt(2) ** float(stop)

    def __repr__(self):
        return f"Av f/{self.fstop}"


class Sv(Exposure):
    """
    Speed value (Sv) reflects the sensitivity of the film or equivalent,
    expressed as an “ISO speed”. A larger Sv represents a greater
    sensitivity (speed).

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
        super().__init__(stop)
        self.iso = 100 * 2 ** stop

    @classmethod
    def from_iso(cls, iso: float):
        """
        Sv Factory with `iso` as parameter.

        >>> Sv.from_iso(100)
        Sv 100 ISO
        >>> Sv.from_iso(400)
        Sv 400 ISO
        >>> Sv.from_iso(400).stop
        Fraction(2, 1)
        """
        return cls(stop=Fraction(math.log(iso / 100, 2)))

    def __repr__(self) -> str:
        return f"Sv {self.iso} ISO"


class Tv(Exposure):
    """
    Time value (Tv) represents the exposure time (shutter speed) in
    seconds. A larger Tv represents a “faster” shutter speed and thus less
    exposure.
    """

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
        super().__init__(stop)
        self.precise = 2 ** self.stop
        self.time = self.stop2time[self.stop]

    @classmethod
    def from_time(cls, duration_in_sec: Fraction):
        """
        Tv Factory with `duration_in_sec` as parameter.

        >>> Tv.from_time(Fraction(10, 13))
        Tv 10/13 sec
        >>> Tv.from_time(Fraction(10, 13)).stop
        Fraction(-1, 3)
        """

        return cls(cls.time2stop[duration_in_sec])

    def __repr__(self) -> str:
        return f"Tv {self.time} sec"


class Bv(Exposure):
    """
    Brightness value (Bv) indicates the metered luminance (brightness) of
    the scene. A larger Bv represents greater scene luminance.

    >>> Bv.from_foot_lamberts(1).stop
    Fraction(0, 1)
    >>> Bv.from_foot_lamberts(1)
    Bv 3.4 cd/m2
    >>> Bv.from_stop(3)
    Bv 27.4 cd/m2
    >>> Bv.from_candelas(109)
    Bv 109.2 cd/m2
    >>> Bv.from_candelas(109).stop
    Fraction(5, 1)
    """

    def __init__(self, stop: Fraction):
        super().__init__(stop)
        self.candelas = self._candelas_from_stop(stop)
        self.foot_lamberts = self._foot_lamberts_from_stop(stop)

    @classmethod
    def _candelas_from_stop(cls, stop: Union[float, Fraction]):
        """
        >>> Bv._candelas_from_stop(0)
        3.4
        >>> Bv._candelas_from_stop(1)
        6.9
        """
        return round(2 ** stop * 3.4262591, 1)

    @classmethod
    def _foot_lamberts_from_stop(cls, stop: Fraction):
        """
        >>> Bv._foot_lamberts_from_stop(0)
        1
        >>> Bv._foot_lamberts_from_stop(1)
        2
        """
        return 2 ** stop

    @classmethod
    def from_candelas(cls, candelas: float):
        """
        Bv Factory with `candelas` as parameter.

        >>> Bv.from_candelas(3.4)
        Bv 3.4 cd/m2
        """
        stop = math.log2(candelas / (0.3 * 11.4))
        return cls(Fraction(stop))

    @classmethod
    def from_foot_lamberts(cls, foot_lamberts: float):
        """
        Bv Factory with `foot_lamberts` as parameter.

        >>> Bv.from_foot_lamberts(1)
        Bv 3.4 cd/m2
        """
        stop = math.log2(foot_lamberts)
        return cls(Fraction(stop))

    def __repr__(self) -> str:
        return f"Bv {self.candelas} cd/m2"


class Iv(Exposure):
    """
    Incident light value (Iv) indicates the (metered) illuminance
    (illumination) on the scene. A larger incident light value represents a
    greater illuminance.

    >>> Iv.from_foot_candles(25).stop
    Fraction(2, 1)
    >>> Iv.from_foot_candles(25)
    Iv 269.2 lux
    >>> Iv.from_stop(3)
    Iv 537.6 lux
    >>> Iv.from_lux(1076)
    Iv 1076.0 lux
    >>> Iv.from_lux(1076).stop
    Fraction(4, 1)
    """

    def __init__(self, stop: Fraction):
        super().__init__(stop)
        self.foot_candles = self._foot_candles_from_stop(stop)
        self.lux = self._lux_from_stop(stop)

    @classmethod
    def _foot_candles_from_stop(cls, stop: Fraction):
        """
        >>> Iv._foot_candles_from_stop(0)
        6.2
        >>> Iv._foot_candles_from_stop(1)
        12.5
        """
        return round(2 ** stop * 0.3 * 20.8, 1)

    @classmethod
    def _lux_from_stop(cls, stop: Fraction):
        """
        >>> Iv._lux_from_stop(0)
        67.2
        >>> Iv._lux_from_stop(1)
        134.4
        """
        return round(2 ** stop * 0.3 * 224, 1)

    @classmethod
    def from_foot_candles(cls, foot_candles: float):
        """
        Iv Factory from `foot_candles` parameter.

        >>> Iv.from_foot_candles(25)
        Iv 269.2 lux
        """
        stop = math.log2(foot_candles / (0.3 * 20.8))
        return cls(Fraction(stop))

    @classmethod
    def from_lux(cls, lux: float):
        """
        Iv Factory from `lux` parameter.

        >>> Iv.from_lux(269)
        Iv 269.0 lux
        """
        stop = math.log2(lux / (0.3 * 224))
        return cls(Fraction(stop))

    def __repr__(self) -> str:
        return f"Iv {self.lux} lux"

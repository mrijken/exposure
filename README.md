# Exposure

![Build](https://github.com/mrijken/exposure/workflows/CI/badge.svg)
![Hits](https://hitcounter.pythonanywhere.com/count/tag.svg?url=https%3A%2F%2Fgithub.com%2Fmrijken%2Fexposure)

With Exposure you can compute the exposure for a photo camera based
on settings of the camera and metrics of the environment.

## Installation

`pip install exposure`

## Usage

    >>> from exposure import Av, Tv, Sv, Bv, Iv, Exposure
    >>> from decimal import Decimal
    >>> from fractions import Fraction

### Aperture

    >>> Av.from_stop(1)
    Av f/1.4

    >>> Av.from_focal_length_and_diameter(10, 5)
    Av f/2.0

    >>> Av.from_fstop(Decimal("1.4"))
    Av f/1.4

    >>> Av.from_fstop(Decimal("22")).stop
    Fraction(9, 1)

    >>> Av.from_fstop(Decimal("22")).fstop
    Decimal('22')

### Speed

    >>> Sv.from_iso(100)
    Sv 100 ISO

    >>> Sv.from_stop(Fraction(1, 1))
    Sv 200 ISO

    >>> Sv.from_iso(100).stop
    Fraction(0, 1)

    >>> Sv.from_iso(100).iso
    100

### Shutter

    >>> Tv.from_stop(1)
    Tv 2 sec

    >>> Tv.from_time(Fraction(10, 13))
    Tv 10/13 sec

    >>> Tv.from_time(Fraction(2, 1)).stop
    Fraction(1, 1)

    >>> Tv.from_time(Fraction(2, 1)).time
    Fraction(2, 1)

### Brightness

    >>> Bv.from_foot_lamberts(1)
    Bv 3.4 cd/m2

    >>> Bv.from_candelas(109)
    Bv 109.2 cd/m2

    >>> Bv.from_stop(3)
    Bv 27.4 cd/m2

    >>> Bv.from_stop(3).stop
    Fraction(3, 1)

    >>> Bv.from_stop(3).candelas
    27.4

    >>> Bv.from_stop(3).foot_lamberts
    8

### Incident Light

    >>> Iv.from_foot_candles(25)
    Iv 269.2 lux

    >>> Iv.from_lux(1076)
    Iv 1076.0 lux

    >>> Iv.from_stop(3)
    Iv 537.6 lux

    >>> Iv.from_lux(1076).stop
    Fraction(4, 1)

    >>> Iv.from_lux(1076).lux
    1076.0

    >>> Iv.from_lux(1076).foot_candles
    99.9


### Exposure

    >>> tv = Tv.from_stop(1)
    >>> av = Av.from_stop(2)
    >>> sv = Sv.from_stop(2)
    >>> bv = Bv.from_stop(1)
    >>> iv = Iv.from_stop(1)

    The exposure is in balance when

    >>> tv + av == sv + bv
    True

    or

    >>> tv + av == sv + iv
    True

    This can also be used to compute a needed setting, like

    >>> Tv.from_exposures(sv, bv, av)
    Tv 2 sec
    >>> Tv.from_exposures(sv, bv, av) == tv
    True

    >>> Av.from_exposures(sv, bv, tv)
    Av f/2.0

    >>> Sv.from_exposures(tv, bv, av)
    Sv 400 ISO

    >>> Sv.from_exposures(tv, iv, av)
    Sv 400 ISO

Future work:

* from_exif

## Disclaimer

This package is based on http://dougkerr.net/Pumpkin/articles/APEX.pdf

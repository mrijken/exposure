// Aperture value (Av) represents the aperture in its “relative aperture”
// (f/number), form (e.g., f/3.5). A larger Av represents a smaller
// aperture (larger f/number) and thus less exposure.

use rust_decimal::prelude::*;

mod fraction;

pub struct Av {
    precise: f64,
    fstop: String,
}

impl Av {
    /// # Examples
    ///
    /// ```
    /// use exposure::Av;
    /// use rust_decimal::prelude::*;
    ///
    /// let s = Av::fstop_to_stop(Decimal::from_str("1.4").unwrap());
    /// assert_eq!(format!("{}",s), "1/1");
    ///
    /// let s = Av::fstop_to_stop(Decimal::from_str("22.0").unwrap());
    /// assert_eq!(format!("{}",s), "9/1");
    ///
    /// let s = Av::fstop_to_stop(Decimal::from_str("1.7").unwrap());
    /// assert_eq!(format!("{}",s), "3/2");
    ///
    /// let s = Av::fstop_to_stop(Decimal::from_str("1.6").unwrap());
    /// assert_eq!(format!("{}",s), "4/3");
    ///
    /// let s = Av::fstop_to_stop(Decimal::from_str("1.8").unwrap());
    /// assert_eq!(format!("{}",s), "5/3");
    ///
    /// ```
    pub fn fstop_to_stop(fstop: Decimal) -> fraction::Fraction {
        let fstop = fstop.to_f64().unwrap();
        let stop = 2.0 * fstop.log10() / (2.0_f64).log10();
        fraction::Fraction::from_f64(stop, 0.1)
    }

    pub fn stop_to_fstop(&self, stop: fraction::Fraction) -> Decimal {
        let stop = stop.to_f64();
        Decimal::from_f64(2.0_f64.sqrt() * stop).unwrap()
    }

    // @classmethod
    // def _stop_to_fstop(cls, stop: Fraction) -> decimal.Decimal:
    //     """
    //     >>> Av._stop_to_fstop(1)
    //     Decimal('1.4')
    //     >>> Av._stop_to_fstop(Fraction(5, 3))
    //     Decimal('1.7')
    //     >>> Av._stop_to_fstop(9)
    //     Decimal('22')
    //     """
    //     fstop_precise = cls._stop_to_fstop_precise(stop)
    //     return Decimal(str(floor(fstop_precise, 2)))
}

pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}

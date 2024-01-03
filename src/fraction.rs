use std::cmp::Ordering;
use std::f64::consts::PI;
use std::ops::{Add, Div, Mul, Sub};
use std::{cmp, fmt};

#[derive(Debug)]
pub struct Fraction {
    numerator: i64,
    denominator: i64,
}

impl Fraction {
    /// Creates a new fraction with the given numerator and denominator
    /// Panics if given a denominator of 0
    pub fn new(numerator: i64, denominator: i64) -> Self {
        if denominator == 0 {
            panic!("Tried to create a fraction with a denominator of 0!")
        }
        if denominator < 0 {
            Self {
                numerator: -numerator,
                denominator: -denominator,
            }
        } else {
            Self {
                numerator,
                denominator,
            }
        }
    }

    pub fn from_str(s: &str) -> Self {
        let mut parts = s.split('/');
        let numerator = parts.next().unwrap().parse::<i64>().unwrap();
        let denominator = parts.next().unwrap().parse::<i64>().unwrap();
        Self::new(numerator, denominator)
    }

    pub fn from_f64(mut x: f64, error: f64) -> Self {
        let n = x.floor() as i64;
        let mut x = x - (n as f64);
        if x < error {
            return Fraction::new(n, 1);
        } else if 1.0 - error < x {
            return Fraction::new(n + 1, 1);
        }

        let mut lower_n = 0;
        let mut lower_d = 1;
        let mut upper_n = 1;
        let mut upper_d = 1;

        loop {
            let middle_n = lower_n + upper_n;
            let middle_d = lower_d + upper_d;

            match (middle_d as f64 * (x + error)).partial_cmp(&(middle_n as f64)) {
                Some(Ordering::Less) => {
                    upper_n = middle_n;
                    upper_d = middle_d;
                }
                Some(Ordering::Greater) => {
                    if (middle_n as f64) < (x - error) * (middle_d as f64) {
                        lower_n = middle_n;
                        lower_d = middle_d;
                    } else {
                        return Fraction::new(n * middle_d + middle_n, middle_d);
                    }
                }
                _ => {
                    return Fraction::new(n * middle_d + middle_n, middle_d);
                }
            }
        }
    }
    /// Returns a new Fraction that is equal to this one, but simplified
    pub fn reduce(&self) -> Self {
        // Use absolute value because negatives
        let gcd = gcd(self.numerator.abs(), self.denominator.abs());
        Self {
            numerator: (self.numerator / gcd),
            denominator: (self.denominator / gcd),
        }
    }

    pub fn to_f64(&self) -> f64 {
        self.numerator as f64 / self.denominator as f64
    }
}

impl fmt::Display for Fraction {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let temp = self.reduce();
        write!(f, "{}/{}", temp.numerator, temp.denominator)
    }
}

impl cmp::PartialEq for Fraction {
    fn eq(&self, other: &Fraction) -> bool {
        let simp_self = self.reduce();
        let simp_other = other.reduce();
        simp_self.numerator == simp_other.numerator
            && simp_self.denominator == simp_other.denominator
    }
}

impl cmp::Eq for Fraction {}

impl cmp::PartialOrd for Fraction {
    fn partial_cmp(&self, other: &Fraction) -> Option<cmp::Ordering> {
        self.to_f64().partial_cmp(&other.to_f64())
    }
}

impl<'a> Add for &'a Fraction {
    type Output = Fraction;

    fn add(self, other: Self) -> Fraction {
        Fraction {
            numerator: (self.numerator * other.denominator + other.numerator * self.denominator),
            denominator: (self.denominator * other.denominator),
        }
    }
}

impl<'a> Sub for &'a Fraction {
    type Output = Fraction;

    fn sub(self, other: Self) -> Fraction {
        Fraction {
            numerator: (self.numerator * other.denominator - other.numerator * self.denominator),
            denominator: (self.denominator * other.denominator),
        }
    }
}

impl<'a> Mul for &'a Fraction {
    type Output = Fraction;

    fn mul(self, other: Self) -> Fraction {
        Fraction {
            numerator: (self.numerator * other.numerator),
            denominator: (self.denominator * other.denominator),
        }
    }
}

impl<'a> Div for &'a Fraction {
    type Output = Fraction;

    fn div(self, other: Self) -> Fraction {
        Fraction {
            numerator: (self.numerator * other.denominator),
            denominator: (self.denominator * other.numerator),
        }
    }
}

// Calculate the greatest common denominator for two numbers
pub fn gcd(a: i64, b: i64) -> i64 {
    // Terminal cases
    if a == b {
        return a;
    }
    if a == 0 {
        return b;
    }
    if b == 0 {
        return a;
    }

    let a_is_even = a % 2 == 0;
    let b_is_even = b % 2 == 0;

    match (a_is_even, b_is_even) {
        (true, true) => gcd(a / 2, b / 2) * 2,
        (true, false) => gcd(a / 2, b),
        (false, true) => gcd(a, b / 2),
        (false, false) => {
            if a > b {
                gcd((a - b) / 2, b)
            } else {
                gcd((b - a) / 2, a)
            }
        }
    }
}

#[test]
fn ordering_test() {
    let a = Fraction::new(1, 2);
    let b = Fraction::new(3, 4);
    let c = Fraction::new(4, 3);
    let d = Fraction::new(-1, 2);
    assert!(a < b);
    assert!(a <= b);
    assert!(c > b);
    assert!(c >= a);
    assert!(d < a);
}

#[test]
fn equality_test() {
    let a = Fraction::new(1, 2);
    let b = Fraction::new(2, 4);
    let c = Fraction::new(5, 5);
    assert!(a == b);
    assert!(a != c);
}

#[test]
fn arithmetic_test() {
    let a = Fraction::new(1, 2);
    let b = Fraction::new(3, 4);
    assert!(&a + &a == Fraction::new(1, 1));
    assert!(&a - &a == Fraction::new(0, 5));
    assert!(&a * &b == Fraction::new(3, 8));
    assert!(&a / &b == Fraction::new(4, 6));
}

#[test]
fn limit_denominator_test() {
    assert_eq!(Fraction::from_f64(3.1415926, 0.01), Fraction::new(22, 7));
    assert_eq!(Fraction::from_f64(PI, 0.00001), Fraction::new(355, 113));
}

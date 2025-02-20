import galois
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass


class KoetterVardyException(Exception):
    """Custom exception for Koetter-Vardy algorithm related errors."""

    def __init__(self, message: str, code: int = 0, original_exception: Exception = None):
        super().__init__(message)
        self.code = code
        self.original_exception = original_exception


@dataclass
class RSInterpolationPoint:
    """Represents a single interpolation point with multiplicity."""

    x: galois.GF
    y: galois.GF
    m: int  # Multiplicity


class RSInterpolationPointSet:
    """Represents a set of interpolation points."""

    def __init__(self, field: galois.GF, points: List[RSInterpolationPoint]):
        self.field = field
        self.points = points

    def size(self) -> int:
        """Returns the number of points in the set."""
        return len(self.points)

    def point_at(self, index: int) -> RSInterpolationPoint:
        """Returns the point at the given index."""
        return self.points[index]


class GFBiPolynomial:
    """Represents a bivariate polynomial over a Galois Field."""

    def __init__(self, coefficients: np.ndarray, field: galois.GF):
        """
        Initializes a GFBiPolynomial.

        Args:
            coefficients: A 2D numpy array representing the coefficients of the polynomial.
                          coefficients[i][j] is the coefficient of x^i * y^j.
            field: The Galois Field over which the polynomial is defined.
        """
        self.coefficients = coefficients
        self.field = field

    def __str__(self) -> str:
        """Returns a string representation of the polynomial."""
        terms = []
        for i in range(self.coefficients.shape[0]):
            for j in range(self.coefficients.shape[1]):
                coeff = self.coefficients[i, j]
                if coeff != 0:
                    term = ""
                    if i == 0 and j == 0:
                        term = str(coeff)
                    else:
                        if coeff != 1:
                            term += str(coeff) + "*"
                        if i > 0:
                            term += f"x^{i}"
                        if j > 0:
                            if i > 0:
                                term += "*"
                            term += f"y^{j}"
                    terms.append(term)

        if not terms:
            return "0"
        return " + ".join(terms)

    def coefficient(self, alpha_i: galois.GF, beta_i: galois.GF, r: int, s: int) -> galois.GF:
        """
        Evaluates the (r, s)-th derivative of the polynomial at (alpha_i, beta_i).

        Args:
            alpha_i: The x-coordinate of the evaluation point.
            beta_i: The y-coordinate of the evaluation point.
            r: The derivative order with respect to x.
            s: The derivative order with respect to y.

        Returns:
            The value of the (r, s)-th derivative at (alpha_i, beta_i).
        """
        # Implement the derivative and evaluation logic here.
        # This is a placeholder; you'll need to implement the actual calculation.
        # This is the most complex part and requires careful implementation of polynomial derivatives.
        # The galois library does not have built-in derivative functionality, so you'll need to implement it manually.
        # This will involve iterating through the coefficients, applying the power rule for derivatives,
        # and then evaluating the resulting polynomial at (alpha_i, beta_i).
        # The following is a very basic placeholder that always returns 0.
        return self.field(0)

    def mMul(self, element: galois.GF, x_degree: int, y_degree: int) -> "GFBiPolynomial":
        """
        Multiplies the polynomial by a monomial element * x^x_degree * y^y_degree.

        Args:
            element: The element to multiply by.
            x_degree: The degree of x in the monomial.
            y_degree: The degree of y in the monomial.

        Returns:
            A new GFBiPolynomial representing the result of the multiplication.
        """
        new_coeffs = np.zeros(
            (self.coefficients.shape[0] + x_degree, self.coefficients.shape[1] + y_degree),
            dtype=self.field.dtype,
        )
        new_coeffs[x_degree:, y_degree:] = self.coefficients * element
        return GFBiPolynomial(new_coeffs, self.field)

    def mSub(self, element: galois.GF, x_degree: int, y_degree: int) -> "GFBiPolynomial":
        """
        Subtracts a monomial element * x^x_degree * y^y_degree from the polynomial.

        Args:
            element: The element to subtract.
            x_degree: The degree of x in the monomial.
            y_degree: The degree of y in the monomial.

        Returns:
            A new GFBiPolynomial representing the result of the subtraction.
        """
        sub_poly = GFBiPolynomial(np.array([[element]]), self.field).mMul(element, x_degree, y_degree)
        return self.sub(sub_poly)

    def mul(self, other: "GFBiPolynomial") -> "GFBiPolynomial":
        """
        Multiplies this polynomial by another polynomial.

        Args:
            other: The other polynomial to multiply by.

        Returns:
            A new GFBiPolynomial representing the result of the multiplication.
        """
        new_coeffs = np.zeros(
            (
                self.coefficients.shape[0] + other.coefficients.shape[0] - 1,
                self.coefficients.shape[1] + other.coefficients.shape[1] - 1,
            ),
            dtype=self.field.dtype,
        )

        for i in range(self.coefficients.shape[0]):
            for j in range(self.coefficients.shape[1]):
                for k in range(other.coefficients.shape[0]):
                    for l in range(other.coefficients.shape[1]):
                        new_coeffs[i + k, j + l] += self.coefficients[i, j] * other.coefficients[k, l]

        return GFBiPolynomial(new_coeffs, self.field)

    def sub(self, other: "GFBiPolynomial") -> "GFBiPolynomial":
        """
        Subtracts another polynomial from this polynomial.

        Args:
            other: The other polynomial to subtract.

        Returns:
            A new GFBiPolynomial representing the result of the subtraction.
        """
        max_x_degree = max(self.coefficients.shape[0], other.coefficients.shape[0])
        max_y_degree = max(self.coefficients.shape[1], other.coefficients.shape[1])

        new_coeffs = np.zeros((max_x_degree, max_y_degree), dtype=self.field.dtype)

        for i in range(self.coefficients.shape[0]):
            for j in range(self.coefficients.shape[1]):
                new_coeffs[i, j] = self.coefficients[i, j]

        for i in range(other.coefficients.shape[0]):
            for j in range(other.coefficients.shape[1]):
                new_coeffs[i, j] -= other.coefficients[i, j]

        return GFBiPolynomial(new_coeffs, self.field)

    def yDegree(self) -> int:
        """
        Returns the degree of the polynomial in the y variable.

        Returns:
            The degree of the polynomial in y.
        """
        degree = 0
        for j in range(self.coefficients.shape[1] - 1, -1, -1):
            if np.any(self.coefficients[:, j] != 0):
                degree = j
                break
        return degree


def argmin_l(Wdeg: List[int], d_rs: List[galois.GF]) -> int:
    """
    Finds the index l with the minimum Wdeg[l] such that d_rs[l] != 0.

    Args:
        Wdeg: A list of integer weights.
        d_rs: A list of Galois Field elements.

    Returns:
        The index l with the minimum Wdeg[l] such that d_rs[l] != 0.
        Returns -1 if no such l exists.
    """
    min_l = -1
    min_wdeg = float("inf")  # Initialize with positive infinity

    for l in range(len(Wdeg)):
        if d_rs[l] != 0 and Wdeg[l] < min_wdeg:
            min_wdeg = Wdeg[l]
            min_l = l

    return min_l


def interpolate(
    ip_set: RSInterpolationPointSet, dy: int, k: int, dy_min: int
) -> Optional[GFBiPolynomial]:
    """
    Performs the interpolation step of the Koetter-Vardy algorithm.

    Args:
        ip_set: The set of interpolation points.
        dy: The target degree in y.
        k: The message length.
        dy_min: The minimum degree in y.

    Returns:
        The interpolated polynomial, or None if interpolation fails.

    Raises:
        KoetterVardyException: If interpolation fails.
    """
    try:
        if dy_min > dy:
            raise KoetterVardyException("Interpolation fails: t_min must be < t.", 4)

        field = ip_set.field
        oneBiPoly = GFBiPolynomial(np.array([[field(1)]]), field)  # Represents the constant polynomial 1
        print("oneBiPoly:", oneBiPoly)

        xBiPoly = GFBiPolynomial(np.array([[field(0)], [field(1)]]), field)  # Represents the polynomial x
        print("xBiPoly:", xBiPoly)

        Q: List[GFBiPolynomial] = [None] * (dy + 1)  # type: ignore # List of polynomials Q_l
        Wdeg: List[int] = [0] * (dy + 1)  # Weights associated with each Q_l
        d_rs: List[galois.GF] = [field(0)] * (dy + 1)  # Values d_rs[l]

        l_min: int = 0

        # Initialize Q[l] = y^l and Wdeg[l] = l * (k - 1)
        for l in range(dy + 1):
            Q[l] = oneBiPoly.mMul(field(1), 0, l)  # Q[l] = y^l
            print("Q:", Q[l])
            Wdeg[l] = l * (k - 1)

        n = ip_set.size()

        # Interpolation loop
        for i in range(n):
            alpha_i = ip_set.point_at(i).x
            beta_i = ip_set.point_at(i).y
            multiplicity = ip_set.point_at(i).m

            for r in range(multiplicity):
                for s in range(multiplicity - r):
                    # Evaluate derivatives
                    for l in range(dy + 1):
                        d_rs[l] = Q[l].coefficient(alpha_i, beta_i, r, s)

                    # Find l_min
                    l_min = argmin_l(Wdeg, d_rs)

                    if l_min == -1:
                        continue

                    # Update polynomials
                    for l in range(dy + 1):
                        if l == l_min:
                            continue
                        Q[l] = Q[l].mMul(d_rs[l_min], 0, 0).sub(Q[l_min].mMul(d_rs[l], 0, 0))

                    Q[l_min] = Q[l_min].mul(xBiPoly.mSub(alpha_i, 0, 0))
                    Wdeg[l_min] += 1

        # Find l_min with Wdeg[l] >= Wdeg_min and Q[l].yDegree() >= dy_min
        l_min = dy_min
        Wdeg_min = Wdeg[l_min]

        for l in range(dy + 1):
            if Wdeg[l] >= Wdeg_min or Q[l].yDegree() < dy_min:
                continue
            Wdeg_min = Wdeg[l]
            l_min = l

        # Return the polynomial if its y-degree is at least dy_min, otherwise return None
        return Q[l_min] if Q[l_min].yDegree() >= dy_min else None

    except Exception as e:
        raise KoetterVardyException("Interpolation fails.", 4, e)



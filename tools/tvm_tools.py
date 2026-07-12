import math

def _validate_rate(i: float) -> float:
    """
    Validate that an interest rate is mathematically usable.

    Parameters:
        i (float): Effective interest rate per period as a decimal.

    Returns:
        float: Validated interest rate.
    """
    if i <= -1:
        raise ValueError("Interest rate must be greater than -100%.")
    return i

def present_value(fv: float, i: float, n: float) -> float:
    """
    Calculate the present value of a future lump sum.

    Parameters:
        fv (float): Future value.
        i (float): Effective interest rate per period as a decimal.
        n (float): Number of periods.

    Returns:
        float: Present value.
    """
    _validate_rate(i)
    return fv / ((1 + i) ** n)

def future_value(pv: float, i: float, n: float) -> float:
    """
    Calculate the future value of a present lump sum.

    Parameters:
        pv (float): Present value.
        i (float): Effective interest rate per period as a decimal.
        n (float): Number of periods.

    Returns:
        float: Future value.
    """
    _validate_rate(i)
    return pv * ((1 + i) ** n)

def solve_rate(pv: float, fv: float, n: float) -> float:
    """
    Solve for the effective interest rate per period.

    Parameters:
        pv (float): Present value.
        fv (float): Future value.
        n (float): Number of periods.

    Returns:
        float: Effective interest rate per period as a decimal.
    """
    if pv == 0:
        raise ValueError("PV cannot be zero.")
    if n == 0:
        raise ValueError("n cannot be zero.")
    if fv / pv <= 0:
        raise ValueError("FV/PV must be positive to solve rate.")
    return (fv / pv) ** (1 / n) - 1

def solve_n(pv: float, fv: float, i: float) -> float:
    """
    Solve for the number of periods.

    Parameters:
        pv (float): Present value.
        fv (float): Future value.
        i (float): Effective interest rate per period as a decimal.

    Returns:
        float: Number of periods.
    """
    _validate_rate(i)
    if pv == 0:
        raise ValueError("PV cannot be zero.")
    if i == 0:
        raise ValueError("i cannot be zero when solving for n.")
    if fv / pv <= 0:
        raise ValueError("FV/PV must be positive to solve n.")
    return math.log(fv / pv) / math.log(1 + i)

def nominal_to_effective(j: float, m: int) -> float:
    """
    Convert a nominal annual interest rate to an effective annual interest rate.

    Parameters:
        j (float): Nominal annual rate as a decimal.
        m (int): Number of compounding periods per year.

    Returns:
        float: Effective annual interest rate as a decimal.
    """
    if m <= 0:
        raise ValueError("m must be positive.")
    return (1 + j / m) ** m - 1

def effective_to_nominal(i: float, m: int) -> float:
    """
    Convert an effective annual interest rate to a nominal annual interest rate.

    Parameters:
        i (float): Effective annual interest rate as a decimal.
        m (int): Number of compounding periods per year.

    Returns:
        float: Nominal annual interest rate as a decimal.
    """
    _validate_rate(i)
    if m <= 0:
        raise ValueError("m must be positive.")
    return m * ((1 + i) ** (1 / m) - 1)

def force_to_effective(delta: float) -> float:
    """
    Convert force of interest to effective interest rate.

    Parameters:
        delta (float): Force of interest.

    Returns:
        float: Effective interest rate as a decimal.
    """
    return math.exp(delta) - 1

def effective_to_force(i: float) -> float:
    """
    Convert an effective interest rate to force of interest.

    Parameters:
        i (float): Effective interest rate as a decimal.

    Returns:
        float: Force of interest.
    """
    _validate_rate(i)
    return math.log(1 + i)

def equation_of_value(cashflows: list, i: float, focal_date: float) -> float:
    """
    Calculate the equivalent value of multiple cashflows at a focal date.

    Sign convention:
        Cash inflows are positive.
        Cash outflows are negative.

    Parameters:
        cashflows (list): List of dictionaries with amount and time keys.
        i (float): Effective interest rate per period as a decimal.
        focal_date (float): Date at which all cashflows are valued.

    Returns:
        float: Equivalent value at the focal date.
    """
    _validate_rate(i)
    total = 0
    for cf in cashflows:
        amount = cf["amount"]
        time = cf["time"]
        total += amount * ((1 + i) ** (focal_date - time))
    return total

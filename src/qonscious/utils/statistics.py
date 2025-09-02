import math
import statistics
from collections.abc import Sequence

__all__ = ["describe", "percentile_linear"]


def percentile_linear(vals: Sequence[float], p: float) -> float:
    if not vals:
        return math.nan
    xs = sorted(vals)
    k = (len(xs) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] * (c - k) + xs[c] * (k - f)


def describe(
    values: Sequence[float],
    nonfinite: str = "ignore",  # "ignore", "cap", "error"
    cap_value: float | None = None,
) -> dict[str, float | str]:
    """
    Compute simple descriptive statistics for a list of numbers.

    Parameters
    ----------
    values : Sequence[float]
        Input values to analyze.
    nonfinite : {"ignore", "cap", "error"}, default="ignore"
        Policy for handling non-finite values (NaN, ±inf):
          - "ignore": drop them before computing statistics.
          - "cap": replace them with `cap_value` (must be provided).
          - "error": raise an exception if any non-finite is found.
    cap_value : float, optional
        Replacement value when `nonfinite="cap"`.

    Returns
    -------
    dict[str, float | str]
        A dictionary containing:
          - "mean", "median", "std", "min", "max", "q25", "q75", "cv"
            (coefficient of variation = std / mean),
          - "comments": notes about how non-finite values were handled
            or why results are NaN (e.g., empty input).
    """
    comments = None
    xs = list(values)

    if nonfinite == "ignore":
        finite = [v for v in xs if math.isfinite(v)]
        if len(finite) != len(xs):
            comments = "Non-finite values ignored"
        xs = finite

    elif nonfinite == "cap":
        if any(not math.isfinite(v) for v in xs):
            if cap_value is None:
                raise ValueError("cap_value must be provided when nonfinite='cap'")
            xs = [v if math.isfinite(v) else cap_value for v in xs]
            comments = f"Non-finite values capped to {cap_value}"

    elif nonfinite == "error":
        if any(not math.isfinite(v) for v in xs):
            raise ValueError("Non-finite values present")

    else:
        raise ValueError(f"Unknown nonfinite policy: {nonfinite}")

    if not xs:
        return {
            k: math.nan for k in ("mean", "median", "std", "min", "max", "q25", "q75", "cv")
        } | {"comments": comments or "no finite values"}

    xs.sort()
    mean = statistics.fmean(xs)
    std = statistics.pstdev(xs) if len(xs) > 1 else 0.0
    cv = std / mean if mean != 0 else math.nan

    return {
        "mean": mean,
        "median": statistics.median(xs),
        "std": std,
        "min": xs[0],
        "max": xs[-1],
        "q25": percentile_linear(xs, 0.25),
        "q75": percentile_linear(xs, 0.75),
        "cv": cv,
        "comments": comments or "",
    }

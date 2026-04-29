from dataclasses import dataclass


@dataclass(frozen=True)
class FaultContext:
    source: str
    condition: str
    value: int
    previous_value: int | None = None


DEFAULT_RECOMMENDATION = (
    "Check the machine status screen, confirm the register mapping, and inspect nearby sensors or operator messages."
)


RECOMMENDATIONS: dict[tuple[str, str], str] = {
    ("package_count", "below_min"): (
        "Verify the package counter register, check whether the counter was reset, and confirm product is feeding normally."
    ),
    ("package_count", "reset"): (
        "Confirm this was caused by a lot change, operator reset, or normal machine restart before treating it as a fault."
    ),
    ("format", "below_min"): (
        "Check the selected format on the HMI and verify the format register address is correct."
    ),
    ("format", "above_max"): (
        "Check for an invalid format selection, stale HMI value, or incorrect register scaling."
    ),
    ("set_format", "below_min"): (
        "Confirm the requested format value on the HMI and verify the operator did not enter an invalid setup."
    ),
    ("set_format", "above_max"): (
        "Review the requested format setting and compare it against the known valid format list."
    ),
}


def recommend_fix(context: FaultContext) -> str:
    """Return a first-pass fix recommendation for a detected fault."""

    recommendation = RECOMMENDATIONS.get((context.source, context.condition))
    if recommendation:
        return recommendation

    if context.condition == "below_min":
        return f"Inspect {context.source}; the value is lower than expected and may indicate a reset or bad register map."

    if context.condition == "above_max":
        return f"Inspect {context.source}; the value is higher than expected and may indicate a stuck sensor or scaling issue."

    if context.condition == "reset":
        return f"Confirm whether {context.source} was intentionally reset before escalating."

    return DEFAULT_RECOMMENDATION

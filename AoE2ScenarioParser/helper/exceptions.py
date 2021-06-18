class InvalidScenarioStructureError(Exception):
    pass


class UnknownScenarioStructureError(Exception):
    pass


class UnknownStructureError(Exception):
    pass


class EndOfFileError(Exception):
    pass


class TargetRetrieverReached(Exception):
    """Used like StopIteration in nested generator. But StopIteration stops both and raises the error on the outside"""
    pass


class UnsupportedAttributeError(Exception):
    pass


def type_error_message(value, include_hint=True):
    return f"Expected int, found: {value.__class__}. " + (f"Maybe you meant: '{value}.ID'?" if include_hint else "")


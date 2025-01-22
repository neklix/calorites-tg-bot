class ValidationError(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def validate_str(value):
    if not isinstance(value, str):
        raise ValidationError("given value is not str")
    return value

def validate_int(value):
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError as e:
            raise ValidationError("given value is not an int") from e
    if not isinstance(value, int):
        raise ValidationError("given value is not an int")
    return value

def validate_float(value):
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError as e:
            raise ValidationError("given value is not float") from e
    if not isinstance(value, (int, float)):
        raise ValidationError("given value is not float")
    return value

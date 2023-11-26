"""Helpers ib, to provide some useful, but not mandatory functionality
"""
import time

# SPDX-FileCopyrightText: 2022 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
# https://github.com/spdx/tools-python/blob/main/pyproject.toml
from dataclasses import dataclass

from bugal import cfg


def dataclass_with_properties(cls):
    """Decorator to generate a dataclass with properties out of the class' value:type list.
    Their getters and setters will be subjected to the @typechecked decorator to ensure type conformity."""
    data_cls = dataclass(cls)
    for field_name, field_type in data_cls.__annotations__.items():
        set_field = make_setter(field_name, field_type)
        get_field = make_getter(field_name, field_type)

        setattr(data_cls, field_name, property(get_field, set_field))

    return data_cls


def make_setter(field_name, field_type):
    """helper method to avoid late binding when generating functions in a for loop"""

    def set_field(self, value: field_type):
        setattr(self, f"_{field_name}", value)

    def set_field_with_error_conversion(self, value: field_type):
        try:
            set_field(self, value)
        except cfg.ModelStackError as err:
            error_message: str = f"SetterError {self.__class__.__name__}: {err}"

            # As setters are created dynamically, their argument name is always "value". We replace it by the
            # actual name so the error message is more helpful.
            raise TypeError(error_message.replace("value", field_name, 1) + f": {value}")

    return set_field_with_error_conversion


def make_getter(field_name, field_type):
    """helper method to avoid late binding when generating functions in a for loop"""

    def get_field(self) -> field_type:
        return getattr(self, f"_{field_name}")

    return get_field


class ExecutionTimer:
    """Execution time measurement, which can be used as decorator
    it can be used like this:
    @ExecutionTimer(repetitions=100)
    def my_function(par):
        function body
    """
    def __init__(self, repetitions=1):
        self.repetitions = repetitions

    def __call__(self, func):
        def timer(*args, **kwargs):
            result = None
            total_time = 0
            print(f"Running {func.__name__}() {self.repetitions} times")
            for _ in range(self.repetitions):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                total_time += end - start
            average_time = total_time / self.repetitions
            print(
                f"{func.__name__}() takes "
                f"{average_time * 1000:.4f} ms on average"
            )
            return result

        return timer


'''
Beispiel für multi exceptions. match wird nicht unterstützt python version?
try:
    first = float(input("What is your first number? "))
    second = float(input("What is your second number? "))
    operation = input("Enter either * or /: ")
    if operation == "*":
        answer = calculate(mul, first, second)
    elif operation == "/":
        answer = calculate(truediv, first, second)
    else:
        raise RuntimeError(f"'{operation}' is an unsupported operation")
except (RuntimeError, ValueError, ZeroDivisionError) as error:
    print(f"A {type(error).__name__} has occurred")
    match error:
        case RuntimeError():
            print(f"You have entered an invalid symbol: {error}")
        case ValueError():
            print(f"You have not entered a number: {error}")
        case ZeroDivisionError():
            print(f"You can't divide by zero: {error}")
else:
    print(f"{first} {operation} {second} = {answer}")
'''
# Choice Between Subclassing and Union

## Status

Accepted

## Context

The Job Management System is used across all model containers. Therefore, the lowest python version of 3.9 must be supported.

In python 3.9, with a union type `MyType = Union[MyClass1, MyClass2]`, `isinstance(x, MyType)` results in the error `TypeError: Subscripted generics cannot be used with class and instance checks`.

Alternatives are using `isinstance(x, get_args(MyType))` and declaring a function to assert the type, but it cannot be analyzed by Pylance type checking.

## Decision

While there is no preference to subclassing or union, subclassing should be used if `isinstance` calls for narrowing needs to be supported.

Example: Implementation of `StoppedJobs` in `job_info.py`

## Consequences

from typing import TypedDict


class MachineStartResult(TypedDict):
    success_count: int
    failed_count: int
    all_started: bool
    message: str
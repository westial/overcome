from dataclasses import dataclass


@dataclass
class Positions:
    read_for_win: callable
    remove_for_win: callable
    read_for_lose: callable
    remove_for_lose: callable

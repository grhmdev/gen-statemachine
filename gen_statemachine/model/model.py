from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Event:
    name: str = ""


@dataclass
class Action:
    text: str = ""


@dataclass
class Transition:
    start_state: State
    destination_state: State
    event: Optional[Event] = None
    actions: List[Action] = field(default_factory=list)


@dataclass
class State:
    name: str = ""
    entry_actions: List[Action] = field(default_factory=list)
    exit_actions: List[Action] = field(default_factory=list)
    parent_state: Optional["State"] = None
    sub_states: List["State"] = field(default_factory=list)
    exit_transitions: List[Transition] = field(default_factory=list)
    entry_transitions: List[Transition] = field(default_factory=list)


@dataclass
class FSM:
    name: str = ""
    states: Dict[str, State] = field(default_factory=dict)
    transitions: List[Transition] = field(default_factory=list)

    def find_state(self, name: str) -> Optional[State]:
        return self.states.get(name, None)

    def add_state(self, name: str) -> State:
        state = State()
        state.name = name
        self.states[state.name] = state
        return state

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


@dataclass
class Entity:
    id: str
    name: Optional[str] = None
    description: Optional[str] = None

    def __str__(self) -> str:
        return f"id:{self.id}, name:{self.name}"

@dataclass
class Trigger(Entity):
    pass


@dataclass
class Effect(Entity):
    text: Optional[str] = None


@dataclass
class Guard(Entity):
    condition: Optional[str] = None


class TransitionType(Enum):
    INVALID  = 1
    EXTERNAL = 2
    INTERNAL = 3
    LOCAL    = 4


@dataclass
class Transition(Entity):
    source: Optional[Vertex] = None
    target: Optional[Vertex] = None
    type: TransitionType = TransitionType.INVALID
    stereotype: Optional[str] = None
    trigger: Optional[Trigger] = None
    guard: Optional[Guard] = None
    effect: Optional[Effect] = None

@dataclass
class Vertex(Entity):
    container: Optional[Region] = None
    incoming_transitions: List[Transition] = field(default_factory=list)
    outgoing_transitions: List[Transition] = field(default_factory=list)
    stereotype: Optional[str] = None


class StateType(Enum):
    INVALID   = 0
    SIMPLE    = 1
    COMPOSITE = 2


@dataclass
class State(Vertex):
    type: StateType = StateType.INVALID
    entry_effects: List[Effect] = field(default_factory=list)
    exit_effects: List[Effect] = field(default_factory=list)
    regions: List[Region] = field(default_factory=list)


@dataclass
class PseudoState(Vertex):
    pass


@dataclass
class ChoicePseudoState(PseudoState):
    pass


@dataclass
class InitialState(State):
    pass


@dataclass
class FinalState(State):
    pass


@dataclass
class Region(Entity):
    states: Dict[str, State] = field(default_factory=dict)
    transitions: Dict[str, Transition] = field(default_factory=dict)
    choice_pseudo_states: Dict[str, ChoicePseudoState] = field(default_factory=dict)


@dataclass
class StateMachine(Entity):
    region: Optional[Region] = None
    entities: Dict[str, State] = field(default_factory=dict)

    def get_or_create_state(self, name: str) -> State:
        if state := self.states.get(name, None) is None:
            state = State()
            state.name = name
            self.states[state.name] = state
        return state

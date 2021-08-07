from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Type, cast
from enum import Enum
from datetime import datetime

MODEL_VERSION_MAJOR = 1
MODEL_VERSION_MINOR = 0

@dataclass
class Entity:
    id: Id
    name: Optional[str] = None
    description: Optional[str] = None

    def __str__(self) -> str:
        return f"id:{self.id}, name:{self.name}"


@dataclass
class Event(Entity):
    pass


@dataclass
class Action(Entity):
    text: Optional[str] = None


@dataclass
class Guard(Entity):
    condition: Optional[str] = None


class TransitionType(Enum):
    INVALID = 1
    EXTERNAL = 2
    INTERNAL = 3
    LOCAL = 4


@dataclass
class Transition(Entity):
    source: Optional[Vertex] = None
    target: Optional[Vertex] = None
    type: TransitionType = TransitionType.INVALID
    stereotype: Optional[str] = None
    trigger: Optional[Event] = None
    guard: Optional[Guard] = None
    action: Optional[Action] = None


@dataclass
class Vertex(Entity):
    container: Optional[Region] = None
    incoming_transitions: List[Transition] = field(default_factory=list)
    outgoing_transitions: List[Transition] = field(default_factory=list)
    stereotype: Optional[str] = None


class StateType(Enum):
    INVALID = 0
    SIMPLE = 1
    COMPOSITE = 2


@dataclass
class State(Vertex):
    type: StateType = StateType.INVALID
    entry_actions: List[Action] = field(default_factory=list)
    exit_actions: List[Action] = field(default_factory=list)
    regions: List[Id, Region] = field(default_factory=list)


@dataclass
class PseudoState(Vertex):
    pass


@dataclass
class Choice(PseudoState):
    pass


@dataclass
class InitialState(State):
    pass


@dataclass
class FinalState(State):
    pass


@dataclass
class Region(Entity):
    states: List[Id, State] = field(default_factory=list)
    transitions: List[Id, Transition] = field(default_factory=list)
    choices: List[Id, Choice] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Does this region own any entities?"""
        return not (self.states or self.transitions or self.choices)

@dataclass
class Metadata:
    model_version_major: int = MODEL_VERSION_MAJOR
    model_version_minor: int = MODEL_VERSION_MINOR
    generated_on: datetime = datetime.now()
    source_diagram: Optional[str] = None

@dataclass
class StateMachine(Entity):
    metadata: Metadata = Metadata()
    region: Optional[Region] = None
    entities: Dict[Id, AnyEntity] = field(default_factory=dict)

    def _filter_entities(self, EntityType: Type[AnyEntity]) -> Dict[str, AnyEntity]:
        return dict(filter(lambda t: type(t[1]) is EntityType, self.entities.items()))

    def _gen_entity_id(self, EntityType: Type[AnyEntity]) -> Id:
        return f"{self.id}.{EntityType.__name__.lower()}{len(self._filter_entities(EntityType)) + 1}"

    def _new_entity(self, EntityType: Type[AnyEntity]) -> AnyEntity:
        entity = EntityType(id=self._gen_entity_id(EntityType))
        self.entities[entity.id] = entity
        return entity

    def states(self) -> Dict[Id, State]:
        return cast(Dict[Id, State], self._filter_entities(State))

    def regions(self) -> Dict[Id, Region]:
        return cast(Dict[Id, Region], self._filter_entities(Region))

    def choices(self) -> Dict[Id, Choice]:
        return cast(Dict[Id, Choice], self._filter_entities(Choice))

    def transitions(self) -> Dict[Id, Transition]:
        return cast(Dict[Id, Transition], self._filter_entities(Transition))

    def new_state(self) -> State:
        return cast(State, self._new_entity(State))

    def new_initial_state(self) -> InitialState:
        return cast(InitialState, self._new_entity(InitialState))

    def new_final_state(self) -> FinalState:
        return cast(FinalState, self._new_entity(FinalState))

    def new_region(self) -> Region:
        return cast(Region, self._new_entity(Region))

    def new_transition(self) -> Transition:
        return cast(Transition, self._new_entity(Transition))

    def new_event(self) -> Event:
        return cast(Event, self._new_entity(Event))

    def new_action(self) -> Action:
        return cast(Action, self._new_entity(Action))

    def new_guard(self) -> Guard:
        return cast(Guard, self._new_entity(Guard))

    def new_choice(self) -> Choice:
        return cast(Choice, self._new_entity(Choice))


# Type aliases
Id = str
AnyEntity = Union[
    Event,
    Action,
    Guard,
    Transition,
    State,
    Choice,
    InitialState,
    FinalState,
    Region,
    StateMachine,
]

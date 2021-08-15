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
    region: Optional[Region] = None
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
    sub_regions: List[Region] = field(default_factory=list)


@dataclass
class PseudoState(Vertex):
    pass


@dataclass
class Choice(PseudoState):
    pass


@dataclass
class InitialState(PseudoState):
    pass


@dataclass
class TerminalState(PseudoState):
    pass


@dataclass
class Region(Entity):
    initial_state: Optional[InitialState] = None
    terminal_state: Optional[TerminalState] = None
    state: Optional[State] = None
    sub_vertices: List[Vertex] = field(default_factory=list)
    transitions: List[Transition] = field(default_factory=list)

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

    def _filter_entities(
        self, EntityType: Type[AnyEntity], include_subclasses=False
    ) -> Dict[str, AnyEntity]:
        if include_subclasses:
            select = lambda entity: isinstance(entity, EntityType)
        else:
            select = lambda entity: type(entity) is EntityType

        return dict(filter(lambda e: select(e[1]), self.entities.items()))

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

    def vertices(self) -> Dict[Id, Vertex]:
        return cast(
            Dict[Id, Vertex], self._filter_entities(Vertex, include_subclasses=True)
        )

    def transitions(self) -> Dict[Id, Transition]:
        return cast(Dict[Id, Transition], self._filter_entities(Transition))

    def new_state(self) -> State:
        return cast(State, self._new_entity(State))

    def new_initial_state(self) -> InitialState:
        return cast(InitialState, self._new_entity(InitialState))

    def new_terminal_state(self) -> TerminalState:
        return cast(TerminalState, self._new_entity(TerminalState))

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
    Vertex,
    State,
    Choice,
    InitialState,
    TerminalState,
    Region,
    StateMachine,
]

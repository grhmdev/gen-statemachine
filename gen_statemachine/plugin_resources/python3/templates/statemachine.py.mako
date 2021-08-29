<%
import gen_statemachine

_null_event_name = "_null_event"
_initial_state_name = "_initial_state"
_terminal_state_name = "_terminal_state"

class IfOrElif:
    def __init__(self):
        self.called = False
    def __next__(self):
        if not self.called:
            self.called = True
            return "if"
        return "elif"

def vertex_namespace(vertex):
    return (vertex.region.state.name 
            if vertex.region.state 
            else ""
    )

def enum_name(vertex):
    if isinstance(vertex, gen_statemachine.model.InitialState):
        return vertex_namespace(vertex) + _initial_state_name
    elif isinstance(vertex, gen_statemachine.model.TerminalState):
        return vertex_namespace(vertex) + _terminal_state_name
    else:
        return vertex.name

def states_with_entry_actions():
    return [state for state in statemachine.states().values() if state.entry_actions]

def states_with_exit_actions():
    return [state for state in statemachine.states().values() if state.exit_actions]

def vertices_with_outgoing_transitions():
    return [vertex for vertex in statemachine.vertices().values() if vertex.outgoing_transitions]

def transitions_by_source():
    transitions = {}
    for transition in statemachine.transitions().values():
        key = enum_name(transition.source)
        if key not in transitions:
            transitions[key] = []
        transitions[key].append(transition)
    return transitions

def vertex_outgoing_transitions_by_event(vertex):
    transitions = {}
    for transition in vertex.outgoing_transitions:
        key = transition.event.name if transition.event else _null_event_name
        if key not in transitions:
            transitions[key] = []
        transitions[key].append(transition)
    return transitions

def region_set_for_vertex(vertex):
    regions = []
    region = vertex.region
    while region.state:
        regions.append(region)
        region = region.state.region
    return regions

def exited_states(transition):
    exited_states = []
    source_regions = region_set_for_vertex(transition.source)
    target_regions = region_set_for_vertex(transition.target)
    exited_regions = [source_region for source_region in source_regions if source_region not in target_regions]
    exited_states += [region.state for region in exited_regions if region.state]
    return exited_states

def entered_states(transition):
    entered_states = []
    source_regions = region_set_for_vertex(transition.source)
    target_regions = region_set_for_vertex(transition.target)
    entered_regions = [target_region for target_region in target_regions if target_region not in source_regions]
    entered_states += [region.state for region in entered_regions if region.state]
    entered_states.reverse()
    return entered_states
%>\
<%def name="exit_superstates(transition)">\
% for exited_state in exited_states(transition):
                self._exit_state(State.${exited_state.name})
% endfor
</%def>\
<%def name="enter_superstates(transition)">\
% for entered_state in entered_states(transition):
                self._enter_state(State.${entered_state.name})
% endfor
</%def>\
<%def name="transition_action(transition)">\
% if transition.action:
                ${transition.action.text}
% endif
</%def>\
from enum import Enum
from queue import SimpleQueue

class State(Enum):
    % for vertex in statemachine.vertices().values():
    ${enum_name(vertex)} = ${loop.index}
    % endfor

class Event(Enum):
    ${_null_event_name} = 0
    % for event in statemachine.events().values():
    ${event.name} = ${loop.index + 1}
    % endfor

class Statemachine:
    def __init__(self):
        self._current_state = State._initial_state
        self._event_queue = SimpleQueue()

    # State transition hooks
    def on_state_exit(self, state): pass
    def on_state_exited(self, state): pass
    def on_state_entry(self, state) : pass
    def on_state_entered(self, state): pass

    def start(self):
        self.queue_event(Event.${_null_event_name})
        self.process_events()

    def queue_event(self, event):
        self._event_queue.put(event)

    def process_events(self):
        while not self._event_queue.empty():
            self._process_event(self._event_queue.get())

    def _process_event(self, event):
        return

    def _push_transition(self, target_state):
        self._transition_queue.put(target_state)

    def _transition_to(self, target_state):
<% if_elif = IfOrElif() %>\
        % for source_name, transitions in transitions_by_source().items():
        ${next(if_elif)} self._current_state is State.${source_name}:
            self._exit_state(State.${source_name})
<% if_elif1 = IfOrElif() %>\
            % for transition in transitions:
            ${next(if_elif1)} target_state is State.${enum_name(transition.target)}:
${exit_superstates(transition)}\
${transition_action(transition)}\
${enter_superstates(transition)}\
            % endfor
                self._enter_state(target_state)
        % endfor
        self.queue_event(Event._null_event)

    def _exit_state(self, state):
        self.on_state_exit(state)
<% if_elif = IfOrElif() %>\
        % for state in states_with_exit_actions():
        ${next(if_elif)} state is State.${enum_name(state)}:
<% if_elif1 = IfOrElif() %>\
            % for exit_action in state.exit_actions:
            ${exit_action.text}
            % endfor
        % endfor
        self.on_state_exited(state)

    def _enter_state(self, state):
        self.on_state_entry(state)
<% if_elif = IfOrElif() %>\
        % for state in states_with_entry_actions():
        ${next(if_elif)} state is State.${enum_name(state)}:
<% if_elif1 = IfOrElif() %>\
            % for entry_action in state.entry_actions:
            ${entry_action.text}
            % endfor
        % endfor
        self._current_state = state
        self.on_state_entered(state)
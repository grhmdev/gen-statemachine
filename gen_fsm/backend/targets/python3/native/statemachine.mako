<%
import gen_fsm
import gen_fsm.model

_null_event_name = "_null_event"
_initial_state_name = "_initial_state"
_terminal_state_name = "_terminal_state"
_event_handler_prefix = "_process_event_in_"
_indent = "    "

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
    if isinstance(vertex, gen_fsm.model.InitialState):
        return vertex_namespace(vertex) + _initial_state_name
    elif isinstance(vertex, gen_fsm.model.TerminalState):
        return vertex_namespace(vertex) + _terminal_state_name
    else:
        return vertex.name

def states_with_entry_actions():
    return [state for state in statemachine.states().values() if state.entry_actions]

def states_with_exit_actions():
    return [state for state in statemachine.states().values() if state.exit_actions]

def vertices_with_outgoing_transitions():
    return [vertex for vertex in statemachine.vertices().values() if vertex.outgoing_transitions]

def terminal_states_in_sub_regions():
    return [terminal_state for terminal_state in statemachine.terminal_states().values() if terminal_state.region.state]

def transitions_by_source():
    transitions = {}
    for transition in statemachine.transitions().values():
        key = enum_name(transition.source)
        if key not in transitions:
            transitions[key] = []
        transitions[key].append(transition)
    return transitions

def preprocess_model():
    return

def transitions_by_source_and_event():
    transitions = {}
    for transition in statemachine.transitions().values():
        source_name = enum_name(transition.source)
        event_name = _null_event_name if not transition.trigger else enum_name(transition.trigger)
        key = (source_name, event_name)
        if key not in transitions:
            transitions[key] = []
        transitions[key].append(transition)
    return transitions

def vertex_outgoing_transitions_by_event(vertex):
    transitions = {}
    for transition in vertex.outgoing_transitions:
        key = transition.trigger.name if transition.trigger else _null_event_name
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
<%def name="exit_superstates(transition, indent_str)">\
% for exited_state in exited_states(transition):
${indent_str}self._exit_state(State.${enum_name(exited_state)})
% endfor
</%def>\
<%def name="enter_superstates(transition, indent_str)">\
% for entered_state in entered_states(transition):
${indent_str}self._enter_state(State.${enum_name(entered_state)})
% endfor
</%def>\
<%def name="transition_action(transition, indent_str)">\
% if transition.action:
${indent_str}${transition.action.text}
% endif
</%def>\
<%def name="enter_substates(vertex, indent_str)">\
% if type(vertex) is gen_fsm.model.State and vertex.sub_regions:
${indent_str}self._enter_state(State.${enum_name(vertex.sub_regions[0].initial_state)})
${enter_substates(vertex.sub_regions[0].initial_state, indent_str)}\
% endif
</%def>\
<%def name="transition_block(transition, indent_lvl)">\
<% indent_str = _indent * indent_lvl %>\
${indent_str}self._exit_state(State.${enum_name(transition.source)})
${exit_superstates(transition, indent_str)}\
${transition_action(transition, indent_str)}\
${enter_superstates(transition, indent_str)}\
${indent_str}self._enter_state(State.${enum_name(transition.target)})
${enter_substates(transition.target, indent_str)}\
</%def>\
<% preprocess_model() %>\
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

class StateMachine:
    def __init__(self):
        self._current_state = State._initial_state
        self._event_queue = SimpleQueue()
        self._event_handlers = {}
        % for source_name, event_name in transitions_by_source_and_event().keys():
        self._event_handlers[(State.${source_name}, Event.${event_name})] = self._process_${event_name}_in_${source_name}
        % endfor
        % for terminal_state in terminal_states_in_sub_regions():
        self._event_handlers[(State.${enum_name(terminal_state)}, Event.${_null_event_name})] = self._process_${_null_event_name}_in_${enum_name(terminal_state)}
        % endfor

    def start(self):
        self.queue_event(Event.${_null_event_name})
        self.process_events()

    def queue_event(self, event: Event):
        self._event_queue.put(event)

    def process_events(self):
        while not self._event_queue.empty():
            self._process_event(self._event_queue.get())

    def _process_event(self, event: Event):
        if handler := self._event_handlers.get((self._current_state, event), None):
            handler(event)
            self.queue_event(Event.${_null_event_name})

    def _exit_state(self, state: State):
<% if_elif = IfOrElif() %>\
        % for state in states_with_exit_actions():
        ${next(if_elif)} state is State.${enum_name(state)}:
            % for action in state.exit_actions:
            ${action.text}
            % endfor
        % endfor
        % if not states_with_exit_actions():
        pass
        % endif

    def _enter_state(self, state: State):
<% if_elif = IfOrElif() %>\
        % for state in states_with_entry_actions():
        ${next(if_elif)} state is State.${enum_name(state)}:
            % for action in state.entry_actions:
            ${action.text}
            % endfor
        % endfor
        self._current_state = state

% for key, transitions in transitions_by_source_and_event().items():
<% source_name = key[0] %>\
<% event_name = key[1] %>\
<% if_elif = IfOrElif() %>\
<% transitions_with_guards = [t for t in transitions if t.guard] %>\
<% transitions_without_guards = [t for t in transitions if not t.guard] %>\
    def _process_${event_name}_in_${source_name}(self, event: Event):
        % for transition in transitions_with_guards:
        ${next(if_elif)} ${transition.guard.condition}:
${transition_block(transition, indent_lvl=3)}\
        % endfor
        % for transition in transitions_without_guards:
        % if transitions_with_guards:
        else:
${transition_block(transition, indent_lvl=3)}\
        % else:
${transition_block(transition, indent_lvl=2)}\
        % endif
        % endfor

% endfor
% for terminal_state in terminal_states_in_sub_regions():
    def _process_${_null_event_name}_in_${enum_name(terminal_state)}(self, event: Event):
        self._exit_state(State.${enum_name(terminal_state)})
        self._current_state = State.${enum_name(terminal_state.region.state)}

% endfor

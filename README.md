# gen_fsm

`gen_fsm` generates state machine code from PlantUML's [state diagrams](https://plantuml.com/state-diagram). It features an extensible backend that can be used to target any language or implementation. It aims to remove the need for programmers to write boilerplate code, allowing them to focus on state machine design rather than implementation.

## Supported language

> Note: `gen_fsm` is not a syntax checker, nor will it enforce completely correct grammar

The following PlantUML language features are supported:

- Simple states and composite states
- State transitions
- State aliasing, e.g.: `state "long name.." as long1`
- Notes
- Conditionals
- State inputs and outputs: Entry/exit points, input/output pins, expansion input/outputs
- Stereotypes

The following language features are supported but will not have an impact on the generated outputs:

- Comments
- Arrow directions
- Arrow line color and style

The following language features are currently not supported and will result in an error if encountered by the parser:

- Sub-state history, e.g. `[H], [H*]`
- Forks and concurrent state
- Notes on links, e.g. `note on link`

## Extended Language Features

### State Entry and Exit Actions

Entry and exit actions can be expressed through state descriptions. An entry or exit action is prefixed with either `entry/` or `exit/`:

```
state Powering_On : entry/ initialise();
state Powering_Off : exit/ send_shutdown();
```

Multiple actions can be added to any state:

```
state Data_Received : UI views are updated with the latest data
state Data_Received : entry/ update_table_view();
state Data_Received : entry/ update_summary_view();
state Data_received : exit/ redraw();
```

### Transition Triggers, Guards and Actions

PlantUML's transitions are used to express trigger events, guards constraints and actions. Transitions with these features are written with the following format:

`<state-name> --> <state-name> : [<trigger>] [‘[‘ <guard-constraint>’]’] [‘/’ <behavior-expression>]`.

Some examples are provided below.

1. Default transition with action:

```
Initializing --> Ready : /Log::info("Subsystem initialized")
```

2. Transition with trigger event:

```
Enabled --> Disabled : EvDisable
```

3. Transition with guard constraint:

```
powering_on --> active : [skip_power_on_test == true]
```

4. Transition with trigger event, guard constraint and action:

```
TransactionInProgress --> TransactionSucceeded : StatusReceived [status is StatusType.SUCCEEDED] / print("Transaction succeeded")
```

## Examples

After installing with `make install`, try running one of the examples below. These are simple and self-contained programs that demonstrate some of the capability of `gen_fsm`.

1. `make example-hello-world`

2. `make example-washing-machine`

## Dev Dependencies

- [Python](https://www.python.org/) [>=3.8]
- [Poetry](https://python-poetry.org/) [>=1.1.5]
- [PlantUML](https://plantuml.com/) [>=1.2019.9]
    - Required to use `make diagrams` only

## Road Map

### Version 1.0.0

* Add support for following PlantUML language:

    - `<style>..</style>` sections
    - `skinparam`
    - State colours and colour transitions
    - Captions
    - Legends
    - `scale`
    - Title
    - Header/footer

* Additional documentation

* Additional testing

* Alternative Python implementation templates

* Basic model validation

* Analyse alternative parsers to replace home-cooked implementation

### Version x.x.x

* Code-gen templates for more languages

* Data passing for transition events
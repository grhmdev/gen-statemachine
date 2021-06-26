# PlantUML Statemachine Code Generator

This tool generates statemachines from PlantUML's state diagrams.

## Disclaimers

- This is not a syntax checker, nor will it enforce completely correct grammar.

## Supported language

- States and sub-states
- State transitions
- State aliasing

*TODO*

- Notes
- State inputs and outputs: Entry/exit points, input/output pins, expansion input/outputs
- Stereotypes
- Conditional

The following language features are supported but will be ignored by the tool and not have an impact on the generated outputs.

*TODO*

- `<style>..</style>` sections
- skinparam
- State colours and colour transitions
- Directional and coloured transition arrow styles
- Arrow directions
- Arrow line color and style

## Unsupported language

- Sub-state history: [H], [H*]
- Forks and concurrent state
- Notes on links, e.g. `note on link`

## Usage

TODO

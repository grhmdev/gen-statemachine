# State Machine Code Generator

This tool generates statemachines from PlantUML's state diagrams.

## Disclaimers

- This is not a syntax checker, nor will it enforce completely correct grammar.

## Supported language

- States and sub-states
- State transitions
- State aliasing
- Notes
- Conditionals
- State inputs and outputs: Entry/exit points, input/output pins, expansion input/outputs
- Stereotypes

*TODO*
- Comments

The following language features are supported but will be ignored by the tool and will not have an impact on the generated outputs.

- Arrow directions
- Arrow line color and style

*TODO*
- `<style>..</style>` sections
- `skinparam`
- State colours and colour transitions
- Captions
- Legends
- `scale`
- Title
- Header/footer


## Unsupported language

- Sub-state history, e.g. `[H], [H*]`
- Forks and concurrent state
- Notes on links, e.g. `note on link`

## Usage

TODO

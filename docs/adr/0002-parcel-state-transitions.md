# N. Short noun phrase naming the decision

<!-- Copy this file to docs/adr/NNNN-kebab-case-title.md (for example
0001-parcel-state-machine.md). This template does not count towards your two ADRs. -->

## Status

<!-- One of: Proposed, Accepted, Superseded, Deprecated, Rejected. -->
Accepted

## Context

<!-- The forces at play, including the ones pulling the other way. -->
A parcel must follow valid states during delivery. Allowing invalid transitions could cause incorrect parcel information.

## Decision

<!-- One or two sentences in active voice: "We will ..." -->
We will validate each event before changing a parcel's state, and reject invalid transitions.

## Consequences

<!-- What becomes easier and what becomes harder. Be honest. -->
This keeps parcel states consistent and prevents invalid operations. However, we need to define and maintain the allowed transitions.

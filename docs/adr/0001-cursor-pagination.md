# N. Short noun phrase naming the decision

<!-- Copy this file to docs/adr/NNNN-kebab-case-title.md (for example
0001-parcel-state-machine.md). This template does not count towards your two ADRs. -->

## Status

<!-- One of: Proposed, Accepted, Superseded, Deprecated, Rejected. -->
Accepted

## Context

<!-- The forces at play, including the ones pulling the other way. -->
The list of parcels can change when parcels change state. Using an offset may cause parcels to be skipped or repeated while loading pages.

## Decision

<!-- One or two sentences in active voice: "We will ..." -->
We will use cursor pagination to continue loading parcels from the last item in the previous page.

## Consequences

<!-- What becomes easier and what becomes harder. Be honest. -->
This helps reduce skipped or repeated parcels when the list changes. However, the API needs to create and manage cursors.

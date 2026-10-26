# AI usage

Keep all three headings exactly as they are. If this file is missing or any heading is
missing, the grader stops and gives 0 ("AI_USAGE.md missing or incomplete"). The content
is not scored, but your Track Mentor reads it and the W8 defence can ask about it.

## Tools

<!-- Which tools you used (ChatGPT, Copilot, Claude, Cursor, none...) and for which parts. -->
ChatGPT

## What AI got wrong

<!-- At least one thing an assistant got wrong that you changed, and how you noticed
(a test failed, the docs said otherwise, you ran it). -->
As I'm right now learning how to write an API, AI explained to me how this code works and why. But I noticed that AI was implementing libraries that weren't used in the code, AI told me about the hidden tests that might fail and how I should figure it out by myself.

## In my own words

<!-- Answer without AI, one or two sentences each. -->

1. Why does `listParcels` need a cursor rather than an offset?
A cursor helps us continue from the last item without skipping parcels. An offset may skip parcels that have not been shown yet if parcel states change.

2. Which of your four operations would break the courier app if you renamed one field, and who would have to approve that change?
Renaming a field in `getParcel` could make the courier app unable to read parcel details correctly. The courier app team and the merchant integration team should approve the change if it affects their systems.

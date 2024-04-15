# Solution Intent

  

[SAFe definition](https://scaledagileframework.com/solution-intent/)

  

## Abstract

<!--
Guideline
> Write a short description about what this solution intent is about.
-->

The **bugal** Tool should track all transactions and enable analysis of those. It shall create different types of reports and automatically assign tags to transactions, so the tags can be used for further analysis.

  

## Current Status

<!--
Guideline
> Briefly describe the current state and its shortcoming
-->

From online banking csv or PDF file can be downloaded to show the transaction of dedicated period.  

## Future Status

<!--
Guideline
> Briefly describe the vision for the future status. Rather write about a use-case (e.g. authenticated communication) than about implementation (e.g. provide TLS support).
-->

The tool shall: 
- process the files
- store results persistently
- set some properties to the transactions
- generate reports for analysis
- allow to do some adatations in the report which can be stored persistantlly again
- the tool shall be executed firts over CLI
- for user friendly usage a GUI shall be used for the tool  

## Intent details

### Fixed intent

<!--
Guideline
Add here everything we know about the solution intent which is non-negotiable or already fixed during exploration. This can be:
- Specifications and protocols that need to be followed or implemented
- Non-functional requirements, e.g. performance criteria, applicable safety standards, etc.
When design options reduce during the exploration, design decisions can move from the [Variable intent](#variable-intent) section to this section.
-->
- The tool must support the csv files in new and classic format
- The duplicate transactions must be avoided

#### Fixed features {#fixed-features}

<!--
Guideline
Describe small feature increments that can be shown in a system demo in the scope of one PI.
 - At most a tweet describing the feature
 - At most a tweet describing the benefit hypothesis (what are we going to improve with this feature)
 - If meaningful at this stage a short architectural draft and allocation to high-level components
-->

1. import of the classic csv file into the DB
2. import of the new csv file into the DB
3. check the csv hash before import will be executed into db
4. check hash over the transaction before its import into db

### Variable intent {#variable-intent}

<!--
Guideline
In this area, the solution intent is developed. Add here:
 - New knowledge that comes in over time (technical, business, constraints, guidance, etc.)
 - Different increments of functionality that would be possible.
 - Design options and key decisions
 - New ideas
When a design decision is taken that leads to a feature, please make sure that it is documented in the [Fixed features](#fixed-features) section and mark it as resolved in this section.
No formal guidance is given here, everything is allowed. Some guidance, though:
 - Structure your thoughts properly. Embrace the reader's point of view.
 - Images and models are fine and better than lengthy documentation.
 - Make decisions as late as possible to keep alternatives open.
 - Keep everything at one place - here.
 - This is a high-level abstract document. Don't get lost in details.
 - KISS - keep it simple, stupid!
-->

[Domain Model](https://habababa.ru/cosmicpython/book_ru.html#chapter_01_domain_model)
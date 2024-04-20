# Requirements management UG

## General

The requirements are captured using [StrictDoc](https://github.com/strictdoc-project/strictdoc).
The documents are located in the subfolder "_sdoc_".

### Basic commands

To install the requirements management tool:

```shell
pip install strictdoc
```

To generate the requirements documentation in HTML format:

```shell
strictdoc export .
```

To browse/edit the requirements using StrictDoc's web interface:

```shell
strictdoc server .
```

To generate uid's for new written requirements use the command:
```shell
strictdoc manage auto-uid .
```

### Document maintenance

The subfolder shall contain only sdoc files and sgra file(s) for grammer. 
The index.sdoc collects all specifications for the whole project. 

The sdoc files shall have block:

```shell
[GRAMMAR]
IMPORT_FROM_FILE: grammar.sgra
```
instead of definingn own grammar.

After Some `strictdoc manage auto-uid` the block will be replaced by the grammar within the files.

## Document Levels

### L1 Requirements

Top Level requirements without any implementation relevance. The L1 requirements are describing what a user should be able to do with the tool/system.
Coverage
:  to be covered by the L2 and/or L3 requirements.

### L2 Requirements

Design decisions with rational, explaining how the L1 requirements shall be realized in the project. All L2 requirements shall have at least one parent L1 requirement.
- what external packages to be used
- what technologies to be used e.g. which data base technology
- which layers shall exist
- which modules shall exist and to which layer they shall belong to
- level of the abstraction
- what design pattern to be used
- how the tool shall be deployed
- how the tool shall be packaged

Coverage
: design
: Users guide
: source code
: integration tests
: L3 requirements

### L3 Requirements

SW implementation requirements, specifying detailed SW requirements:
- API description
  - signature
  - functional behavior
- Classes of the modules
- functional behavior 

Coverage
: All requirements shall be automatically tested.
: can be covered by a test requirement

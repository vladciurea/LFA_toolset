# Formal Languages Toolkit

Two command-line tools written in Python for working with formal languages and automata theory:

| Tool | Description |
|------|-------------|
| [**CFG → Chomsky Normal Form**](#1-cfg--chomsky-normal-form-converter) | Converts a context-free grammar into Chomsky Normal Form (CNF) |
| [**PDA Word Acceptor**](#2-pushdown-automaton-pda-word-acceptor) | Simulates a pushdown automaton and decides whether a word is accepted |

Both tools use only the Python standard library — no external dependencies.

---

## Table of Contents

- [Repository Structure](#repository-structure)
- [Requirements](#requirements)
- [1. CFG → Chomsky Normal Form Converter](#1-cfg--chomsky-normal-form-converter)
  - [Algorithm](#algorithm)
  - [Input Format](#input-format)
  - [Usage](#usage)
  - [Example](#example)
  - [Notes and Limitations](#notes-and-limitations)
- [2. Pushdown Automaton (PDA) Word Acceptor](#2-pushdown-automaton-pda-word-acceptor)
  - [How It Works](#how-it-works)
  - [Input Format](#input-format-1)
  - [Usage](#usage-1)
  - [Example](#example-1)
  - [Notes and Limitations](#notes-and-limitations-1)

---

## Repository Structure

```
.
├── README.md
├── chomsky/
│   ├── chomsky.py
│   └── input            # sample grammar
│   └── output          
└── pda/
    ├── pda.py
    └── input            # sample automaton
    └── output
```

## Requirements

- Python 3.8 or newer

---

## 1. CFG → Chomsky Normal Form Converter

`chomsky/chomsky.py` reads a context-free grammar from a text file and converts it to an equivalent grammar in **Chomsky Normal Form**, where every production has one of the following shapes:

- `A -> BC` (two non-terminals)
- `A -> a` (a single terminal)
- `S0 -> λ` (only for the start symbol, and only if the language contains the empty word)

The resulting grammar is printed to the console and saved to an output file in the same format as the input, so it can be fed back into other tools.

### Algorithm

The conversion follows the standard sequence of transformations:

1. **New start symbol** — introduces `S0 -> S`, so the start symbol never appears on a right-hand side.
2. **Eliminate λ-productions** — computes the nullable non-terminals and generates all productions obtained by omitting any subset of nullable symbols. If the original language contains λ, the rule `S0 -> λ` is preserved.
3. **Eliminate unit productions** — removes rules of the form `A -> B`, copying the productions of `B` into `A`.
4. **Eliminate useless symbols** — keeps only symbols that are both *generative* (derive a terminal string) and *reachable* from the start symbol.
5. **Isolate terminals** — in productions longer than one symbol, replaces each terminal `a` with a fresh non-terminal `Xa<n>` and adds `Xa<n> -> a`.
6. **Binarize long productions** — splits productions with more than two symbols into chains of binary rules using helper non-terminals `Y<n>`. Identical suffixes are cached and share the same helper symbol, avoiding duplicate rules.

### Input Format

The tool reads a file named `input` from the current working directory:

```
<non-terminals, space-separated>
<terminals, space-separated>
<number of productions N>
<non-terminal> <right-hand side>      (N lines, one production per line)
<start symbol>
```

Conventions:

- `l` (lowercase L) denotes **λ** (the empty word). It may appear in the terminal list and as a right-hand side.
- Each right-hand side is written as a single token **without spaces** (e.g. `aAb`).
- Alternatives of the same non-terminal are written on separate lines.
- Multi-character non-terminals are supported; symbols are recognized using longest-match parsing.

### Usage

```bash
cd chomsky
python chomsky.py
```

The program reads `input` and writes the result to `output` in the same directory (and prints both grammars to stdout).

### Example

**`input`**

```
S A B
a b l
6
S AB
S a
A aA
A l
B b
B l
S
```

Equivalent to the grammar:

```
S -> AB | a
A -> aA | λ
B -> b | λ
```

**Console output**

```
GRAMATICA INITIALA
  S -> AB | a
  A -> aA | l
  B -> b | l
Start: S

 FORMA NORMALA CHOMSKY
  A -> Xa0A | a
  B -> b
  S0 -> l | AB | a | Xa0A | b
  Xa0 -> a
```

**`output`**

```
S0 A B Xa0
a b l
9
S0 l
S0 AB
S0 a
S0 Xa0A
S0 b
A Xa0A
A a
B b
Xa0 a
S0
```

### Notes and Limitations

- The symbol `l` is reserved for λ and therefore cannot be used as a regular terminal.
- Productions must be written without spaces inside the right-hand side.
- The input path is fixed (`input` in the working directory) and the output path is fixed (`output`).

---

## 2. Pushdown Automaton (PDA) Word Acceptor

`pda/pda.py` reads the definition of a pushdown automaton together with an input word, and decides whether the automaton **accepts** or **rejects** it. Non-determinism is handled by exploring all possible computations.

### How It Works

- A *configuration* is a triple `(state, input position, stack)`.
- The simulator performs a **breadth-first search** over configurations, starting from `(initial state, 0, [initial stack symbol])`.
- A set of visited configurations prevents processing the same configuration twice.
- Every transition pops the top-of-stack symbol and pushes a (possibly empty) string. The pushed string is placed so that its **first character ends up on top of the stack**.
- A transition may read an input symbol or read nothing (λ-move).
- The word is accepted as soon as the whole input has been consumed and the configured **acceptance condition** holds.

Supported acceptance modes:

| Mode | Accepts when… |
|------|---------------|
| `stare_finala` | the automaton is in a final state |
| `stiva_goala` | the stack is empty |
| `ambele` | the automaton is in a final state **and** the stack is empty |

### Input Format

```
<states, space-separated>
<input alphabet, space-separated>
<number of transitions N>
<state> <read> <top> <next state> <push>      (N lines)
<initial state>
<initial stack symbol>
<final states, space-separated>
<acceptance mode: stare_finala | stiva_goala | ambele>
<word to test>
```

Conventions:

- The empty word / empty push / no-read move is written as `lambda`, `λ` or `_`.
- Each transition has exactly five whitespace-separated fields: `current_state  read_symbol  stack_top  next_state  string_to_push`.
- The stack symbols and input symbols are single characters (the pushed string is interpreted character by character).

### Usage

```bash
cd pda
python pda.py [input_file] [output_file]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `input_file` | `input` | Path to the automaton definition |
| `output_file` | `output` | File where the result is written |

The output file contains a single line: `Acceptat` (accepted) or `Respins` (rejected).

### Example

The following PDA recognizes the language `{ aⁿbⁿ | n ≥ 1 }` by final state.

**`input`**

```
q0 q1 q2
a b
5
q0 a Z q0 AZ
q0 a A q0 AA
q0 b A q1 lambda
q1 b A q1 lambda
q1 lambda Z q2 Z
q0
Z
q2
stare_finala
aaabbb
```

```bash
$ python pda.py input output
$ cat output
Acceptat
```

Changing the last line to `aabbb` produces `Respins`.

### Notes and Limitations

- Because the search is over *all* computations, the simulation of non-deterministic automata is exhaustive.
- The visited-set only bounds the search when the number of reachable configurations is finite. An automaton containing λ-loops that grow the stack indefinitely may therefore not terminate.

---

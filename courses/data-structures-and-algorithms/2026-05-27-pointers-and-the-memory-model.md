---
concepts: pointers,memory_model,stack,heap
order: 1
source_repo: study
description: The foundation of low-level C. What a pointer really is (just a memory address), the two operators that work with them (& and *), and the two places your data lives — the stack and the heap. Bridges from the TypeScript reference model the learner already knows to C's explicit, manual memory model.
understanding_score: null
last_quizzed: null
prerequisites: []
created: 27-05-2026
last_updated: 27-05-2026
---

# Pointers and the Memory Model

Your goal is to *really* understand how computers work. This tutorial is where that starts — because almost everything confusing about C, and almost everything interesting about how a computer actually runs, comes back to one idea: **memory is just a long row of numbered boxes, and a pointer is a box that holds the number of another box.**

That is the whole secret. By the end of this page you will know exactly what that sentence means, and the rest of Phase 0 will feel like applying it.localstack-init.sh

Here is the good news: **you already use pointers every day in TypeScript** — you just never had to see them. Let's start there.

---

## The Problem

Look at this TypeScript. You have written code like this a thousand times:

```ts
function addItem(list: number[]) {
  list.push(42);          // we change the list inside the function
}

const xs = [1, 2, 3];
addItem(xs);
console.log(xs);          // [1, 2, 3, 42]   <-- the original changed!
```

Now look at this, which feels almost the same but behaves differently:

```ts
function tryChange(x: number) {
  x = 99;                 // we change x inside the function
}

let n = 5;
tryChange(n);
console.log(n);           // 5   <-- nothing changed
```

Why does pushing to an array leak out of the function, but reassigning a number does not?

You probably know the rule of thumb: *"objects and arrays are passed by reference, primitives are passed by value."* That rule is correct, but it is a label, not an explanation. **What *is* a reference?** Where does it live? Why is a number different?

In TypeScript you are not allowed to ask. The language hides it on purpose. In C, you are *forced* to answer — and once you can, that fuzzy "pass by reference" rule turns into something you can see and control. That is what we are unlocking.

---

## Key Concepts

### 1. Memory is a row of numbered boxes

Picture your computer's memory as a very long street of identical houses. Each house holds **one byte** (a number from 0 to 255). Each house has an **address** — house #0, house #1, house #2, and so on, for billions of houses.

```
 address:   1000   1001   1002   1003   1004   1005  ...
          ┌──────┬──────┬──────┬──────┬──────┬──────┐
 byte:    │  ..  │  ..  │  ..  │  ..  │  ..  │  ..  │ ...
          └──────┴──────┴──────┴──────┴──────┴──────┘
```

When you write `int x = 5;`, C picks some free houses, writes the number 5 there, and remembers "the variable named `x` lives at address 1004." (An `int` is usually 4 bytes, so it takes 4 houses — but let's not worry about that yet; think of `x` as living "at 1004.")

```
        x  (an int, value 5)
          ┌──────┐
   1004 → │  5   │
          └──────┘
```

The address — `1004` — is the key idea. Every variable lives *somewhere*, and that somewhere has a number.

### 2. A pointer is a variable that holds an address

Normal variable: holds a value, like `5`.
**Pointer:** holds an *address*, like `1004`.

That is the entire definition. A pointer is not magic — it is just a variable whose value happens to be "the house number of some other variable."

```
        x                      p  (a pointer to x)
      ┌──────┐               ┌────────┐
 1004 │  5   │          2000 │  1004  │
      └──────┘               └────────┘
          ▲                       │
          └───────────────────────┘
              p holds 1004, which is the address of x
```

So `p` "points to" `x` because `p`'s value is the address where `x` lives. Now look back at the TypeScript: a "reference" is exactly this — a hidden value that is really *the address of* an object. When you passed `xs` into `addItem`, you passed its address, so the function could find the real array and change it. When you passed `n`, you passed a *copy of the number 5*, so the function only ever changed its own copy. **C just lets you see the addresses.**

### 3. Two operators: `&` ("address of") and `*` ("value at")

These are the only two new things you need to manipulate pointers:

- `&x`  → "give me the **address of** `x`"  (the house number)
- `*p`  → "give me the **value at** the address stored in `p`"  (go to that house, look inside)

Here is the canonical example. Read each line as an English sentence using the translations above:

```c
int x = 5;            // x holds 5
int *p = &x;          // p holds the ADDRESS of x   (read & as "address of")
printf("%d\n", *p);   // prints 5: *p means "the value at p's address"
*p = 10;              // write 10 INTO the house that p points at
printf("%d\n", x);    // prints 10  <-- we changed x without naming x!
```

That last part is the payoff. `*p = 10;` reached through the pointer and changed `x`. This is the C version of `list.push(42)` reaching out and changing the caller's array.

> **Confusion alert — the `*` symbol does two different jobs.**
> In a *declaration*, `int *p` means "`p` is a pointer to an int." It is describing the *type*.
> In an *expression*, `*p` means "go fetch the value at that address." It is an *action*.
> Same symbol, two meanings. Everyone trips on this at first — when you see `*`, ask yourself: "am I declaring a variable, or using one?"

### 4. Stack vs Heap — the two neighborhoods

Not all memory is the same. There are two regions you must learn to tell apart:

```
   high addresses
  ┌───────────────────────────┐
  │           STACK           │   ← function locals live here
  │   automatic, fast,        │     created when a function is called,
  │   freed for you           │     destroyed when it returns
  │            │              │
  │            ▼  (grows down) │
  │                           │
  │            ▲  (grows up)   │
  │            │              │
  │           HEAP            │   ← memory you request with malloc()
  │   manual: YOU free it     │     lives until YOU say free()
  └───────────────────────────┘
   low addresses
```

- **The stack** is automatic. Every time a function runs, its local variables get houses on the stack. When the function returns, those houses are *instantly reclaimed* — gone. You do nothing; it is free and automatic. `int x = 5;` inside a function lives on the stack.

- **The heap** is manual. When you need memory that must *outlive* the function that created it — or whose size you only learn at runtime — you ask the system for it with `malloc()` (next tutorial). The heap does **not** clean up after itself. You must hand it back with `free()`.

Here is the connection to your whole career so far: **in TypeScript and C#, every object lives on a heap, and a garbage collector quietly frees it when nobody points to it anymore.** You have *always* used a heap — you just never had to manage it. C hands you the keys to that heap and says "it's yours now, and so is the responsibility." That shift — from "the runtime frees memory" to "*I* free memory" — is the single biggest mental change in Phase 0. We tackle it head-on in Tutorial 2.

### 5. The trap this sets up (a preview)

Because stack memory vanishes the moment a function returns, this is one of the most famous bugs in C:

```c
int *broken(void) {
    int local = 42;
    return &local;     // returning the ADDRESS of a stack variable...
}                      // ...but `local`'s house is reclaimed RIGHT HERE.
```

The caller gets an address that now points to a reclaimed house — a **dangling pointer**. It might still *look* like 42 for a moment, then get overwritten by the next function call. This is exactly the kind of bug that the `sanitizers` skill (Tutorial 2) will catch for you instantly. Keep this example in the back of your mind — it is *why* the heap exists.

---

## Examples — from your world (TS) to C

### Example 1: The "reference" you already knew

| TypeScript (hidden) | C (explicit) |
| --- | --- |
| `addItem(xs)` passes a *reference* to the array | you pass `&x` — the actual address |
| inside, `list.push(42)` mutates the original | inside, `*p = 10` mutates the original |
| `tryChange(n)` passes a *copy* of the number | passing `int x` (not `int *x`) copies the value |

**What this demonstrates:** "pass by reference vs pass by value" was never two different rules — it was just *whether an address or a copy got handed over*. C makes the choice visible and puts it in your hands.

### Example 2: Reading a pointer declaration out loud

```c
int   x;     // "x is an int"
int  *p;     // "p is a pointer to an int"
int **pp;    // "pp is a pointer to a pointer to an int"
```

**What this demonstrates:** read these right-to-left. The `*` count tells you how many "hops" away from the actual `int` you are. You will rarely need `**` early on, but recognizing it stops it from being scary later.

---

## Try It Yourself

You write the code here — that is the whole point of this study folder. I will guide, review, and help you debug, but your hands type every line. Put these in a file like `study/phase0/pointers.c`.

**Compile with warnings on** (get used to this command — those flags are your safety net, and `-g` adds the debug info we will need for `gdb`):

```
gcc -Wall -Wextra -g pointers.c -o pointers && ./pointers
```

**Exercise A — Address explorer (warm-up).**
Declare three `int` variables. Print the *address* of each one using `printf("%p\n", (void*)&myvar);`. Run it. Look at the numbers: are they close together? Are they 4 apart? What does that tell you about where stack variables live?

**Exercise B — Change a value through a pointer (the core skill).**
Write a function `void increment(int *n)` that adds 1 to whatever it points at. In `main`, make an `int`, print it, call `increment` on its address, print it again. Prove that the change "leaked out" of the function — just like `list.push(42)` did in TypeScript. *(I am deliberately not writing this for you. If you get stuck, ask me for a hint, not the answer.)*

**Exercise C — Stretch: swap.**
Write `void swap(int *a, int *b)` that exchanges the two values the pointers point to. This is the classic "you cannot do this without pointers" exercise — think about *why* a version taking plain `int a, int b` could never work.

Bring me your code (even if it does not compile) and we will read it together. If it crashes, even better — that is when the real learning happens, and we will use it as our first `gdb` moment.

---

## Summary

- **Memory is a row of numbered houses (addresses).** Every variable lives at some address.
- **A pointer is just a variable whose value is an address** — "the house number of another variable." Nothing more.
- **`&x`** = "address of x"; **`*p`** = "the value at the address in p." `*` also means "pointer to" *in a declaration* — same symbol, two jobs.
- **Stack** = automatic, function-scoped, freed for you. **Heap** = manual, lives until you `free()` it. TS/C# always used a heap + garbage collector for you; C makes you the manager.
- The "pass by reference vs value" rule you knew in TypeScript was really *"address vs copy"* all along — now you can see it and control it.
- **Next:** Tutorial 2 takes you onto the heap with `malloc`/`free`, the idea of *ownership*, and the two classic bugs (leaks and dangling pointers) — with `sanitizers` to catch them live.

---

## Q&A

### 27-05-2026 — "Are the addresses on the stack or the heap?" (revealed a key misconception)

**Asked (by tutor):** Exercise A printed addresses like `0x7ffeb35166fc`. Does living high in memory fit the stack or the heap?

**Learner answered:** "It is pointers located in the heap; the values of those numbers are inside the stack, but the pointer is on the heap."

**What it revealed:** Correct that the *values* (`a`, `b`, `c`) are on the stack. But two misconceptions:
1. Thought `ex1` contained a *pointer* — it does not. `&a` is the **address-of operator** (computes an address as a throwaway value); it does not declare or store a pointer variable. A pointer is a *stored variable that holds an address* (e.g. `int *p = &a;`).
2. Thought something was on the **heap** — nothing is. The heap is only used after calling `malloc()`, which had not happened.

**Correction taught:** In `ex1`, `a`/`b`/`c` are plain `int` locals → all on the **stack**. No pointer is stored; the heap is empty. Heuristic: on Linux x86-64 the stack sits at very high addresses (`0x7fff…`) and the heap much lower (`0x55…`), so `0x7ffe…` ⇒ stack. Distinction to reinforce later: **stored pointer variable** vs **`&` operator**. The malloc-address-vs-stack-address contrast in Tutorial 2 will make stack-vs-heap concrete.

## Quiz History

[Quiz sessions will be recorded here after the learner is quizzed on this topic]

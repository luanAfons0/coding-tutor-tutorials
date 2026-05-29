---
concepts: heap,malloc,free,ownership,memory_leaks,dangling_pointers
order: 2
source_repo: study
description: The garbage-collector-to-manual-memory leap. How to allocate memory on the heap with malloc, hand it back with free, and the new question C forces you to answer — "who owns this memory and when does it die?" Covers the two classic bugs (leaks and dangling pointers) and introduces AddressSanitizer to catch them live. Builds directly on the pointers/stack/heap tutorial.
understanding_score: null
last_quizzed: null
prerequisites: [~/coding-tutor-tutorials/courses/data-structures-and-algorithms/2026-05-27-pointers-and-the-memory-model.md]
created: 27-05-2026
last_updated: 27-05-2026
---

# The Heap: malloc, free, and Ownership

In Tutorial 1 you learned that the **stack** is automatic — locals appear when a function is called and vanish when it returns, and you do nothing. That's wonderful, until it isn't. This tutorial is about the moment the stack stops being enough, and you have to step onto the **heap** and manage memory with your own hands.

This is the big one for you. Every line of TypeScript and C# you've ever written ran on top of a **garbage collector** — a silent helper that watched your objects and freed them when nobody was looking. You're about to fire that helper and do its job yourself. It sounds scary. By the end of this page it will feel like a simple contract you can follow every time.

---

## The Problem

Remember the famous bug from the end of Tutorial 1?

```c
int *broken(void) {
    int local = 42;
    return &local;     // return the address of a stack variable...
}                      // ...but local's house is reclaimed RIGHT HERE.
```

The caller receives an address to a house that no longer belongs to anyone. The stack gave us automatic cleanup, but that's exactly the problem: **what if you need a value to survive *after* the function that made it returns?**

Think about it in your world. When you write this in TypeScript:

```ts
function makeUser(name: string) {
  return { name, createdAt: Date.now() };   // this object outlives the function
}
const u = makeUser("Ana");                  // u is still alive here
```

That object survives `makeUser` returning. Where does it live? **On a heap.** And who cleans it up later? **The garbage collector.** You never thought about it — that's the whole point of a GC.

In C there is no GC. If you want a value to outlive its function, *you* must put it on the heap, and *you* must free it. The question the GC silently answered for you — **"when is this safe to delete?"** — now lands on your desk. That question has a name: **ownership.** It's the soul of this tutorial.

---

## Key Concepts

### 1. `malloc`: asking the heap for memory

`malloc` (memory allocate) means: *"Heap, please give me a block of N bytes, and tell me where it is."*

```c
int *p = malloc(sizeof(int));   // "give me enough bytes for one int"
```

Let's read that slowly, because every piece matters:

- `sizeof(int)` → the number of bytes one `int` needs (4 on your machine). You almost never hardcode `4`; you ask `sizeof` so your code is correct on any machine. (Representation over magic numbers.)
- `malloc(...)` → goes to the heap, finds a free block of that size, and **returns its address**.
- `int *p = ...` → you store that address in a pointer. **This is why pointers exist.** The heap block has no name — `p` is your only handle to it. Lose `p` and you've lost the block forever.

Here is the picture, and notice it's the stack/heap diagram from Tutorial 1, now in action:

```
   STACK (high, ~0x7ffe...)            HEAP (low, ~0x55...)
  ┌──────────────────────┐           ┌──────────────────────┐
  │  p  │  0x5500abcd ────┼──────────▶│ 0x5500abcd │  ????   │  ← 4 bytes malloc gave you
  └──────────────────────┘           └──────────────────────┘
   p lives on the stack                the block lives on the heap
   p HOLDS a heap address              p is the only way to reach it
```

This is the answer to last session's question, made real: **`p` sits on the stack (high address), but it points to a block on the heap (low address).** When you print both addresses, you'll *see* the two regions. That's your first exercise.

> **Confusion alert — what's actually *in* the block right after malloc?**
> Garbage. `malloc` gives you raw, uninitialized bytes — whatever was left there from before. It does **not** zero them out. Reading the block before you write to it gives you unpredictable junk. (There's a sibling, `calloc`, that zeroes the memory for you — we'll meet it later.)

### 2. `malloc` can fail — and C won't warn you

`malloc` returns the address of your block, **or `NULL`** if the system has no memory to give. `NULL` is a special pointer value meaning "points to nothing" (it's address 0).

```c
int *p = malloc(sizeof(int));
if (p == NULL) {
    // the allocation failed — using p now would crash
}
```

In TypeScript, running out of memory throws an exception that bubbles up loudly. In C, a failed `malloc` just hands you `NULL` and walks away. If you don't check, the *next* time you write `*p = 5` you're writing to address 0 — an instant crash (segfault). Checking for `NULL` is a habit worth building from day one.

### 3. `free`: giving the memory back

The heap does not clean up after itself. When you're done with a block, you must return it:

```c
free(p);    // "Heap, I'm done with this block. Take it back."
```

`free` hands the block back to the heap so it can be reused. Three things to burn into memory:

- You `free` **once** per `malloc`. Every `malloc` has exactly one matching `free`. Think of them as a pair, like opening and closing a bracket.
- You pass `free` the **same address** `malloc` gave you — the start of the block.
- After `free(p)`, the block is gone, but **`p` still holds the old address.** `p` is now a *dangling pointer* — it points at memory you no longer own. (More on this in a moment.)

### 4. Ownership — the idea that ties it all together

Here's the mental model that makes manual memory manageable. For every heap block, ask one question:

> **Who owns this block — i.e., whose job is it to `free` it?**

That's it. "Ownership" just means "the responsibility to free." In a GC language the runtime owns everything. In C, *you* assign ownership, usually with a simple rule: **whoever allocates it is responsible for freeing it** (or for clearly handing that responsibility to someone else).

When you `malloc` in one function and the block travels to another, you have to *decide and document* who frees it. That decision — made consciously — is what separates C programmers who write solid code from those who write leaky, crashy code. We'll practice it constantly as we build the dynamic array, the linked list, and beyond.

### 5. The two classic bugs (and your new best friend, the sanitizer)

Manual memory creates exactly two famous failure modes. They are mirror images of each other:

**Bug 1 — Memory leak: you forget to `free`.**
```c
void leak(void) {
    int *p = malloc(sizeof(int));   // got a block...
    *p = 42;
}                                   // ...p disappears (it was a stack local),
                                    // but the heap block is still allocated.
                                    // No one has its address anymore. It's lost forever.
```
The block is still "in use" as far as the heap knows, but you've thrown away the only handle to it. It can never be freed and never reused. Do this in a loop and your program slowly eats all the memory. A GC would have caught this; C will not.

**Bug 2 — Dangling pointer / use-after-free: you `free`, then keep using it.**
```c
int *p = malloc(sizeof(int));
*p = 42;
free(p);            // block returned to the heap
*p = 99;            // CRIME: writing to memory you no longer own
```
After `free`, the block may be handed to some other part of your program. Writing through `p` now corrupts whatever moved in. These bugs are nasty because the program often *looks* fine, then crashes mysteriously much later.

**Here's the good news:** you do not have to find these by squinting. Your **`sanitizers`** skill installs a watchdog into your program. Compile with **AddressSanitizer**:

```
gcc -Wall -Wextra -Wpedantic -g -fsanitize=address phase0_heap.c -o phase0_heap && ./phase0_heap
```

ASan will *interrupt your program the instant* you use-after-free, and *report leaks when it exits*, pointing at the exact line. It turns invisible, mysterious bugs into a clear error message. We'll deliberately write both bugs and watch ASan catch them — making the mistake *on purpose* is the fastest way to never fear it.

---

## Examples — from your world (TS) to C

### Example 1: The GC you never noticed

| TypeScript / C# | C |
| --- | --- |
| `const u = makeUser("Ana")` allocates on a heap | `User *u = malloc(sizeof(User))` allocates on the heap |
| GC frees `u` automatically when unreachable | **you** call `free(u)` when done |
| Forgetting to "free" is impossible | forgetting `free` = a **leak** |
| Using an object after it's gone is impossible | using after `free` = a **dangling pointer** crash |

**What this demonstrates:** the heap was always there in your career. The only thing C adds is the *responsibility* — and a clear rule (ownership) to manage it.

### Example 2: The malloc/free pair, read as a bracket

```c
int *p = malloc(sizeof(int));   // [  open: acquire ownership
if (p == NULL) return;          //    always check the result
*p = 42;                        //    use it
free(p);                        // ]  close: release ownership
```

**What this demonstrates:** well-managed heap code has a visual rhythm — every `malloc` opens a bracket that a `free` must close. When you train your eye to see unmatched brackets, you start spotting leaks by reading.

---

## Try It Yourself

Your hands, your code. Put these in `study/exercises/phase0_heap.c`. Compile with the full flag set, and add `-fsanitize=address` where noted:

```
gcc -Wall -Wextra -Wpedantic -g phase0_heap.c -o phase0_heap && ./phase0_heap
```

**Exercise A — Prove the heap exists (the payoff from last session).**
`malloc` space for one `int`. Print **two** addresses with `%p`: the address *of your pointer variable* (`&p` — where the pointer lives) and the address *the pointer holds* (`p` — where the heap block lives). Compare them to the stack addresses from your last program. Is the heap address high (`0x7ffe…`) or low (`0x55…`)? Tell me what you see — this is the moment stack-vs-heap becomes real. (Then write a value through the pointer, print it, and `free` it.)

**Exercise B — Make a leak on purpose, then let ASan bust you.**
Write a function that `malloc`s a block and returns *without* freeing it. Call it. Compile **with `-fsanitize=address`** and run. Read ASan's report carefully — it will tell you there's a leak and point at the allocation. Then *fix* the leak and watch the report go away. (Goal: learn to read the sanitizer's voice — it will be your guide for the rest of Phase 0.)

**Exercise C — Stretch: the function that *should* use the heap.**
Rewrite the broken function from the top of this tutorial so it actually works: a function `int *make_int(int value)` that returns a pointer to an `int` (holding `value`) that *survives* after the function returns. Think hard about: where must that `int` live for it to survive — stack or heap? And now — *who owns it, and who must free it?* Use it in `main`, then free it. This is your first real ownership decision.

Bring me your code and especially your ASan output — if it crashes or leaks, that's not failure, that's the lesson working.

---

## Summary

- **The heap is for values that must outlive the function that created them**, or whose size you only know at runtime. The stack can't do that.
- **`malloc(n)`** returns the address of an `n`-byte block (or `NULL` on failure — always check). The bytes are **uninitialized garbage** until you write them.
- **`free(p)`** returns the block to the heap. **One `free` per `malloc`** — like matching brackets. After `free`, `p` is a dangling pointer; don't use it.
- **Ownership = "whose job is it to `free` this?"** The question a garbage collector silently answered for you. Decide it consciously for every heap block. Default rule: whoever allocates, frees.
- **Two classic bugs:** *leak* (forgot to free → memory lost forever) and *use-after-free / dangling pointer* (freed, then used → corruption/crash).
- **AddressSanitizer (`-fsanitize=address`) is your watchdog** — it catches both bugs and names the line. Make the bugs on purpose to learn its voice.
- **Next:** with the heap and ownership in hand, you're ready to build your first real data structure — a **dynamic array** that grows on demand, the thing TypeScript's `array` and C#'s `List<T>` secretly are.

---

## Q&A

### 27-05-2026 — First pass review of `lesson-2.c` (revealed several recurring/new misconceptions)

**Wins:** Switched to `<stdio.h>` + added `<stdlib.h>`. Organized into `study/exercises/phase-0/`. Always paired `malloc` with `free` (responsible default). Ex3's ownership structure (allocate in helper, return pointer, caller frees) is correct. Ex3's printed address (`0x55b593bdc2a0`) IS a heap address — the stack-vs-heap payoff actually happened, learner just didn't notice.

**Misconceptions surfaced:**
1. **Compiled and ran without reading warnings.** Under `-Wall -Wextra -Wpedantic`, the compiler emits 4 `%p` format-type warnings (one per printf with `%p`). Learner missed them. Habit to install: treat warnings as errors; the compiler is the first safety net.
2. **Pointer vs pointee, again.** Ex1 line 8 prints `*p` (the value at the heap block) when it meant `p` (the heap address). Same lesson-1 distinction in new clothing. Three-way table reinforced: `&p` (addr of pointer var, stack), `p` (heap addr), `*p` (int value at heap addr).
3. **The `0xbebebebe` tell.** With ASan, the "Heap address" line printed `0xbebebebe`. Taught that AddressSanitizer poisons fresh `malloc`'d bytes with `0xbe` so reads of uninitialized memory are visible. The exercise required writing a value into the block before reading it — that step was skipped.
4. **Ex2 was not actually a leak.** `free(p)` was called → ASan reported no leaks. Exercise B's intent (deliberately leave out `free`, see ASan's leak report) was missed.
5. **Comment in ex2 confused runtime and compile-time errors.** Reinforced: leaks are runtime; the compiler can't decide them; that's why ASan is a *runtime* watchdog installed via `-fsanitize=address`.
6. **Ex3 only proves an address survives, not a value.** Signature was supposed to be `int *make_int(int value)`; learner used `make_heap_int()` with no value parameter, never wrote into the block, printed the address (`%p`) rather than the value (`%d`).
7. **No NULL checks** after any `malloc`. Tutorial introduced the habit; not yet applied.

**Action items handed back:** recompile with `-Wall -Wextra -Wpedantic -fsanitize=address` and read every warning; in ex1 write `*p = 42` then print with `%d`; in ex2 comment out `free` and paste the ASan leak report; in ex3 accept and store a value, print value not address; add NULL checks.

## Quiz History

[Quiz sessions will be recorded here after the learner is quizzed on this topic]

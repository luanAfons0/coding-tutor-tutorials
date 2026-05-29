---
concepts: dynamic_array,realloc,amortized_complexity,struct,data_structures
order: 3
source_repo: study
description: First real data structure of Phase 0 — build a dynamic array (the thing TypeScript's `array` and C# `List<T>` secretly are) from scratch in C. Learn the data+size+capacity trick, the realloc API and its "may move" gotcha, the capacity-doubling strategy, and why amortized O(1) is real even though some pushes are expensive. Combines everything from Tutorials 1 and 2 into a single working tool.
understanding_score: null
last_quizzed: null
prerequisites: [~/coding-tutor-tutorials/courses/data-structures-and-algorithms/2026-05-27-pointers-and-the-memory-model.md, ~/coding-tutor-tutorials/courses/data-structures-and-algorithms/2026-05-27-the-heap-malloc-free-and-ownership.md]
created: 27-05-2026
last_updated: 27-05-2026
---

# Build a Dynamic Array From Scratch

You've used arrays your whole career and you've never had to think about how big they are. In TypeScript you write `arr.push(42)` and the array just... gets bigger. In C# you write `list.Add(42)` to a `List<T>` and the same thing happens. The language quietly handles "is there room? if not, make more room." You never had to ask.

In this tutorial you build that. **You are about to write — from raw `malloc`, `realloc`, and `free` — the thing that has been silently growing under your code your whole life.** When you finish, you'll *know* what `push` really does, and the question "what does it cost?" will have a satisfyingly concrete answer.

This is the first build of your toolbox — the dynamic array becomes the foundation for the next pieces of Phase 0 and beyond.

---

## The Problem

C gives you fixed-size arrays. You declare:

```c
int arr[10];
```

and you get exactly 10 ints. Forever. There is no `arr.push(...)`. If you decide you need an 11th element, the language has nothing to offer you. You're stuck.

But your real-world code rarely knows the size in advance. *"Read all the lines from this file." "Collect every event the user clicks." "Store the words in this sentence."* You can't write `int events[???]` — you don't know `???` until the program runs.

In TypeScript and C# this was a non-problem — you just `push`. But under the hood, *someone* was solving it for you. That someone allocated a heap block, kept track of how full it was, and quietly moved everything to a bigger block when needed. **You're about to be that someone.**

---

## Key Concepts

### 1. The trick: store the array AND its bookkeeping in one struct

A C array doesn't carry its size with it. So we'll wrap it in a struct that does:

```
┌──────────────────────────────────────────┐
│                  Vec                      │
│   data      → pointer to heap block       │
│   size      = how many items USED         │
│   capacity  = how many items the BLOCK    │
│               currently fits before we    │
│               need a bigger one           │
└──────────────────────────────────────────┘
```

In code (this is *the only* design snippet I'll give you — you write the implementation):

```c
typedef struct {
    int *data;       // heap-allocated buffer of ints
    size_t size;     // number of items currently in use
    size_t capacity; // number the buffer can hold before resize
} Vec;
```

> **Why two numbers, not one?** Because `size` and `capacity` are *different facts*. `size` is what your user sees ("how many things have I pushed?"). `capacity` is the secret you keep ("how much room do I have before I must grow?"). The trick of a fast dynamic array is: **capacity ≥ size, with room to spare, so most pushes are O(1)**. Without that gap, every `push` would have to allocate — slow.

> **Why `size_t`?** It's the standard C type for "a size or count of bytes/items." It's unsigned and big enough to hold any in-memory size on your platform. Use it whenever you mean "a count." Lives in `<stddef.h>` (and is dragged in by `<stdlib.h>`).

### 2. The new function: `realloc`

`malloc` gives you a new block. `free` gives a block back. `realloc` does something in between: **"resize this block."**

```c
new_ptr = realloc(old_ptr, new_size_in_bytes);
```

Three things it might do, and you don't get to choose which:

1. **Grow in place.** If there happens to be free heap space right after your block, `realloc` extends it. Same address comes back. Fast.
2. **Move to a new block.** If there isn't room to grow in place, `realloc` allocates a brand-new block, **copies your old bytes into it**, frees the old block, and returns the *new* address. Slower (because of the copy), but still automatic.
3. **Fail and return `NULL`.** Same way `malloc` can fail.

> 🚨 **The single most important `realloc` rule — internalize this:**
> Because `realloc` *may move the block*, **the old pointer might no longer be valid after the call.** Always capture the return value, check for `NULL`, and only then overwrite your stored pointer.

Wrong:
```c
v->data = realloc(v->data, new_cap * sizeof(int));   // if realloc returns NULL,
                                                     // you've just overwritten v->data
                                                     // with NULL and LEAKED the old block.
```

Right:
```c
int *tmp = realloc(v->data, new_cap * sizeof(int));
if (tmp == NULL) {
    /* leave v->data alone; original block still valid; report failure */
    return;
}
v->data = tmp;
```

This is one of those "looks fine, blows up rarely" C bugs — exactly the kind a senior C dev spots in a code review. Now you do too.

> **Quiet bonus:** `realloc(NULL, size)` behaves exactly like `malloc(size)`. Some people exploit this so the *first* push and *every later* push can share the same code path. You don't have to — but it's worth knowing the C standard library is occasionally elegant.

### 3. The growth strategy — why we **double** the capacity

When the array is full and you must grow, how much extra room should you take? Two tempting wrong answers and one right one:

- **"Add 1."** Every push past the initial capacity copies all N existing items into a new block. Pushing N items takes 1 + 2 + 3 + … + N work ≈ **N² / 2**. For 1,000,000 items that's 500 billion operations of copying. Horrifically slow.
- **"Add 100 (or any fixed chunk)."** Better, but still O(N²) — every fixed chunk you fill triggers another full copy.
- **"Double the capacity"** (or multiply by some factor like 1.5). Now resizes happen *exponentially less often*. The total cost of pushing N items is **O(N)**. The average cost per push is **O(1)**. This is what every grown-up dynamic array does (Java's `ArrayList`, C++'s `std::vector`, Go slices, Python lists). TypeScript's V8 engine does it. C#'s `List<T>` does it.

This is your first formal data-structures result. The name is **amortized O(1)** — *amortized* meaning "averaged out over a long sequence of pushes." Some individual pushes are expensive (the ones that trigger a copy), but the expensive ones are rare *enough* that the total work stays linear.

The intuition in one sentence: **every time you copy N items, you've "earned" the right to do N free pushes before the next copy.** Doubling guarantees that bookkeeping balances.

### 4. The minimum API you'll build

A real dynamic array needs more (delete, insert, iterate), but the core five are enough to prove you understand it:

| Function | What it does | Notes |
| --- | --- | --- |
| `vec_init(Vec *v, size_t initial_cap)` | set up an empty Vec, malloc the buffer | initialize size = 0 |
| `vec_push(Vec *v, int value)` | append `value`; grow if needed | the heart of the whole thing |
| `vec_get(const Vec *v, size_t i)` | return the i-th value | check bounds; what should you do if `i >= size`? |
| `vec_free(Vec *v)` | release the heap buffer | set `data = NULL`, `size = capacity = 0` after |
| (optional) `vec_print(const Vec *v)` | print contents for debugging | very handy during testing |

Notice how almost every signature takes a `Vec *` — a pointer to the struct. **Why a pointer and not a copy?** Two reasons:
1. You want the function to *modify* the original (`push` needs to update size/capacity).
2. Passing a copy would copy the *struct fields* (data pointer, size, capacity), not the heap block — but you'd have two structs pointing at the same heap, which gets confusing fast.

Use `v->size` (arrow) to mean "the `size` field of the struct that `v` points to." `v->size` is just shorthand for `(*v).size`.

### 5. Ownership recap — who frees what

For your `Vec`:
- The `Vec` struct itself can live on the stack (`Vec v;` inside `main`) — automatic, no `free` needed.
- The `v.data` buffer is on the **heap** — owned by the `Vec`. Whoever creates the `Vec` must call `vec_free(&v)` before letting it go out of scope. One `vec_free` per `vec_init`. ASan will catch you if you forget.

That's the contract. Document it. Live by it.

---

## Examples — from your world (TS) to C

### Example 1: What `push` was hiding from you

Picture TypeScript:
```ts
const a = [];          // some empty backing buffer somewhere
a.push(1);             // size=1, capacity=4 (engines pick a starting cap)
a.push(2); a.push(3); a.push(4);  // size=4, capacity=4
a.push(5);             // capacity full → engine quietly allocates a new
                       //   buffer of size 8, copies [1,2,3,4] into it,
                       //   appends 5, frees the old one. You see nothing.
```

In your C version, **you will write that "quietly" step explicitly.** That's the whole point of building it.

### Example 2: The bytes-vs-items confusion `realloc` will hand you

`realloc` thinks in **bytes**. Your `Vec` thinks in **items** (ints). Every time you call `realloc`, multiply:

```c
realloc(v->data, new_capacity * sizeof(int))
```

Forget the `sizeof(int)` and you'll allocate a *quarter* of what you intended (since `sizeof(int) == 4`). Then your push of the 5th item walks off the end of the buffer and corrupts memory — and ASan will catch it with a "heap-buffer-overflow" report. (Tip: when ASan reports `heap-buffer-overflow`, the very first thing to check is whether you forgot to multiply by `sizeof(...)` somewhere.)

---

## Try It Yourself

Time to build. Suggested location: `study/exercises/phase-0/lesson-3.c` (single file is fine; or split into `vec.h` + `vec.c` + `main.c` if you want to practice that — your call).

**Compile flags you should already have memorized:**
```
gcc -Wall -Wextra -Wpedantic -g -fsanitize=address lesson-3.c -o lesson-3 && ./lesson-3
```

### Step 1 — Declare the struct
Define `Vec` exactly as shown in the struct snippet above (or improve it). Add `#include <stdlib.h>` (malloc/realloc/free) and `<stdio.h>`. You may want `<assert.h>` too.

### Step 2 — Implement `vec_init` and `vec_free`
- `vec_init` should `malloc` a buffer of `initial_cap * sizeof(int)`, set size = 0 and capacity = initial_cap, and store the pointer in `v->data`. NULL-check the malloc the same way you did in lesson-2.
- `vec_free` should `free(v->data)`, then null out the fields (so a stale `Vec` is detectably empty).

Test it: in `main`, init a Vec with capacity 4, free it, run under ASan. **There should be zero leaks and zero errors.** That's your first green light.

### Step 3 — Implement `vec_push` (the heart)
The logic in plain English:
1. If `size == capacity`, the buffer is full → grow:
   - Choose a new capacity (start with **double** — `capacity * 2`). What should happen if the initial capacity is 0? (Hint: pick a minimum like 1 or 4.)
   - Call `realloc` correctly (see the "single most important `realloc` rule" above — *don't overwrite the old pointer until you check the result*).
   - Update `v->capacity` to the new value.
2. Write `value` into `v->data[v->size]` (the next empty slot).
3. Increment `v->size`.

Test it: push 10 ints. Print all of them with a small loop. Watch capacity grow.

**Suggested debug print after each push:** `printf("pushed %d → size=%zu, capacity=%zu\n", value, v->size, v->capacity);` — the `%zu` is the right format for `size_t`. You'll *see* the doubling moments.

### Step 4 — Implement `vec_get`
Decide your bounds policy: if someone calls `vec_get(v, 999)` on a vec of size 3, what should happen? Two reasonable choices:
- **Crash cleanly** with `assert(i < v->size);` — good for catching bugs early.
- **Return a sentinel** like `-1` (only works if you'd never store `-1` legitimately).

Pick one. Document it in a comment. Defending your decision in your own words is part of becoming senior.

### Step 5 — Stress test: prove the doubling
Push 1000 items. Print only the capacity each time it *changes*. You should see something like: `4, 8, 16, 32, 64, 128, 256, 512, 1024` — about **log₂(1000) ≈ 10** resize events for 1000 pushes. That's amortized O(1) made visible. If your numbers don't look like this, something's off — bring it to me.

### Step 6 — Stretch: make ASan angry on purpose
Pick *one*:
- **Off-by-one:** intentionally write to `v->data[v->capacity]` (one past the end). Run under ASan. Read the `heap-buffer-overflow` report it produces.
- **Forget to free:** comment out your `vec_free` call. Read the leak report.
- **Use after free:** call `vec_free`, then try `vec_get`. Read the `heap-use-after-free` report.

These are the three classic dynamic-array bugs. Seeing each one *under controlled conditions* makes you immune to fearing them later.

Bring me your code and especially your stress-test output and any ASan reports. Don't worry if it takes 2–3 sessions; this is the biggest build of Phase 0. Take it in pieces.

---

## Summary

- **A dynamic array = (heap buffer, size, capacity).** The size–capacity gap is what makes it fast.
- **`realloc(p, new_bytes)`** resizes a heap block. It may move the block, so **always capture the return value and check for NULL before overwriting `p`**. Forgetting this is a classic leak/use-after-free.
- **Doubling the capacity on each grow** keeps the average cost per push **O(1) amortized**. This is the trick every grown-up dynamic array uses.
- The five-function API (`init`, `push`, `get`, `free`, `print`) is enough to prove you understand the structure. The dynamic array is now a tool in your toolbox.
- **You owe ASan some bugs on purpose** (off-by-one, leak, use-after-free) to train your eye on its three classic reports.
- **Next:** with a working dynamic array, you have one of two data structures Redis is built on. The Phase 0 finale is the **hash table** — and after that, you're ready for Phase 1.

---

## Q&A

### 28-05-2026 — Building the Vec: the major moments

**The pass-by-value struct trap (recurring lesson 1).** First `vec_push`/`vec_debug`/`vec_free`
took `struct Vec vec` by value. Pushes ran, the heap buffer got written, but `size` stayed `0`
in the caller and `vec_debug` always printed "empty." Exact same lesson as `tryChange(int x)` vs
`increment(int *p)` from lesson 1, now applied to a struct. Fixed by changing every mutating
signature to `struct Vec *vec` and using `vec->size`, etc. Senior rule reinforced: *if a
function needs to modify something the caller will see, it takes a `T *`.*

**Other bugs surfaced during the build:**
- `init_vec` allocated `init_size` ints but set `capacity = init_size * 2` → heap-buffer-overflow
  waiting to happen. Capacity must equal what `data` can actually hold.
- `vec_push`'s `else` branch wrote `data[size + 1]` (off-by-one). Compounded by an unnecessary
  `if (size == 0)` special case. Simplified to a single `data[size] = value; size++;` formula
  that works for any size.
- `vec_free` initially by value: functional but left the caller's `data` dangling. Refactored
  to `vec_free(struct Vec *)` that nulls the fields. The `vec->data = NULL;` line specifically
  makes a double-free safe (because `free(NULL)` is a defined no-op).

**Step 5 — amortized O(1) made visible.** Stress-pushing 1000 ints into a Vec that started
at capacity 1 produced exactly **10 resize events** at loop indices 1, 2, 4, 8, …, 512.
`log₂(1024) = 10`. The doubling strategy demonstrated concretely.

**Step 6 — assert vs ASan layering.** First attempts at heap-buffer-overflow and
use-after-free fired the in-function `assert` in `vec_get` instead of ASan's reports — the
defensive guard stops the bad access before ASan can see it. To produce ASan's specific
reports, bypass the guard with direct buffer access (`v.data[v.capacity] = …`) or retain a
raw pointer before `vec_free` and read through it afterwards. Bigger principle: defensive
code (asserts) and runtime sanitizers (ASan) catch overlapping things; the first to fire
wins. Test B (the leak) worked first time → real `Direct leak of 4 byte(s)` report. Test C
hit `SEGV on 0x000…` because `vec_free` now nulls `data` — i.e. learner's good defensive
practice turned "use-after-free" into "clean NULL crash" (preferable in production).

## Quiz History

[Quiz sessions will be recorded here after the learner is quizzed on this topic]

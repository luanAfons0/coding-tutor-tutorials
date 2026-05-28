---
concepts: linked_list,nodes,pointer_chasing,recursive_structures,list_traversal,pointer_to_pointer
source_repo: study
description: Second build of Phase 0 — a singly linked list. Each node is its own heap allocation, threaded together with a `next` pointer. Introduces the pointer-to-pointer idiom (`Node**`), the "save-next-before-free" walking pattern, and the deep trade-off vs the dynamic array (fast prepend vs fast indexed access). Cements ownership thinking: many small allocations, one careful walk to free them all.
understanding_score: null
last_quizzed: null
prerequisites: [~/coding-tutor-tutorials/2026-05-27-pointers-and-the-memory-model.md, ~/coding-tutor-tutorials/2026-05-27-the-heap-malloc-free-and-ownership.md, ~/coding-tutor-tutorials/2026-05-27-build-a-dynamic-array-from-scratch.md]
created: 28-05-2026
last_updated: 28-05-2026
---

# Build a Singly Linked List From Scratch

You just built a dynamic array. It is *fantastic* at one thing — *"give me element N"* in O(1) — and pretty good at many others. So why would you ever want a different structure?

Two reasons your `Vec` cannot help you:

1. **Insert at the front (prepend).** To prepend an item to your Vec, you'd shift every existing element one slot to the right. For a million-element Vec, that's a million copies *per prepend*. O(n). Painful.
2. **Insert in the middle** (cheaply, when you already have a pointer to the spot). Same problem — shift everything after that point. O(n).

In return for fast indexed access, your array paid you in *contiguous memory* — which is exactly why insertion in the middle is expensive. The **linked list** is the structure that makes the opposite trade. **Insertion at the front (or middle, if you have a pointer) is O(1). Random access is O(n).** Different tool, different job.

By the end of this tutorial, your toolbox has its second piece — and you'll understand *why* you'd reach for each one.

---

## The Problem

Imagine you're collecting events as they arrive — say, the last 1000 user actions, newest first. Every new event goes to the *front*.

With your `Vec`, every push-to-front costs O(n) — you shift everything. With a linked list, you allocate one tiny new "node" and make it point to the current front. That's it. **The work to add one item is the work for one item, no matter how big the list is.**

Or imagine an undo stack. Or a queue of pending tasks. Or a chain of cells in a hash table that collide on the same bucket (foreshadowing Phase 0's finale!). Linked lists are the natural shape whenever items are added/removed at the ends or by-pointer in the middle, and you don't need random access.

---

## Key Concepts

### 1. The node — a struct that contains a pointer to *its own type*

Here is the only design snippet you need. Stare at it for a moment, because it's a quietly profound idea:

```c
typedef struct Node {
    int data;            // the value this node carries
    struct Node *next;   // a pointer to the next Node — or NULL if this is the last
} Node;
```

A struct **containing a pointer to itself** is how every linked structure in computing is built — lists, trees, graphs, file systems. Read it as: *"a Node is a piece of data, plus directions to the next Node."*

You can't put a whole `Node` inside another `Node` (infinite recursion in the memory layout). But a *pointer* to a Node is fixed-size (8 bytes on your machine), so it fits fine. The pointer is the trick.

> **Why `typedef struct Node { ... } Node;`?** Without `typedef`, you'd have to write `struct Node` everywhere. The `typedef` lets you just say `Node`. You have to write `struct Node *next` *inside* the struct (not `Node *next`) because the typedef isn't visible yet at that line. A small C wart.

### 2. The list is just a head pointer ending in NULL

Visualize this:

```
head ──▶ ┌────┬───┐    ┌────┬───┐    ┌────┬─────┐
         │ 10 │ ●─┼──▶ │ 20 │ ●─┼──▶ │ 30 │NULL │
         └────┴───┘    └────┴───┘    └────┴─────┘
            node 1        node 2       node 3
```

The whole "list" is **one variable**: `Node *head`. From there you walk through `.next` pointers until you hit `NULL`. The `NULL` at the tail is what marks the end — *the* universal "stop walking" signal.

Three of these "lists" deserve special mention:

- A list with **zero elements** is just `head = NULL`. That's a valid empty list. *Don't special-case it everywhere; design your functions to handle `NULL` head naturally.*
- A list with **one element** is one node whose `.next` is `NULL`.
- A node whose `.next` points back at the head (or any earlier node) is a **cycle** — a bug we won't write, but worth knowing exists.

### 3. The mental model: a list is a *recursive* data structure

Here's a beautiful way to think about it. A linked list is either:

- **Empty** (`head == NULL`), or
- **A node** carrying a value AND a (smaller) **linked list** as its `next`.

Yes — a list is "a value plus another list." This recursive definition is real, and it means you can write recursive functions over lists in a totally natural way (free, print, find, length…). You don't have to — but knowing that recursion is *natural* here will pay off later when you build trees.

### 4. The big trade-off vs your dynamic array

| Operation | `Vec` (dynamic array) | Linked list |
| --- | --- | --- |
| Access by index | **O(1)** | O(n) — walk from head |
| Push back (append) | amortized O(1) | O(n) (or O(1) with a kept tail pointer) |
| **Push front (prepend)** | O(n) — shift all | **O(1)** |
| **Insert in the middle (given a node pointer)** | O(n) — shift all after | **O(1)** |
| Memory layout | One contiguous block | N tiny blocks scattered across the heap |
| Memory overhead per element | small | **large** — every element carries an 8-byte `next` pointer |
| CPU cache friendliness | excellent | poor (pointer chasing jumps around) |

Take a minute with that table. It's a *real* trade-off — neither structure is "better." In practice, dynamic arrays win for most workloads (the cache friendliness alone often beats the linked list's theoretical advantages). But for prepend-heavy work, or when an item *must* keep its identity when others are inserted/removed, the linked list earns its place.

### 5. Pointer-to-pointer (`Node **`) — one level deeper than last tutorial

In Tutorial 3 you passed `struct Vec *vec` so a function could *modify the struct's fields*. Same logic, one level up:

The list "is" the `head` pointer. If a function needs to *change which node `head` points to* (e.g., `prepend` changes it to point at the new node; `free` should leave it pointing to NULL), then the function must take a **pointer to `head`** — i.e., `Node **head`. Why? Because `head` is *itself a pointer*, and to mutate a pointer, you pass *its* address.

> **The rule that ties Tutorials 1, 3, and 4 together:**
> *To modify an `X` from a function, pass it a `X *`.*
> So to modify an `int`, pass `int *`. To modify a `struct Vec`, pass `struct Vec *`. **To modify a `Node *` (your head pointer), pass `Node **`.** Same idea, one star deeper.

Inside the function:
- `*head` is the head pointer itself (`Node *`).
- `(*head)->data` reads the head node's data. (The parens matter because of operator precedence.)
- To update the head: `*head = some_new_node;`

If this feels disorienting at first, draw it. Two boxes: the *caller's* `head` (lives wherever the caller put it — usually on the stack), and inside it an address pointing to the first node. The function gets the address *of that box*, so it can replace what's in the box.

### 6. The walk-and-free trap

Freeing a list looks easy, until you write the naive version:

```c
Node *curr = *head;
while (curr != NULL) {
    free(curr);
    curr = curr->next;   // 🚨 curr was JUST freed — reading curr->next is heap-use-after-free
}
```

Look at the bug. You `free(curr)` — the block is gone. Then you read `curr->next` — that memory was returned to the heap a line ago, and may already be repurposed. ASan will fire `heap-use-after-free` instantly.

The fix is a one-line classic C pattern. Save what you need *before* destroying:

```c
Node *curr = *head;
while (curr != NULL) {
    Node *next = curr->next;   // ✓ remember next FIRST
    free(curr);                // now safely destroy
    curr = next;
}
*head = NULL;                  // mark the list as cleanly empty
```

Same principle as your `vec_free(v->data = NULL)` line — **leave a structure in a known, safe state after you destroy what it owned.**

### 7. Ownership recap — many small things

For your `Vec`, *one* heap allocation owned the entire buffer. Easy: one `malloc`, one `free`.

For a linked list, **every node is its own heap allocation**. A list of N items = N separate malloc'd blocks. The list's `free` function walks the chain and `free`s every single one. ASan will not forgive you if you forget one in the middle.

This is also why linked lists feel "small and many" while dynamic arrays feel "one and big" — and why dynamic arrays are usually faster despite being theoretically slower for some operations. The CPU's cache lines (typically 64 bytes) make contiguous data dramatically faster to scan than scattered pointer-chased data. *Worth knowing as you build.*

---

## Examples — from your world (TS) to C

### Example 1: A linked list shape you can already write in TypeScript

```ts
type Node = { data: number; next: Node | null };

const head: Node = {
  data: 10,
  next: { data: 20, next: { data: 30, next: null } }
};
```

This works in TS today. The C version is the *same shape* — just with manual memory. Every `{...}` in the TS example will be a `malloc(sizeof(Node))` in C. Every `null` will be `NULL`. Same chain, same walk.

The conceptual difference is *not* in the data structure — it's in *who frees the chain when you're done*. TS: nobody, the GC handles it. C: you walk and free every node.

### Example 2: The "I lost the head" disaster

The head pointer is the only handle to the entire list. Drop it without freeing and **every node leaks**:

```c
Node *head = make_node(10);
head->next = make_node(20);
head->next->next = make_node(30);

head = NULL;   // 💥 lost the chain. ASan: 3 leaks.
```

**Treat the head pointer like the keys to a house.** Lose it before you've cleaned up inside, and you can never get back in.

---

## Try It Yourself

Suggested file: `study/exercises/phase-0/lesson-4.c`. Same canonical compile command:

```
gcc -Wall -Wextra -Wpedantic -g -fsanitize=address lesson-4.c -o lesson-4 && ./lesson-4
```

### Step 1 — Define the node
Write the `Node` struct exactly as shown. Include `<stdio.h>` and `<stdlib.h>`. (You may want `<assert.h>` for bounds-y things later.)

### Step 2 — `make_node`
A small helper: `Node *make_node(int value)` that `malloc`s a `Node`, sets `data = value`, sets `next = NULL`, and returns the pointer. Don't forget the NULL-check (use the `exit(EXIT_FAILURE)` pattern from `lesson-2`).

### Step 3 — `list_print`
`void list_print(const Node *head)` — walks the chain printing values. Use `const` because you don't modify the list. The walk pattern:

```
for (const Node *curr = head; curr != NULL; curr = curr->next) {
    // print curr->data
}
```

This is the **universal "walk a linked list" loop.** Memorize it.

Test it: build a 3-node list by hand (`make_node` three times, wire `.next` manually) and print it. Expect output like `[10] → [20] → [30] → NULL`.

### Step 4 — `list_prepend` (the headliner)
`void list_prepend(Node **head, int value)`. Two cases to handle correctly (the function should handle both without an explicit `if`):
1. The list is empty (`*head == NULL`) — new node becomes the head.
2. The list isn't empty — new node points at the current head, then becomes the new head.

**Hint:** if you write the function so that *the new node's `next` is set to the current `*head` before* `*head` is updated to point to the new node, then both cases collapse into the same two lines. Try to find that.

Test it: start with `Node *head = NULL;`, prepend 1, 2, 3, then print. You should see `[3] → [2] → [1] → NULL` (prepending reverses your insertion order — by design).

### Step 5 — `list_free` (with the save-next pattern)
`void list_free(Node **head)`. Walk the chain. At each step, **save `curr->next` *before* freeing `curr`.** When done, set `*head = NULL`.

Test it: build a list, free it, run under ASan. **Zero leaks, zero use-after-free.** That's the only acceptable outcome.

### Step 6 — Stress test (linked-list-style)
Prepend 1000 items in a loop. Print only the first 5 and last 5 to keep output reasonable. Then free. ASan should remain silent — and you've just allocated and freed 1000 little heap blocks correctly.

### Step 7 — Stretch: `list_append` and `list_find`
- `void list_append(Node **head, int value)` — add to the *end*. Walking the whole list to find the last node is O(n). This is *why* linked lists are slow for append, *unless* you also keep a tail pointer. (For learning, skip the tail. Feel the O(n).)
- `Node *list_find(const Node *head, int value)` — return a pointer to the first node whose data equals `value`, or `NULL`. Useful for the Phase 0 finale (hash table buckets).

### Step 8 — Make ASan angry on purpose (one of these)
Pick one and write it inside an `#if 0 ... #endif` block (or just comment switching) so you can toggle it:
- **Naive free:** the buggy "walk and free without save-next" pattern from Concept 6. ASan should fire `heap-use-after-free`. Read the report.
- **Leak:** prepend 3 items, then drop `head = NULL` without `list_free`. ASan reports **three** leaks. Read each stack trace.

Bring me your code (especially Steps 4 and 5), your stress-test output, and any ASan reports.

---

## Summary

- A linked list is a chain of heap-allocated **nodes**, each carrying a value and a pointer to the next, terminated by `NULL`.
- The list "is" the **head pointer**. Functions that *modify* the list take a `Node **head` — same rule as before, one star deeper.
- **Trade-off with the dynamic array:** linked lists win at prepend / by-pointer middle-insertion (O(1)); arrays win at random access (O(1)) and at being cache-friendly. Pick the one your workload needs.
- **The walk-and-free trap**: always save `curr->next` *before* freeing `curr`. A C classic.
- A list is a **recursive structure** — "a value, plus another list." That viewpoint will return when you build trees.
- **Next:** the Phase 0 finale, the **hash table** — which (delightfully) uses linked lists under the hood to handle collisions, and is the seed of the Redis clone in Phase 2.

---

## Q&A

[Questions and answers will be added here as the learner asks them during the tutorial]

## Quiz History

[Quiz sessions will be recorded here after the learner is quizzed on this topic]

---
concepts: big_o,complexity,asymptotic_analysis,amortized_complexity
source_repo: study
description: A short, just-enough primer on Big O notation — the vocabulary used throughout DSA to talk about how an algorithm's cost grows with input size. Covers the intuition (shape of growth, not stopwatch time), the common growth classes (O(1), O(log n), O(n), O(n log n), O(n²)), why constants get dropped, and what "amortized" really means — all anchored in the dynamic array and linked list the learner has already built.
understanding_score: null
last_quizzed: null
prerequisites: [~/coding-tutor-tutorials/2026-05-27-build-a-dynamic-array-from-scratch.md]
created: 28-05-2026
last_updated: 28-05-2026
---

# Big O Notation — A Beginner's Primer

Every time you write a piece of code that handles a *collection* of things — an array, a list, a database table — there's a hidden question hanging over it: **"if my input gets 10× bigger, what happens to my runtime?"** Doubles? Stays the same? Explodes a thousand-fold?

Big O is the language we use to answer that question. It is **not** "how fast is this algorithm in seconds" — that depends on your CPU, your compiler, what you had for breakfast. Big O is "**how does the work scale as the input grows?**" — a property of the algorithm, not the machine.

By the end of this short page you'll know enough to read every other tutorial in this trail with comprehension, and to talk about performance the way senior engineers do.

---

## The Problem

You write two functions. Both work. On a 10-item input, both finish in a millisecond. **Which one will you regret on a million-item input?**

You can't tell by running them on 10 items. You need a way to predict *behavior at scale*. Big O is that predictor. It looks past the constants, the noise, the breakfast — and tells you the **shape** of the function "time as a function of input size N."

That shape — flat, linear, exponential, etc. — is what makes the difference between a system that handles a million users and one that buckles at a thousand.

---

## Key Concepts

### 1. The core idea: shape of growth, not stopwatch time

When we write **O(f(N))**, we mean: *"For big enough N, the cost grows roughly like the function f(N)."*

We don't care about exact numbers. We care about the **shape**:
- Flat line? → O(1)
- Straight line (45°)? → O(n)
- Gentle curve up? → O(log n)
- Aggressive curve up? → O(n²)
- Wall going to the sky? → O(2ⁿ)

That's the whole intuition. Big O is the *family* of curves your algorithm belongs to.

### 2. The growth classes you actually need to know

There are five you'll meet again and again. From *best* (cheapest at scale) to *worst*:

| Big O | Name | Intuition | "If I 10× the input, the cost…" |
| --- | --- | --- | --- |
| **O(1)** | constant | One step, no matter how big | …doesn't change |
| **O(log n)** | logarithmic | Each step halves the problem | …grows by ~1 step |
| **O(n)** | linear | One step per item | …becomes 10× |
| **O(n log n)** | log-linear | Like linear, but each item costs log(n) | …becomes ~11× |
| **O(n²)** | quadratic | One step *per pair* of items | …becomes **100×** |

That's it. You can get a long way in your career knowing just these five. (Beyond them lies O(2ⁿ) "exponential" — usually a sign you've taken a wrong turn.)

### 3. Drop the constants and the lower-order terms

This is the trick that makes Big O *useful*: it ignores the noise.

If your algorithm does `2 * N + 100` operations, that's **O(n)** — not "O(2n + 100)." Why? Because the goal is to capture *shape*. For very big N, `2 * N + 100` and `N` and `1000 * N` all draw the *same straight line* on a graph (just at different slopes). The constants change *how fast* you walk; Big O captures *that you walk*.

Same idea for terms of different shape: `N² + 10 * N` is **O(n²)** — the quadratic term dominates for big N, the linear term is dust beside it.

> 🚨 **Don't confuse this with "constants don't matter in real code."** They matter a lot in practice — a 100× constant factor between two O(n) algorithms is a 100× real-world speed difference. Big O simply ignores constants to highlight the *family*. Two O(n) algorithms can still be wildly different in practice; Big O just tells you neither will *explode* as N grows.

### 4. Each of those classes, in *your own examples*

Every one of these has appeared in something you've already built. Look back at your work with fresh eyes:

#### 🟢 O(1) — constant
- **`vec_get(v, 5)` in your Vec.** It computes one address (`data + 5 * sizeof(int)`) and reads it. **One step. Always.** Whether your Vec has 10 items or 10 million, `vec_get` is the same handful of CPU instructions. That's O(1).
- **`*p = 42`** — write through any pointer. One step.

#### 🟡 O(log n) — logarithmic
- You haven't built one of these yet — but you will. **Binary search** of a sorted array is the classic: every comparison halves the remaining range, so to find one item among N you need only `log₂(N)` comparisons. For a million items: ~20 comparisons. For a billion: ~30.
- **Preview:** the B-trees inside your future SQLite clone are O(log n). That's *why* databases are fast.

#### 🟢 O(n) — linear
- **`vec_debug` printing all items in your Vec** — one print per item, N items, O(n). If you doubled the size of the Vec, the loop runs twice as long.
- **Walking a linked list to find a value** — same shape. One step per node.

#### 🟡 O(n log n) — log-linear
- You haven't built one yet either — but this is the cost of **efficient sorting** (merge sort, heap sort). It's the cost of *touching each item once* (n) and doing *log n work per item* (the divide-and-conquer structure of these algorithms).

#### 🔴 O(n²) — quadratic
- **The "+1 capacity each grow" version of `vec_push`** that the Tutorial 3 doc warned you not to write. Pushing N items would have cost `1 + 2 + 3 + … + N ≈ N² / 2` operations. For a million items: ~500 *billion* operations of copying. You skipped this trap by doubling the capacity. ✅
- **Prepending to your Vec** in a loop (which you *don't* do — that's the linked list's job). Each prepend shifts every existing element, so prepending N items costs O(n²) total.
- The classic "compare every pair of items" pattern (e.g., naïve sorting). Two nested loops over the same input.

### 5. Worst case vs amortized (this is what "amortized O(1)" really meant)

When we say something is O(N), we usually mean **worst case** — the most work *any single call* could ever do.

But sometimes a single call is occasionally expensive, while *the average over many calls* is much cheaper. That's the world of **amortized complexity** — and you've already produced the textbook example of it.

Look at your stress-test output from Tutorial 3:
```
Vector capacity 2    in loop 1
Vector capacity 4    in loop 2
Vector capacity 8    in loop 4
...
Vector capacity 1024 in loop 512
```

Most calls to `vec_push` were O(1) (just write into the next slot). But **10 of those 1000 pushes were expensive** — each one copied the entire existing buffer into a bigger block (work proportional to the current size).

So *worst case* a single `vec_push` is O(n) — the resize push could copy a billion items. But *over a long sequence of pushes*, the total work for N pushes is O(N), so the **average per push** is O(N) / N = **O(1)**. That's what *amortized* O(1) means: "averaged across a long sequence, each operation costs a constant amount."

> 🧠 **Mental model for amortized:** every time a `vec_push` does work proportional to N (the resize-and-copy), it has *also bought you* roughly N free pushes before the next resize. The expensive ones "pay forward" the cheap ones. That's why doubling is the magic ratio — it balances the books.

The doubling strategy is the most famous amortized result in all of programming. You've now generated the data that proves it. 🏆

### 6. The trade-off table from Tutorial 4, re-read

Now this:

| Operation | `Vec` | Linked list |
| --- | --- | --- |
| Access by index | **O(1)** | O(n) |
| Push front (prepend) | O(n) | **O(1)** |

…stops being abstract. "Vec gets bigger by 10×, indexed access stays one step" vs "list gets bigger by 10×, walking to element N becomes 10× slower." That's the language of trade-offs you'll use for the rest of your career.

### 7. Best vs average vs worst (a brief footnote)

Three Big Os actually exist for most algorithms:
- **Worst case** — the most work *any* input could cause. Usually what we mean by "O(...)" without qualifier.
- **Average case** — averaged over typical inputs. Requires assumptions about input distribution.
- **Best case** — the luckiest path. Often not very useful (a quicksort's best case is O(n), but you can't rely on luck).

For now: assume "Big O" means "worst case" unless told otherwise (or "amortized" — covered above).

---

## Examples — from your world (TS) to C

### Example 1: `.find` vs `[]` in TypeScript

```ts
arr[5];                    // O(1) — direct index access
arr.find(x => x === 42);   // O(n) — walks the array
```

Same array. Different work. The `[]` operator hops to the right memory address; `.find` walks until it sees the value (or hits the end). When you write TS code, you've been making O(1) vs O(n) choices your whole career — you just didn't have the vocabulary.

### Example 2: Two ways to count duplicates

```ts
// Way 1: for every item, check every other item
for (const a of items) {
  for (const b of items) {
    if (a === b) { /* ... */ }
  }
}
// O(n²)

// Way 2: use a Set (which has O(1) lookup)
const seen = new Set<number>();
for (const a of items) {
  if (seen.has(a)) { /* ... */ }
  seen.add(a);
}
// O(n)
```

For 100 items: 10,000 vs 100 operations. For 1,000,000 items: a trillion vs a million. **This is the kind of difference Big O exists to make visible.**

(And under the hood: a `Set` is a hash table — Phase 0's final tutorial.)

---

## Try It Yourself (mental exercise — no code)

These are quick judgments to test your intuition. Try answering before reading the next line.

1. You walk a linked list of N nodes to find a value. **Big O?**
   — *Worst case you walk every node. O(n).*

2. You insert a value at the **front** of a linked list. **Big O?**
   — *One allocation, two pointer updates. O(1) — doesn't depend on N.*

3. You insert a value at the **front** of a `Vec` of N ints. **Big O?**
   — *Shift every existing element. O(n).*

4. You call `vec_push` 1,000,000 times in a row on an initially-empty Vec. **Total work?**
   — *Amortized O(N) total → ~1,000,000 operations, despite ~20 resize events.*

5. You find an int in a sorted array of size N by repeatedly halving the search range (binary search). **Big O?**
   — *Each step halves the range. log₂(N) steps. O(log n).*

If those clicked, you're equipped. If any felt fuzzy, ask me — that's the kind of moment I'd rather re-explain than leave shaky.

---

## Summary

- **Big O is the language of scale**, not the language of stopwatch time. It captures the *shape* of "cost as a function of input size N."
- **Five classes cover most of your career:** O(1), O(log n), O(n), O(n log n), O(n²). Drop constants and lower-order terms.
- **Pick the right shape for the workload.** Your Vec and your linked list trade between O(1) access and O(1) prepend — that's the whole reason both exist.
- **Amortized O(1)** means "averaged across a long sequence." Your Vec's doubling strategy is the canonical example — you've already produced the data that proves it.
- Big O is *predictive*: tells you what'll happen as N grows. Constants still matter in practice — but at scale, *shape wins*.
- **Next:** back to building the linked list (Tutorial 4) with this vocabulary in hand.

---

## Q&A

[Questions and answers will be added here as the learner asks them during the tutorial]

## Quiz History

[Quiz sessions will be recorded here after the learner is quizzed on this topic]

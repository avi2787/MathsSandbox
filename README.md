# MathsSandbox

A small Pygame playground for math/CS curiosities. Left side: pick a mode and drag sliders. Right side: watch it update in real time.

⚠️ this was my first high-def Pygame project, so some modes can feel quite laggy/slow when you crank settings or just on running. Need to learn how to make my code more efficient in that way too.

## What you can do (and the idea behind it)
- Mandelbrot: click to zoom in, right-click to zoom out; tweak iteration count. It’s just iterating `z = z^2 + c` per pixel and counting when it “escapes”.
- Twin primes: plot primes up to N and show lines for twin pairs. Uses the sieve to find primes, then picks pairs (p, p+2).
- Collatz: chart the steps from any starting number. Follows the simple rule: even → n/2, odd → 3n+1 until it hits 1.
- Sieve: run the sieve of Eratosthenes step by step with a reset. Marks multiples of each prime to leave only primes.
- Birthday paradox: compare the formula vs a quick Monte Carlo for shared birthdays. Formula multiplies the “no collision” chances; sim drops random birthdays to see collisions.
- Hash timing: time SHA-256 vs Argon2id and show how many leading bits match. It hashes random data, times both, and compares leading equal bits of the outputs.

## How it works (quickly)
- Uses `pygame` for drawing and simple buttons/sliders.
- Each mode registers its own controls; the left panel handles layout.
- `numpy` helps with the Mandelbrot grid; `argon2-cffi` provides Argon2.

## Run it
```bash
python sanbox.py
```
Install deps if needed: `pygame`, `numpy`, `argon2-cffi`.

## Controls
- Mode buttons on the left; sliders sit underneath them.
- Canvas: Mandelbrot supports left-click zoom in, right-click zoom out; others are mostly view-only.
- Press `Esc` to quit.

## Tips
- Raise the limits/iterations to see how visuals and runtimes change.
- Use the sieve mode to show how primes get crossed out one pass at a time.
- Hash mode is just a quick timing/bit-match demo, not a full security test.

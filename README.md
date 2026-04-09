# MathsSandbox

A small Pygame playground for math/CS curiosities. Left side: pick a mode and drag sliders. Right side: watch it update in real time.

## What you can do
- Mandelbrot: click to zoom in, right-click to zoom out; tweak iteration count.
- Twin primes: plot primes up to N and show lines for twin pairs.
- Collatz: chart the steps from any starting number.
- Sieve: run the sieve of Eratosthenes step by step with a reset.
- Birthday paradox: compare the formula vs a quick Monte Carlo for shared birthdays.
- Hash timing: time SHA-256 vs Argon2id and show how many leading bits match.

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

# MathsSandbox

A Pygame-based sandbox for exploring maths and CS ideas interactively.

Left side: pick a mode and tweak parameters.  
Right side: see everything update in real time.

⚠️ This was my first higher-resolution Pygame project, so some modes can get slow when you push the settings. Optimising performance is something I still need to improve.
---

## What you can do

### Mandelbrot Set
- Left-click to zoom in, right-click to zoom out  
- Adjustable iteration count  

**How it works**
- Each pixel maps to a complex number c  
- Iterates z = z² + c starting from z = 0  
- Stops when |z| > 2 or max iterations reached  
- Uses the iteration count to colour each pixel  

**Notes**
- Increasing iterations reveals more detail near the boundary  
- Performance depends heavily on resolution × iteration count  
---

### Twin Primes
- Plots primes up to a limit  
- Draws lines between twin pairs (p, p+2)  

**How it works**
- Uses the sieve of Eratosthenes to generate primes  
- Filters pairs with difference = 2  
---

### Collatz Conjecture
- Visualises the sequence for a chosen starting number  

**How it works**
- Applies:
  - even → n / 2  
  - odd → 3n + 1  
- Runs until it reaches 1  
- Tracks number of steps  

---

### Sieve (step-by-step)
- Shows how primes are generated visually  

**How it works**
- Iteratively marks multiples of each prime  
- Leaves only primes unmarked  

---

### Birthday Paradox
- Compares formula vs simulation  

**How it works**
- Formula: multiplies “no shared birthday” probabilities  
- Monte Carlo: generates random birthdays and checks collisions  

**Notes**
- Shows how simulation and theory line up (or don’t)  
---

### Hash Timing (SHA-256 vs Argon2id)
- Compares hashing performance and output behaviour  

**How it works**
- Generates random input  
- Computes hashes using:
  - SHA-256  
  - Argon2id (argon2-cffi)  
- Measures time taken  
- Compares number of matching leading bits  

**Notes**
- Demonstrates performance vs security trade-offs  
- Not meant to be a full cryptographic analysis  
---

## How it’s structured
- Built using `pygame` for rendering and UI  
- Each mode handles its own logic and parameters  
- A shared UI system manages:
  - mode selection  
  - sliders  
  - layout  

- `numpy` is used for Mandelbrot grid calculations  
- `argon2-cffi` is used for Argon2 hashing  
---

## Running it
```bash
python sandbox.py

## Controls
- Mode buttons on the left; sliders sit underneath them.
- Canvas: Mandelbrot supports left-click zoom in, right-click zoom out; others are mostly view-only.
- Press `Esc` to quit.

## Tips
- Raise the limits/iterations to see how visuals and runtimes change.
- Use the sieve mode to show how primes get crossed out one pass at a time.
- Hash mode is just a quick timing/bit-match demo, not a full security test.

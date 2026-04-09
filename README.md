# MathsSandbox

A compact, student-friendly Pygame sandbox that bundles several math/CS visualizations and interactive demos in a single window. The left panel lets you switch modes and tweak parameters; the right canvas visualizes the results live.

## What's inside
- Mandelbrot explorer: zoom/pan via clicks; adjust iteration depth.
- Twin primes: plot primes up to N and connect twin pairs.
- Collatz trajectories: graph the sequence for any starting integer.
- Sieve of Eratosthenes: step-by-step marking with reset and limit control.
- Birthday paradox: formula vs Monte Carlo bars for collision probability.
- Hash timing: compare iterated SHA-256 and Argon2id and show leading-bit matches.

## How it works
- Built with `pygame` for rendering and simple UI elements (buttons/sliders).
- Modes share a control panel (left) and a canvas (right); each mode registers its own sliders/buttons and rendering logic.
- Numerical heavy lifting uses Python stdlib + `numpy` for the Mandelbrot grid and `argon2-cffi` for Argon2 hashing.

## Running
```bash
python sanbox.py
```
(Ensure `pygame`, `numpy`, and `argon2-cffi` are installed in your environment.)

## Controls
- Mode buttons: left panel top.
- Sliders: adjust per-mode parameters (positioned below the mode list).
- Canvas interactions: Mandelbrot supports left-click zoom in, right-click zoom out; other modes are view-only unless noted.
- Keyboard: `Esc` to quit.

## Notes for students
- Try varying limits/iterations to see how complexity scales in time/visual density.
- The sieve mode is step-based—great for classroom demos of prime filtering.
- Hash mode shows timing differences and a quick “leading equal bits” metric to spark discussion about collision intuition.

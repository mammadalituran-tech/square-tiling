# Documentation

## Problem Description:

The square tiling problem asks if it is possible to fill a K x K grid using given set of tiles, so that all the neighboring edges have the same color. Each tile is described by four colors: top, right, bottom, and left. A tiling is proper when every pair of adjacent tiles has the same color on the touching edges.

A valid input format look like this: 

2

3

3

1 1 1 1

1 2 1 2

2 1 2 1


Here, first line is the grid size, second is number of colors, third is list of tile types and the remaining lines are each one tile.

The task is to decide whether a proper tiling exists. If it does, an example of a proper tiling is the following in a 2 x 2 grid:

0 0

0 0


## Encoding:

For every grid position (i, j) and every tile type t, I create a variable X(i, j, t) which shows that tile t is placed in cell (i, j). Since the grid has K x K cells and m tile types, we have K^2 * m variables in total. I used the following constraints:

1. Each cell contains at least one tile.

For each position (i,j), at least one of the tile types must be selected:
X(i, j, 0)∨ X(i, j, 1)∨ … ∨ X(i,j, m−1)

2. A cell cannot have two different tiles.

For every pair of different tile types t1 < t2, we have 
¬X(i, j, t1​) ∨ ¬X(i, j, t2​)

3. Horizontal matching constraint.
If two cells (i, j) and (i, j + 1) are next to each other, the right edge of the tile placed at (i, j) must match the left edge of the tile at (i, j + 1). For every pair of tile types t1, t2 such that right(t1) ≠ left(t2), we add ¬X(i, j, t1​) ∨ ¬X(i, j+1, t2​).

4. Vertical matching constraint.
For every pair (i, j) and (i + 1, j), the bottom of the top tile must match the top of the bottom tile. For every pair of tile types t1, t2 with bottom(t1) ≠ top(t2), we have ¬X(i, j, t1​) ∨ ¬X(i+1, j, t2​).



## User documentation:

Basic usage: 

```
python3 square_tiling.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]

```


Command-line options:
1. -h, --help : Show a help message and exit.
2. -i INPUT, --input INPUT : The instance file. Default: "input.in".
3. -o OUTPUT, --output OUTPUT : Output file for the DIMACS format (i.e. the CNF formula).
4. -s SOLVER, --solver SOLVER : The SAT solver to be used.
5. -v {0,1}, --verb {0,1} :  Verbosity of the SAT solver used.

## Example instances:

1. input-2by2.in: A simple 2×2 instance that is solvable immediately.
2. input-2by2-unsat.in: An unsatisfiable 2×2 instance.
3. input-3by3.in: A basic 3×3 instance that is solvable.
4. input-3by3-unsat.in: An unsatisfiable 3×3 instance.
5. input-hard.in: A solvable instance that takes approximately 10s to solve on my machine.


## Experiments:

Experiments were run on my machine using Ubuntu inside WSL2(Windows 11). All satisfiable and unsatisfiable small instances (2 x 2 and 3 x 3) were solved immediately. Even instances with grid size 8 or 10 were solved in less than a second. For the larger instance input-hard.in with grid size 35 the solving time on my machine was around 10 seconds. This instance was satisfiable mainly because for some tiles same colors were repeated on opposite sides or on all the sides. So in the resulting tiling the solver used mainly those tiles. 











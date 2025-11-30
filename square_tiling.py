import subprocess
from argparse import ArgumentParser

# Global variables describing the current instance.
GRID_SIZE = None       # k
NR_COLORS = None       # number of colours
TILES = []             # list of tiles
NR_TILES = 0           # len(TILES)


def load_instance(input_file_name):
    # read the input instance
    global GRID_SIZE, NR_COLORS, TILES, NR_TILES

    with open(input_file_name, "r") as f:
        first = next(f, None)
        if first is None:
            raise ValueError("Input file is empty.")

        GRID_SIZE = int(first.strip())
        second = next(f, None)
        if second is None:
            raise ValueError("Missing number of colours on the second line.")
        NR_COLORS = int(second.strip())

        third = next(f, None)
        if third is None:
            raise ValueError("Missing number of tiles on the third line.")
        m = int(third.strip())

        tiles = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 4:
                raise ValueError("Each tile must have exactly 4 colours.")
            a, b, c, d = (int(x) for x in parts)
            tiles.append((a, b, c, d))

        if len(tiles) != m:
            raise ValueError(f"Expected {m} tiles, got {len(tiles)}.")

    TILES = tiles
    NR_TILES = len(TILES)

    return TILES


def cell_tile_to_var(i, j, t):
    # variable X(i,j,t)
    return (i * GRID_SIZE + j) * NR_TILES + t + 1


def encode(instance):
    # create CNF clauses
    cnf = []

    # number of variables
    nr_vars = GRID_SIZE * GRID_SIZE * NR_TILES

    # each cell has at least one tile
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            clause = [cell_tile_to_var(i, j, t) for t in range(NR_TILES)]
            clause.append(0)
            cnf.append(clause)

    # each cell has at most one tile
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            for t1 in range(NR_TILES):
                for t2 in range(t1 + 1, NR_TILES):
                    cnf.append([
                        -cell_tile_to_var(i, j, t1),
                        -cell_tile_to_var(i, j, t2),
                        0
                    ])

    # precompute colours of sides for each tile.
    tops = [t[0] for t in TILES]
    rights = [t[1] for t in TILES]
    bottoms = [t[2] for t in TILES]
    lefts = [t[3] for t in TILES]

    # horizontal matching
    bad_horizontal_pairs = []
    for t_left in range(NR_TILES):
        for t_right in range(NR_TILES):
            if rights[t_left] != lefts[t_right]:
                bad_horizontal_pairs.append((t_left, t_right))

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE - 1):  # (i,j) and (i,j+1)
            for t_left, t_right in bad_horizontal_pairs:
                cnf.append([
                    -cell_tile_to_var(i, j, t_left),
                    -cell_tile_to_var(i, j + 1, t_right),
                    0
                ])

    # vertical matching
    bad_vertical_pairs = []
    for t_up in range(NR_TILES):
        for t_down in range(NR_TILES):
            if bottoms[t_up] != tops[t_down]:
                bad_vertical_pairs.append((t_up, t_down))

    for i in range(GRID_SIZE - 1):
        for j in range(GRID_SIZE):
            for t_up, t_down in bad_vertical_pairs:
                cnf.append([
                    -cell_tile_to_var(i, j, t_up),
                    -cell_tile_to_var(i + 1, j, t_down),
                    0
                ])

    return cnf, nr_vars


def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into output_name in DIMACS format
    with open(output_name, "w") as file:
        file.write(f"p cnf {nr_vars} {len(cnf)}\n")
        for clause in cnf:
            file.write(" ".join(str(lit) for lit in clause) + "\n")

    # run the SAT solver
    return subprocess.run(
        ['./' + solver_name, '-model', f'-verb={verbosity}', output_name],
        stdout=subprocess.PIPE
    )


def print_result(result):
    # print raw solver output
    for line in result.stdout.decode('utf-8').splitlines():
        print(line)

    # UNSAT
    if result.returncode == 20:
        print()
        print("Instance is UNSAT: there is no proper tiling.")
        return

   # read model
    model = []
    for line in result.stdout.decode('utf-8').splitlines():
        if line.startswith("v"):
            parts = line.split()
            parts = [p for p in parts if p != "v"]
            model.extend(int(v) for v in parts)

    if 0 in model:
        model.remove(0)

    if not model:
        print("SAT solver did not return a model.")
        return

    print()
    print("############################################################")
    print("##############[ Human readable square tiling ]##############")
    print("############################################################")
    print()

    # read which tile is placed in each cell
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            tile_here = -1
            for t in range(NR_TILES):
                var_id = cell_tile_to_var(i, j, t)
                if var_id - 1 < len(model) and model[var_id - 1] > 0:
                    tile_here = t
                    break
            row.append(str(tile_here))
        print(" ".join(row))


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help="The instance file."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help="Where to write the CNF formula in DIMACS format."
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help="The SAT sovle to be used."
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        help="Verbosity of the SAT solver used."
    )

    args = parser.parse_args()

    # read instance from input file and set global variables
    instance = load_instance(args.input)

    # translate the instance into CNF
    cnf, nr_vars = encode(instance)

    # call the SAT solver
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

    # decode and print the result
    print_result(result)

from typing import Any, List, Dict, Union
from PIL import Image, ImageDraw
import random
import time
import math

# Wall bitmasks
N, E, S, W = 1, 2, 4, 8

BORDER = "\033[0m"
PATH = "\033[33m"
PATTERN = "\033[30m"
RESET = "\033[0m"
BORDER_RGB = (255, 255, 255)
WALL_RGB = (0, 0, 0)
EMPTY = " "
WALL = "█"
PATH_BLOCK = "██"


class MazeGenerator():
    """
    A maze generator using Depth-First Search (DFS) and Prim's algorithms.

    The maze is represented as a 2D grid where each cell contains a bitmask
    indicating which walls are present. Wall bitmasks: N=1, E=2, S=4, W=8.
    For example, a cell with value 12 (S+W = 4+8) has South and West walls.

    Arguments:
        width (int): Width of the maze (number of cells horizontally)
        height (int): Height of the maze (number of cells vertically)
        entry (tuple[int, int]): Entry coordinates (x, y)
        exit (tuple[int, int]): Exit coordinates (x, y)
        output_filename (str): File path to save the generated maze
        perfect (bool): If True, generates a perfect maze (no loops).
                       If False, adds random extra paths.
        seed (Any): Random seed for reproducible maze generation

    Attributes:
        maze (list[list[int]]): 2D grid of cells with wall bitmasks
        width (int): Maze width
        height (int): Maze height
        entry (tuple): Entry point coordinates
        exit (tuple): Exit point coordinates
        perfect (bool): Whether the maze is perfect (no loops)
        seed (Any): Random seed used
        pattern (list[list[int]]): Special pattern cells (e.g., "42" shape)
        visited (set): Set of visited cells during generation
        p (list[tuple]): Path coordinates during pathfinding
        order (list[list[int]]): Order in which cells were visited

    Usage Example:
        >>> from mazegen.mazegen import (MazeGenerator,
                                ft_generate_maze_DFS,
                                ft_print_maze_animation)

        >>> maze = MazeGenerator(
        ...     width=10,
        ...     height=10,
        ...     entry=(0, 0),
        ...     exit=(9, 9),
        ...     output_filename="maze.txt",
        ...     perfect=True,
        ...     seed=42
        ... )
        >>> maze.ft_generate_maze_DFS()
        >>> maze.ft_generate_output_file()
        >>> maze.ft_print_maze_animation("", True)
        >>> maze.ft_maze_options()
    """

    def __init__(self,
                 width: int,
                 height: int,
                 entry: tuple[int],
                 exit: tuple[int],
                 output_filename: str,
                 perfect: bool,
                 seed: Any
                 ) -> None:
        """
        Initialize the MazeGenerator with specified parameters.

        Args:
            width: Number of cells horizontally
            height: Number of cells vertically
            entry: Starting point as (x, y) tuple
            exit: Ending point as (x, y) tuple
            output_filename: Path to save the maze file
            perfect: True for perfect maze (one path), False for multiple paths
            seed: Random seed for reproducibility
        """

        # Set a seed to control the randomization
        random.seed(seed)

        # Set the maze grid
        self.maze: list[list[int]] = [[]]

        # Store configuration parameters
        self.width: int = width
        self.height: int = height
        self.entry: tuple = entry
        self.exit: tuple = exit
        self.perfect: bool = perfect
        self.seed: Any = seed

        # File to write the maze structure
        self.output_filename: str = output_filename

        # Build the "42" pattern (special blocked cells)
        self.pattern: List[List[int]] = self.ft_build_pattern_42()

        # Track visited cells and path during generation/solving
        # self.visited: Any = []
        self.path: list[str] = []
        self.order: List[List[int]] = []

    def ft_build_pattern_42(self) -> list[list[int]]:
        """
        Build a pattern that forms the number "42" in the center of the maze.

        These cells will be treated as solid blocks during maze generation,
        creating a visual "42" shape within the maze.

        Returns:
            list[list[int]]: List of [row, col] coordinates
                forming "42" pattern

        Note:
            The pattern is centered based on maze
                dimensions (height/2, width/2).
            Requires minimum dimensions to properly display the pattern.
        """
        self.path = []
        pattern = []

        # Relative coordinates that form "42" shape
        adding: List[List[int]] = [
            [0, 0], [1, 0], [2, 0],
            [2, 1], [2, 2], [3, 2],
            [4, 2], [0, 4], [0, 5],
            [0, 6], [1, 6], [2, 6],
            [2, 5], [2, 4], [3, 4],
            [4, 4], [4, 5], [4, 6]
            ]

        h_m = int(self.height / 2)
        w_m = int(self.width / 2)

        h_m -= 2
        w_m -= 3

        for add in adding:
            x, y = add
            pattern.append([h_m + x, w_m + y])
        self.pattern = pattern[:]
        return (pattern)

    def ft_build_pattern_13(self) -> None:
        """
        Build a pattern that forms the number "13" in the center of the maze.

        These cells will be treated as solid blocks during maze generation,
        creating a visual "13" shape within the maze.

        Returns:
            list[list[int]]: List of [row, col] coordinates
                forming "13" pattern

        Note:
            The pattern is centered based on maze
                dimensions (height/2, width/2).
            Requires minimum dimensions to properly display the pattern.
        """
        self.path = []
        pattern = []
        adding = [
            [1, 0], [0, 0], [0, 1], [0, 2],
            [1, 2], [2, 2], [3, 2], [4, 1],
            [4, 2], [4, 3], [0, 5], [0, 6],
            [0, 7], [1, 7], [2, 7], [2, 6],
            [2, 5], [3, 7], [4, 7], [4, 6], [4, 5]
            ]
        h_m = int(self.height / 2)
        w_m = int(self.width / 2)

        h_m -= 2
        w_m -= 4

        for add in adding:
            x, y = add
            pattern.append([h_m + x, w_m + y])
        self.pattern = pattern

    def ft_generate_maze_DFS(self) -> None:
        """
        Generate a maze using Depth-First Search (DFS) algorithm.

        Algorithm:
            1. Start at (0, 0) with all walls intact (cell value = 15)
            2. collect unvisited neighbor
            3. Pick a random unvisited neighbor
            4. Remove the wall between current cell and chosen neighbor
            5. Move to the neighbor and repeat
            6. Backtrack when no unvisited neighbors exist
            7. If not perfect, add random extra paths to create loops

        The maze is stored in self.maze as a 2D grid where each cell
        contains a bitmask (0-15) representing which walls remain.

        Time Complexity: O(width * height)
        Space Complexity: O(width * height) for the stack
        """
        self.path = []
        self.maze = [
            [15 for _ in range(self.width)] for _ in range(self.height)]
        self.order = []
        stack: list[tuple] = [(0, 0)]
        visited: set[tuple] = set([(0, 0)])

        dirs = [
            (N, -1,  0, S),
            (E,  0,  1, W),
            (S,  1,  0, N),
            (W,  0, -1, E),
        ]

        while stack:
            x, y = stack[-1]
            unvisited_neighbors = []

            for wall, dx, dy, opp in dirs:
                nx, ny = x + dx, y + dy

                if (
                    (x == 0 and wall == N) or
                    (x == self.height - 1 and wall == S) or
                    (y == 0 and wall == W) or
                    (y == self.width - 1 and wall == E)
                ):
                    continue

                if (
                    0 <= nx < self.height and
                    0 <= ny < self.width and
                    (nx, ny) not in visited and
                    [x, y] not in self.pattern
                ):
                    unvisited_neighbors.append((wall, dx, dy, opp, nx, ny))

            if unvisited_neighbors:
                wall, dx, dy, opp, nx, ny = random.choice(unvisited_neighbors)

                if ([nx, ny] not in self.pattern):
                    self.order.append([x, y])
                    self.order.append([nx, ny])
                    self.maze[x][y] &= ~wall
                    self.maze[nx][ny] &= ~opp

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not (self.perfect):
            for x in range(self.height):
                for y in range(self.width):
                    # Only target dead-ends (cells with 3 walls)
                    if bin(self.maze[x][y]).count('1') == 3:
                        # 30% chance to break a dead-end
                        if random.random() < 0.3:
                            # Find all currently STANDING walls for this cell
                            standing_walls = []
                            for wall, dx, dy, opp in dirs:
                                nx, ny = x + dx, y + dy
                                # Check if the wall exists AND it not a border
                                if (
                                    self.maze[x][y] & wall and
                                    0 <= nx < self.height and
                                    0 <= ny < self.width and
                                    [x, y] not in self.pattern and
                                    [nx, ny] not in self.pattern
                                ):
                                    standing_walls.append((wall, nx, ny, opp))

                            if standing_walls:
                                (
                                    wall,
                                    nx,
                                    ny,
                                    opp
                                ) = random.choice(standing_walls)
                                self.order.append([x, y])
                                self.order.append([nx, ny])
                                self.maze[x][y] &= ~wall
                                self.maze[nx][ny] &= ~opp

        self.visited = visited

    def ft_generate_maze_prims(self) -> None:
        """
            Generate a maze using a randomized version of Prim's algorithm.

            The maze is initialized with all walls present, then passages are
            carved starting from (0, 0). A random frontier wall is selected at
            each step, and if the adjacent cell is unvisited and not part of
            `self.pattern`, the wall between them is removed. Maze is stored
            as a 2D grid of bit-masked integers representing walls (N,E,S,W).

            Updates:
                self.maze: The generated maze grid.
                self.order: Order in which cells were added.

            If `self.perfect` is False, additional walls may be removed from
            dead ends (with 30% probability) to create loops.

            Returns:
                None
        """
        self.path = []
        self.maze = [
            [15 for _ in range(self.width)] for _ in range(self.height)]
        self.order = []
        dirs = [
            (N, -1, 0, S),
            (E, 0, 1, W),
            (S, 1, 0, N),
            (W, 0, -1, E)
            ]

        start_x, start_y = 0, 0
        visited = {(start_x, start_y)}
        frontier = []

        def add_to_frontier(x: int, y: int) -> None:
            for wall, dx, dy, opp in dirs:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self.height and
                    0 <= ny < self.width and
                    (nx, ny) not in visited and
                    list((nx, ny)) not in self.pattern
                ):
                    frontier.append((x, y, nx, ny, wall, opp))

        add_to_frontier(start_x, start_y)

        while frontier:
            idx = random.randrange(len(frontier))
            x, y, nx, ny, wall, opp = frontier.pop(idx)

            if (nx, ny) not in visited:
                self.maze[x][y] &= ~wall
                self.maze[nx][ny] &= ~opp

                visited.add((nx, ny))
                self.order.append([x, y])
                self.order.append([nx, ny])

                add_to_frontier(nx, ny)

        if not self.perfect:
            # Helper to handle the non-perfect maze logic efficiently
            for r in range(self.height):
                for c in range(self.width):
                    # If it's a dead end (only 1 opening, so 3 walls remain)
                    if bin(self.maze[r][c]).count('1') == 3:
                        if random.random() < 0.3:
                            wall, dx, dy, opp = random.choice(dirs)
                            nr, nc = r + dx, c + dy
                            if (
                                0 <= nr < self.height and
                                0 <= nc < self.width and
                                list((nr, nc)) not in self.pattern and
                                list((r, c)) not in self.pattern
                            ):
                                self.order.append([r, c])
                                self.order.append([nr, nc])
                                self.maze[r][c] &= ~wall
                                self.maze[nr][nc] &= ~opp

    def ft_find_path(self) -> list[str]:
        """
            Find a path from `self.entry` to `self.exit`
                using Breadth-First Search (BFS).

            Starting at the entry cell, this method explores neighboring cells
            whose connecting walls are open (based on bit flags N, E, S, W).
            It returns the first path found to the exit, guaranteeing the
            shortest path in terms of number of moves.

            The path is returned as a list of direction strings
            (e.g., ["N", "E", "E", "S"]).

            Returns:
                list[str]: The shortest sequence of
                    directions from entry to exit,
                or an empty list if no path exists.
        """
        start_x, start_y = self.entry
        end_x, end_y = self.exit

        queue: list[tuple[int, int, list[str]]] = [(start_x, start_y, [])]
        visited: set[tuple[int, int]] = set()

        while queue:
            x, y, path = queue.pop(0)

            if (x, y) == (end_x, end_y):
                self.path = path
                return path

            if (x, y) in visited:
                continue

            visited.add((x, y))

            cell = self.maze[y][x]

            if cell & N == 0 and y > 0:
                queue.append((x, y - 1, path + ["N"]))

            if cell & E == 0 and x < self.width - 1:
                queue.append((x + 1, y, path + ["E"]))

            if cell & S == 0 and y < self.height - 1:
                queue.append((x, y + 1, path + ["S"]))

            if cell & W == 0 and x > 0:
                queue.append((x - 1, y, path + ["W"]))

        return []

    def ft_generate_output_file(self) -> None:
        """
            Generate an output file representing the maze in hexadecimal and
            its solution.

            The maze grid is converted into a hexadecimal like format
            (values 0 - 15 mapped to '0' - 'F'), where each cell represents
            its bit masked wall configuration. The formatted maze is written
            line by line to the specified output file.

            The file also includes:
                - The entry coordinates
                - The exit coordinates
                - The solution path (as a string of directions)

            Args:
                maze: MazeGenerator instance containing the maze grid,
                    entry/exit points, output filename, and path logic.

            Returns:
                None
        """
        base: List[str] = [
            '0', '1', '2',
            '3', '4', '5',
            '6', '7', '8',
            '9', 'A', 'B',
            'C', 'D', 'E', 'F']
        output: str = ""

        for row in self.maze:
            for col in row:
                output += base[col]

            output += '\n'

        try:
            with open(self.output_filename, "w") as file:
                path = "".join(self.ft_find_path())
                file.write(f"{output}\n{self.entry}\n{self.exit}\n{path}")
        except Exception:
            print("ERROR: outputing maze")
            exit(1)

    def ft_print_maze(
            self,
            maze: list[list[int]] = [],
            path: Union[str, List[str]] = []) -> None:
        """
            Render the maze in the terminal using ASCII/ANSI colors.

            The maze is expanded to a (2H+1 x 2W+1) grid to visually display
            walls and passages. Walls are drawn using block characters, while
            open cells are rendered as spaces.

            Special rendering:
                - `entry` and `exit` are highlighted.
                - `path` (string of "N", "E", "S", "W") is traced and colored.
                - `pattern_42 o r13` (list of coordinates) is highlighted
                    with priority.

            Passages between adjacent special cells are colored consistently.

            Args:
                maze: 2D grid of bit-masked wall values.
                entry: (y, x) starting coordinate.
                exit: (y, x) ending coordinate.
                path: Optional string representing a solution path.
                pattern_42 or 13: Optional list of special
                    coordinates to highlight.

            Returns:
                None
        """
        global WALL
        height: int = len(maze)
        width: int = len(maze[0])

        # Define wall character
        WALL = f"{BORDER}█{RESET}"

        # 1. Create a logical map of the special cells
        special_cells: Dict = {}

        # Add entry and exit to special cells
        special_cells[
            (self.entry[1], self.entry[0])
            ] = f"{PATTERN}{PATH_BLOCK}{RESET}"
        special_cells[(self.exit[1], self.exit[0])] = f"{PATTERN}██{RESET}"

        # Add the 42/13 Pattern to the special cells
        if self.pattern:
            for y, x in self.pattern:
                special_cells[(y, x)] = f"{PATTERN}██{RESET}"

        # Add path to the special cells
        if path:
            px, py = self.entry
            for move in path:
                if move == "N":
                    py -= 1
                elif move == "S":
                    py += 1
                elif move == "E":
                    px += 1
                elif move == "W":
                    px -= 1

                # Don't overwrite Entry/Exit or pattern if you don't want to
                if (py, px) not in special_cells:
                    special_cells[(py, px)] = f"{PATH}{PATH_BLOCK}{RESET}"

        # 2. Initialize the expanded render grid (2H+1 x 2W+1)
        render_h, render_w = 2 * height + 1, 2 * width + 1
        grid: List[List] = [[WALL for _ in range(render_w)]
                            for _ in range(render_h)]

        # 3. Fill the grid
        for y in range(height):
            for x in range(width):
                cell = maze[y][x]
                ry, rx = 2 * y + 1, 2 * x + 1

                # Determine center content
                if (y, x) in special_cells:
                    grid[ry][rx] = special_cells[(y, x)]
                elif cell == 15:
                    grid[ry][rx] = WALL
                else:
                    grid[ry][rx] = "  "

                # Draw Passages (Between Cells)
                dirs = [
                    (1, -1, 0),
                    (2, 0, 1),
                    (4, 1, 0),
                    (8, 0, -1)
                    ]
                for bit, dy, dx in dirs:
                    if not (cell & bit):
                        wy, wx = ry + dy, rx + dx
                        ny, nx = y + dy, x + dx

                        # If both current and neighbor are special
                        if (
                            (y, x) in special_cells and
                            (ny, nx) in special_cells
                        ):
                            grid[wy][wx] = special_cells[(y, x)]
                        else:
                            grid[wy][wx] = "  "

        # 4. Final Render
        for row in grid:
            line = ""
            for char in row:
                # doub the wall clarto stay square
                line += (char * 2) if char == WALL else char
            print(line)

    def ft_print_maze_animation(
            self,
            path: Union[str, List[str]] = "",
            animation: bool = True) -> None:
        """
            Animate maze generation or solution in the terminal.

            If `path` is provided, animates the solution step-by-step.
            Otherwise, animates the maze generation using `MAZE.order`.

            If `animation` is False, prints the full maze instantly.

            Args:
                MAZE: Maze object containing maze grid, entry, exit,
                    generation order, and pattern.
                path: Optional solution path ("N", "E", "S", "W").
                animation: Enable/disable generation animation.

            Returns:
                None
        """
        # Create an full maze
        empty_maze: List = [
            [15 for _ in range(self.width)] for _ in range(self.height)]

        if not (animation):
            self.ft_print_maze(self.maze)
        else:
            for cord in self.order:
                x, y = cord
                empty_maze[x][y] = self.maze[x][y]
                print("\33c", end="")
                self.ft_print_maze(empty_maze, "")
                time.sleep(0.008)

        if (path):
            empty_path = ""
            for p in path:
                empty_path += p
                print("\33c", end="")
                self.ft_print_maze(self.maze, empty_path)
                time.sleep(0.1)
            return

    def ft_let_user_find_path(self) -> None:
        empty_path = ""
        tries = 0
        for p in self.path:
            user_path = input("Choose a directin: ").upper()
            tries += 1
            while (user_path != p):
                user_path = input("Choose a directin: ").upper()
                tries += 1
                if (user_path in "NESW"):
                    print("Wrong direction choose again!")

            empty_path += p
            print("\33c", end="")
            self.ft_print_maze(self.maze, path=empty_path)
            time.sleep(0.1)

        print(f"Congrats you find the shortest path in {tries} steps! 🥳")

    def ft_change_maze_color(self) -> None:
        """
            Randomly change the global maze color scheme.

            Selects a new combination of ANSI color codes for:
                - BORDER (walls)
                - PATH (solution path)
                - PATTERN (special cells)

            Ensures the new colors differ from the current ones.

            Returns:
                tuple[str, str, str]: The new (BORDER, PATH, PATTERN) colors.
        """
        global BORDER, PATH, PATTERN, BORDER_RGB
        # Some of the colors combination
        colors = [
            ["\033[0m", "\033[33m", "\033[30m", (255, 255, 255)],
            ["\033[36m", "\033[35m", "\033[0m", (179, 117, 255)],
            ["\033[34m", "\033[33m", "\033[32m", (78, 154, 252)],
            ["\033[33m", "\033[34m", "\033[35m", (255, 196, 94)],
            ["\033[35m", "\033[33m", "\033[36m", (245, 120, 239)],
            ["\033[36m", "\033[0m", "\033[35m", (179, 117, 255)],
            ]

        # The choice return type acoording to mypy is Any
        new_colors: Any = random.choice(colors)
        # Looping until find new color
        while (new_colors == [BORDER, PATH, PATTERN, BORDER_RGB]):
            new_colors = random.choice(colors)
        BORDER, PATH, PATTERN, BORDER_RGB = new_colors

    def export_maze_png(
            self,
            cell_size: int = 30,
            wall_thickness: int = 4
            ) -> None:
        """
        Exporting the maze as a png image in the root directory.

        Arguments:
            - cell_size = the size of each cell as pixels.
            - wall_thickness = thickness of the wall to be represented in img.
        """
        rows: int = len(self.maze)
        cols: int = len(self.maze[0])
        filename: str = f"maze{random.randrange(1, 1000)}.png"
        img_w: int = cols * cell_size
        img_h: int = rows * cell_size

        img = Image.new("RGB", (img_w, img_h), (54, 53, 52))
        draw = ImageDraw.Draw(img)

        for y in range(rows):
            for x in range(cols):
                cell = self.maze[y][x]

                px = x * cell_size
                py = y * cell_size

                # North wall
                if cell & N:
                    draw.rectangle(
                        [px, py, px + cell_size, py + wall_thickness],
                        fill=BORDER_RGB
                    )

                # South wall
                if cell & S:
                    draw.rectangle(
                        [
                            px,
                            py + cell_size - wall_thickness,
                            px + cell_size,
                            py + cell_size
                        ],
                        fill=BORDER_RGB)

                # West wall
                if cell & W:
                    draw.rectangle(
                        [px, py, px + wall_thickness, py + cell_size],
                        fill=BORDER_RGB
                    )

                # East wall
                if cell & E:
                    draw.rectangle(
                        [
                            px + cell_size - wall_thickness,
                            py,
                            px + cell_size,
                            py + cell_size
                        ],
                        fill=BORDER_RGB
                    )

        img.save(filename)

    def ft_maze_options(self) -> int:
        """
            Display the interactive menu options and return the user's choice.

            Prints a numbered list of available actions (e.g., regenerate maze,
            change algorithm, toggle path visibility, change colors,
            switch modes, etc. Prompts the user to select an option and
            validates that the input is an integer within the valid range.

            Repeats until a valid choice is entered.

            Returns:
                int: The selected menu option number (1-based index).
        """
        options: list[str] = [
            "1. Re-generate a new maze(previous algo)",
            "2. Re-generate a new maze with DFS Algorithm",
            "3. Re-generate a new maze with Prims Algorithm",
            "4. Show/hide path from entry to exit",
            "5. Change Maze color",
            "6. Change MODE to 42",
            "7. Change MODE to 13",
            "8. Change path block",
            "9. Manual player mode (shortest path)",
            "10. Export maze as image (PNG)",
            "11. Quit",
        ]

        print(BORDER)
        print(
            "\n" +
            "██████████████████████████████████████████████████████\n" +
            "██                                                  ██\n" +
            f"██{PATH}           A-Maze-ing (jamourgh & aarid)       " +
            f"   {BORDER}██\n" +
            "██                                                  ██\n" +
            "██████████████████████████████████████████████████████"
        )

        for option in options:
            option_len = len(option)
            print("██                                                  ██")
            print("██", end="")
            print(f"{PATH}  {option}{BORDER}", end="")
            for _ in range(math.ceil((48 - option_len))):
                print(" ", end="")
            print("██")

        print("██                                                  ██")
        print("██████████████████████████████████████████████████████\n")
        print(RESET)
        while True:
            try:
                user_pick: int = int(input(f"Choice? (1 - {len(options)}): "))
            except Exception:
                print("ERROR: choise a valid option")
                continue
            if 1 <= user_pick <= len(options):
                return user_pick

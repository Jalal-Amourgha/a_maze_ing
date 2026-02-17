import sys
from typing import Any, List, Dict, Union
from mazegen.mazegen import MazeGenerator
from parsing import ft_parsing
import mazegen.mazegen as m


RESET = "\033[0m"


def main() -> None:
    argv: List[str] = sys.argv
    argc: int = len(argv)
    config: Dict = {}
    width: int = 0
    height: int = 0
    entry: tuple = (0, 0)
    exit: tuple = (1, 1)
    output_filename: str = ""
    perfect: bool = True
    seed: bool = False
    path: Union[str, List[str]] = ""
    current_algo: str = "DFS"

    if (argc != 2):
        print("Invalid program usage\n")
        return
    file_name = argv[1]
    try:
        with open(file_name, "r") as config_file:
            config = ft_parsing(config_file.read())
            if not (config):
                return
    except Exception:
        print("ERROR: config file is not exist")
        return

    width = config["WIDTH"]
    height = config["HEIGHT"]
    entry = config["ENTRY"]
    exit = config["EXIT"]
    perfect = config["PERFECT"]
    seed = config["SEED"]
    output_filename = config["OUTPUT_FILE"]

    maze: MazeGenerator = MazeGenerator(
        width, height, entry, exit, output_filename, perfect, seed)

    if (
        list(maze.entry)[::-1] in maze.pattern or
        list(maze.exit)[::-1] in maze.pattern
    ):
        print("WARNING: The corrdinate is a part of the pattern.")
        return

    maze.ft_generate_maze_DFS()

    maze.ft_generate_output_file()

    maze.ft_print_maze_animation()

    while (True):
        user_pick: int = maze.ft_maze_options()

        if (user_pick == 1):
            if current_algo == "DFS":
                path = ""
                maze.ft_generate_maze_DFS()
                maze.ft_print_maze_animation()
            else:
                path = ""
                maze.ft_generate_maze_prims()
                maze.ft_print_maze_animation()
        elif (user_pick == 2):
            path = ""
            maze.ft_generate_maze_DFS()
            maze.ft_print_maze_animation()
            current_algo = "DFS"
        elif (user_pick == 3):
            path = ""
            maze.ft_generate_maze_prims()
            maze.ft_print_maze_animation()
            current_algo = "PRIMS"
        elif (user_pick == 4):
            print("\33c", end="")
            if (path):
                path = ""
                maze.ft_print_maze_animation(path, False)
            else:
                path = maze.ft_find_path()
                maze.ft_print_maze_animation(path, False)
        elif (user_pick == 5):
            maze.ft_change_maze_color()
            print("\33c", end="")
            maze.ft_print_maze(maze.maze)
        elif (user_pick == 6):
            path = ""
            maze.ft_build_pattern_42()
            maze.ft_generate_maze_DFS()
            maze.ft_print_maze_animation()
        elif (user_pick == 7):
            path = ""
            maze.ft_build_pattern_13()
            maze.ft_generate_maze_DFS()
            maze.ft_print_maze_animation()
        elif (user_pick == 8):
            options = ["██", "🐸", "🐛", "🐾",
                       "🛹", "🛞", "⚪", "😐",
                       "⚾", "👣", "💡", "💣"]
            options_name = [
                "Wall",
                "Frog",
                "Bug",
                "Paw Print",
                "skyboard",
                "Wheel",
                "Circle",
                "Neutral FAce",
                "Baeball",
                "Foot Print",
                "Bulb",
                "Bomb",
                ]
            print("\n=== Chose new path emoji ===")
            for idx in range(len(options)):
                print(f"{idx + 1}. {options_name[idx]}: {options[idx]}")
            emoji_pick: Any = input("Chose emoji number: ")
            try:
                emoji_pick = int(emoji_pick)
                if not (1 <= emoji_pick <= len(options)):
                    raise ValueError
            except Exception:
                print("ERROR: Wrong Choose!")
                return
            m.PATH_BLOCK = options[emoji_pick - 1]
            maze.ft_print_maze_animation(path, False)
        elif (user_pick == 9):
            maze.ft_print_maze_animation()
            maze.ft_let_user_find_path()
        elif (user_pick == 10):
            maze.export_maze_png()
            print("\33c", end="")
            maze.ft_print_maze_animation(animation=False)
        else:
            return


main()

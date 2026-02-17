from typing import Any
import random


def ft_parsing(data: str) -> Any:
    """
        Parse and validate maze configuration data from a string.

        The input string should contain configuration lines in the form
        KEY=VALUE. Supported keys are:
            WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT, SEED

        Lines starting with "#" or empty lines are ignored.

        Parsing rules:
            - WIDTH, HEIGHT: integers
            - ENTRY, EXIT: "x,y" → tuple[int, int]
            - PERFECT: "True" or "False"
            - SEED: integer (or stored as string if not convertible)
            - OUTPUT_FILE: non-empty string

        Validation:
            - ENTRY and EXIT must be different
            - Minimum size: HEIGHT > 6, WIDTH > 8
            - ENTRY and EXIT must be within bounds

        Returns:
            dict: Parsed configuration values if valid.
            False: If a parsing or validation error occurs.
    """
    keys: list[str] = ["WIDTH",
                       "HEIGHT",
                       "ENTRY",
                       "EXIT",
                       "OUTPUT_FILE",
                       "PERFECT",
                       "SEED"]
    config_file: list[str] = data.split("\n")
    values: dict = {}
    # print(data)
    for config in config_file:
        if ("#" in config or not config):
            continue

        for key in keys:
            if (config and key in config.upper()):
                if ("=" not in config):
                    print("ERROR: wrong key in config")
                    return
                config = config[0:len(key)].upper() + config[len(key):]
                value: Any = config[len(key) + 1:]
                if (key == "HEIGHT" or key == "WIDTH"):
                    try:
                        values.update({key: int(value)})
                    except Exception:
                        print("ERROR: Wrong config key in HEIGHT OR WIDTH")
                        return (False)

                elif (key == "ENTRY" or key == "EXIT"):
                    value = value.split(",")
                    if (len(value) != 2):
                        print("ERROR: ENTRY/EXIT values are wrong!")
                        return
                    try:
                        values.update({key: (int(value[0]), int(value[1]))})
                    except Exception:
                        print("ERROR: Wrong config key IN ENTRY OR EXIT")
                        return (False)

                elif (key == "PERFECT"):
                    if (value.lower() == "true"):
                        values.update({key: True})
                    elif (value.lower() == "false"):
                        values.update({key: False})
                    else:
                        print("ERROR: Wrong config key IN PERFECT")
                        return (False)

                elif (key == "SEED"):
                    try:
                        n = int(value)
                        values.update({key: n})
                    except Exception:
                        values.update({key: value})

                elif (key == "OUTPUT_FILE"):
                    try:
                        if (len(value) <= 0):
                            raise ValueError
                        values.update({key: value})
                    except Exception:
                        print("ERROR: Wrong config key IN OUTPUT_FILE")
                        return (False)

    try:
        values["SEED"]
    except Exception:
        values.update({"SEED": random.randint(13, 37)})

    if (
        values["ENTRY"] == values["EXIT"] or
        values["HEIGHT"] <= 6 or
        values["WIDTH"] <= 8 or
        (values["ENTRY"][0] < 0 or values["ENTRY"][0] >= values["WIDTH"]) or
        (values["ENTRY"][1] < 0 or values["ENTRY"][1] >= values["HEIGHT"]) or
        (values["EXIT"][0] < 0 or values["EXIT"][0] >= values["WIDTH"]) or
        (values["EXIT"][1] < 0 or values["EXIT"][1] >= values["HEIGHT"])
    ):
        print("ERROR: Wrong configuration in config file.")
        return (False)

    return (values)

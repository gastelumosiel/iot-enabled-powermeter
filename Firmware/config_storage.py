"""Shared storage helpers for the ESP firmware."""

def save_string(filename, text):
    """Save a string to flash in the given file."""
    try:
        with open(filename, "w") as f:
            f.write(text)
        print("String saved successfully to {}.".format(filename))
    except Exception as e:
        print("Error saving string to {}: {}".format(filename, e))


def load_string(filename, default=""):
    """Load a string from flash file, return default if not found or error."""
    try:
        with open(filename, "r") as f:
            return f.read()
    except OSError:
        print("No saved string found in {}. Using default.".format(filename))
        return default
    except Exception as e:
        print("Error loading string from {}: {}".format(filename, e))
        return default


ssid_txt = "ssid.txt"
pass_txt = "pass.txt"
fb_txt = "firstboot.txt"

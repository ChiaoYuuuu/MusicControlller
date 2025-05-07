import sys
from .view_oracle import view_data
from .delete_oracle import delete_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify function：")
        print("  python query.py view     ")
        print("  python query.py delete   ")
        sys.exit(1)

    command = sys.argv[1]

    if command == "view":
        view_data()
    elif command == "delete":
        delete_data()
    else:
        print("Unsupported commands:", command)


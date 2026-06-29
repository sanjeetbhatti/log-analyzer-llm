import argparse


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log analysis assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser(name="analyze", help="Analyze a log file")

    return parser.parse_args()

def main():
    args = _parse_args()
    print(args)


if __name__ == "__main__":
    main()

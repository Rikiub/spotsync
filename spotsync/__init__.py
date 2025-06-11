from spotsync.utils.arguments import OPERATIONS, parseArguments


def run_cli():
    TARGET_FILE = ".spotdl"

    # start CLI
    args = parseArguments()

    OPERATIONS[args.operation](args.query, args.output, TARGET_FILE)

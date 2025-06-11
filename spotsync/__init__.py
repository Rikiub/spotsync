from utils.arguments import parseArguments, OPERATIONS


def run_cli():
    TARGET_FILE = ".spotdl"

    # start CLI
    args = parseArguments()

    OPERATIONS[args.operation](args.query, args.output, TARGET_FILE)

# Command line interface for small block forensics

import argparse

from flask_ml.flask_ml_cli import MLCli

from small_blk_forensics.backend.server import server


def main():
    parser = argparse.ArgumentParser(description="Analyze target directories with small block forensics")
    cli = MLCli(server, parser)
    cli.run_cli()


if __name__ == "__main__":
    main()

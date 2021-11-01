import argparse
import sys

from adastra_analysis import AdastraAnalysis


def main():

    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest='command')

    # Build subprocess
    build = subparser.add_parser('build')
    build.add_argument('-d', '--datasets', required=False, type=str, nargs='*')
    
    # Run subprocess
    run = subparser.add_parser('run')
    run.add_argument('-q', '--queries'    , required=False, type=str, nargs='*')
    run.add_argument('-s', '--screenplays', required=False, type=str, nargs='*')
    run.add_argument('-r', '--relplots'   , required=False, type=str, nargs='*')
    run.add_argument('-w', '--wordclouds' , required=False, type=str, nargs='*')

    # A custom configs path can be supplied.
    # Otherwise, it defaults to a library-internal one.
    default_configs_path = './configs.yaml'
    parser.add_argument('--configs', required=False, type=str, default=default_configs_path)

    args = parser.parse_args()
    # print(args)

    # Establish the AA.
    aa = AdastraAnalysis(args.configs)
    print(f"@ Retrieved configs from `{args.configs}`")

    # Rebuild the datasets if specified.
    if args.command == 'build':
        aa.build_datasets(args.datasets)

    elif args.command == 'run':
        aa.load_datasets()

        ###
        # Set the run options.
        ###

        # If a run is None, the parameter was not specified.
        # * If all runs are None, run all.
        # If a run is list(str), run those specific strings.
        # * If empty, run all.
        runs = {
            'queries'    : args.queries,
            'relplots'   : args.relplots,
            'screenplays': args.screenplays,
            'wordclouds' : args.wordclouds,
        }

        # If all runs are None, run all.
        if all(value is None for value in runs.values()):
            runs = {key: [] for key in runs}


        ###  
        # Retrieve the datasets and complete each run.
        ### 

        # Retrieve the runs from the arguments.
        run_lambdas = {
            'queries'    : aa.run_queries,
            'relplots'   : aa.run_relplots,
            'screenplays': aa.run_screenplays,
            'wordclouds' : aa.run_wordclouds,
        }

        for run_type, run_args in runs.items():

            # Ignore undefined runs.
            # (Runs are redefined as [] if all None.)
            if run_args is None:
                continue

            # Apply the specified lambda using the provided arguments.
            run_lambdas[run_type](run_args)
        


if __name__ == '__main__':
    main()

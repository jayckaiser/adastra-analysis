import argparse
import sys

from adastra_analytics import AdastraAnalytics


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--datasets'   , required=False, type=str, nargs='*')
    parser.add_argument('-q', '--queries'    , required=False, type=str, nargs='*')
    parser.add_argument('-s', '--screenplays', required=False, type=str, nargs='*')
    parser.add_argument('-r', '--relplots'   , required=False, type=str, nargs='*')
    parser.add_argument('-w', '--wordclouds' , required=False, type=str, nargs='*')
    parser.add_argument('-a', '--all'        , type=bool, action='store_true')

    # A custom configs path can be supplied.
    # Otherwise, it defaults to a library-internal one.
    default_configs_path = '../configs.yml'
    parser.add_argument('--configs', required=False, type=str, default=default_configs_path)

    args = parser.parse_args()

    # Establish the AA.
    aa = AdastraAnalytics(args.configs)
    print(f"@ Retrieved configs from `{args.configs}`")

    # Rebuild the datasets if specified.
    if args.datasets is not None:
        aa.build_datasets()
    else:
        aa.load_datasets()

    # End prematurely if no runs are specified.
    run_args = [
        args.queries,
        args.screenplays,
        args.relplots,
        args.wordclouds,
        args.all,
    ]
    if all(lambda x: x is None, run_args):
        sys.exit(0)


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

    # Run all if specified.
    if args.run is True:
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

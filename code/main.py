import argparse

from adastra_analytics import AdastraAnalytics


def main():

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command')

    build = subparser.add_parser('build')
    build.add_argument('--nlp', required=False, action='store_true')

    run = subparser.add_parser('run')
    run.add_argument('--queries'    , required=False, type=str, nargs='*')
    run.add_argument('--screenplays', required=False, type=str, nargs='*')
    run.add_argument('--relplots'   , required=False, type=str, nargs='*')
    run.add_argument('--wordclouds' , required=False, type=str, nargs='*')

    # A custom configs path can be supplied.
    # Otherwise, it defaults to a library-internal one.
    default_configs_path = '../configs.yml'
    parser.add_argument('--configs', required=False, type=str, default=default_configs_path)

    args = parser.parse_args()

    # Establish the AA.
    aa = AdastraAnalytics(args.configs)

    # Build the dataset if specified.
    if args.command == 'build':

        aa.build_adastra_dataset(args.nlp)
        aa.save_adastra_dataset()

    elif args.command == 'run':

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

        # Retrieve the datasets.
        aa.load_adastra_dataset()
        aa.build_datasets()

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

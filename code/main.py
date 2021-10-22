import argparse
import sys

from adastra_analytics import AdastraAnalytics


def main():

    parser = argparse.ArgumentParser()

    # Add all arguments and parse.
    parser.add_argument('--build-dataset', required=False, action='store_true')
    parser.add_argument('--build-nlp-dataset', required=False, action='store_true')
    parser.add_argument('-r', '--run', type=str, nargs='*')
    parser.add_argument('--queries', required=False, type=str, nargs='*')
    parser.add_argument('--screenplays', required=False, type=str, nargs='*')
    parser.add_argument('--relplots', required=False, type=str, nargs='*')
    parser.add_argument('--wordclouds', required=False, type=str, nargs='*')

    args = parser.parse_args()

    # Check that parameters have actually been specified.
    if not vars(args):
        print("No arguments specified! Use `python main.py -h` for help.")
        sys.exit(0)

    # Separate logic for --run.
    runs = args.run or []

    if args.run is not None:
        # If no runs are specified, run all 
        valid_runs = [
            'queries', 'screenplays', 'relplots', 'wordclouds'
        ]   

        if not runs:
            runs = valid_runs

        # Verify that all run params are valid, if provided.
        # If an invalid run is provided, fail.
        all_valid = True
        for run_type in runs:
            if run_type not in valid_runs:
                print(f"Run type `{run_type}` is not defined!")
                all_valid = False

        if not all_valid:    
            print(f"Valid options: [{', '.join(valid_runs)}]")
            sys.exit(0)

    # Build the dataset if specified.
    aa = AdastraAnalytics(
        build_dataset=args.build_dataset or args.build_nlp_dataset,
        use_nlp=args.build_nlp_dataset,
    )

    # Run the parameters, based on `args.run`.
    # (These are run in order of fastest to slowest.)
    if args.queries is not None or 'queries' in runs:
        aa.run_queries(args.queries)

    if args.screenplays is not None or 'screenplays' in runs:
        aa.run_screenplays(args.screenplays)

    if args.relplots is not None or 'relplots' in runs:
        aa.run_relplots(args.relplots)

    if args.wordclouds is not None or 'wordclouds' in runs:
        aa.run_wordclouds(args.wordclouds)



if __name__ == '__main__':
    main()

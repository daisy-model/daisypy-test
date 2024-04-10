'''Program for running daisy tests'''
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import warnings

#pylint: disable=import-error, no-name-in-module
from daisypy.test.compare_dlf_files import compare_dlf_files

def main():
    # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser(
        description='Run daisy programs and compare generated output against a reference'
    )
    parser.add_argument('daisy_binary', type=str, help='Name of or path to the daisy binary')
    parser.add_argument('program', type=str, help='Path to the .dai file to run')
    parser.add_argument('reference_dir', type=str, help='''Path to directory containing reference
    output files. All files in the directory will be compared against the generated log files''')
    parser.add_argument('out_dir', type=str, help='Output directory for errors')
    parser.add_argument('--no-warnings', action='store_true',
                        help='If set do not emit warnings from SML comparisons')
    parser.add_argument('--sml-identity-threshold', type=float, default=0.001,
                        help='Consider two values identical if their difference is less than '
                        '`sml_identity_threshold` * sml')
    parser.add_argument('--default-float-epsilon', type=float, default=1e-8, help='''Pass numeric
    comparison if absolute difference is less than this value. Only used if no SML is defined''')
    parser.add_argument('--path', type=str, help='Add to path when running daisy', default='.')
    args = parser.parse_args()

    if args.no_warnings:
        warnings.showwarning = lambda message, *args: message
    else:
        warnings.showwarning = lambda message, category, *args: \
            print(category.__name__, message, file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmpdir:
        daisy_args = [args.daisy_binary, '-q', '-d', tmpdir, '-D', args.path, args.program]
        print(' '.join(daisy_args))
        result = subprocess.run(daisy_args, check=False)
        if result.returncode != 0:
            print('ERROR: Daisy execution failed', file=sys.stderr)
            return 1

        errors, not_similar, not_identical = [], [], []
        for entry in os.scandir(args.reference_dir):
            if entry.is_file():
                new_file_path = os.path.join(tmpdir, entry.name)
                if not os.path.exists(new_file_path):
                    errors.append((entry.name, [f'{new_file_path} does not exist']))
                else:
                    file_type = os.path.splitext(entry.name)[-1]
                    if file_type != '.dlf':
                        warnings.warn(f'Skipping file type {file_type}')
                    else:
                        failed = False
                        err, not_sim, not_id = compare_dlf_files(
                            entry.path,
                            new_file_path,
                            precision=args.default_float_epsilon,
                            sml_identity_threshold=args.sml_identity_threshold
                        )
                        if len(err) > 0:
                            errors.append((entry.name, err))
                            failed = True
                        if len(not_sim) > 0:
                            not_similar.append((entry.name, not_sim))
                            failed = True
                        if len(not_id) > 0:
                            not_identical.append((entry.name, not_id))
                            failed = True
                        if failed:
                            os.makedirs(args.out_dir, exist_ok=True)
                            error_file_path = os.path.join(args.out_dir, f'error_{entry.name}')
                            ref_file_path = os.path.join(args.out_dir, f'ref_{entry.name}')
                            shutil.copy(new_file_path, error_file_path)
                            shutil.copy(entry.path, ref_file_path)
    status = 0
    if len(errors) > 0:
        print('== Errors ==')
        for name, err in errors:
            print(name, *errors, sep='\n\t', end='\n\n')
        status += 1

    if len(not_similar) > 0:
        print('== Not similar ==')
        for name, not_sim in not_similar:
            print(name, *not_sim, sep='\n\t', end='\n\n')
        status += 2

    if len(not_identical) > 0:
        print('== Not identical ==')
        for name, not_id in not_identical:
            print(name, *not_id, sep='\n\t', end='\n\n')
    return status

if __name__ == '__main__':
    sys.exit(main())

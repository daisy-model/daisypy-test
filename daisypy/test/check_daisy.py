'''Program for running daisy tests'''
import argparse
import subprocess
import sys
import tempfile

def main():
    # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser(
        description='Run daisy programs and check that they dont fail'
    )
    parser.add_argument('daisy_binary', type=str, help='Name of or path to the daisy binary')
    parser.add_argument('program', type=str, help='Path to the .dai file to run')
    parser.add_argument('--path', type=str, help='Add to path when running daisy', default='.')
    args = parser.parse_args()


    with tempfile.TemporaryDirectory() as tmpdir:
        daisy_args = [args.daisy_binary, '-q', '-d', tmpdir, '-D', args.path, args.program]
        print(' '.join(daisy_args))
        result = subprocess.run(daisy_args, check=False)
        if result.returncode != 0:
            print('ERROR: Daisy execution failed', file=sys.stderr)
        return result.returncode

if __name__ == '__main__':
    sys.exit(main())

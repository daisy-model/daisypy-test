# daisypy-test
Test framework for daisy log files (.dlf)

    pip install daisypy-test@git+https://github.com/daisy-model/daisypy-test

## Smallest meaningfull level
The smallest meaningful level (SML) for a particular value is the smallest scale at which differences are meaningful. For example, the SML for field nitrogen is 1 kg/ha, which means that differences less than 1 kg/ha are ignored.

An SML for a specific log is defined in a `.toml` file in `daisypy/test/sml-definitions`. Mapping from log names to SMLs are done in `daisypy/test/sml.py`. Log names are specified when the log is defined, `(deflog "log name" ...`.

There are general SML definitions for chemicals, but this might not work for specific chemicals. To define an SML for a specific chemical you should add a mapping with the name `log-name chemical-name`. For example, to add an SML definition for "N" in the "Field chemical" log you should a mapping named `Field chemical N`.

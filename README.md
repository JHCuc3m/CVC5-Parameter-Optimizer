This project uses SMAC3 to automatically find optimal parameter settings for the CVC5 SMT solver. It aims to improve solving time for specific SMT2 problems by tuning CVC5's parameters.

### Requirements
- Python 3.8+
- CVC5 (SMT Solver)
- SMAC3 (Parameter Optimization Framework)
- NumPy <= 1.24.3 (due to compatibility issues with ConfigSpace)

## Usage

```bash
python cvc5_runner.py path/to/your/file.smt2
```

## Output
The script will:
1. Create a configuration space from CVC5's available parameters
2. Run SMAC3 optimization to find the best parameter settings
3. Print the best configuration found
4. Save optimization results in the `smac_output` directory

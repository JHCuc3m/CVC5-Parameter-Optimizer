from cvc5.pythonic import *
import sys
import argparse
import subprocess
from typing import Dict, Any, List, Union, Optional
from get_params import get_parameter_mappings, validate_param

class CVC5Solver:
    def __init__(self):
        """Initialize CVC5 solver with parameter mappings"""
        self.param_mappings = get_parameter_mappings()
        self.solver_options = []

    def set_option(self, param: str, value: Any = None) -> None:
        """
        Set a solver option with validation using parameter mappings
        Args:
            param (str): Parameter name
            value (Any, optional): Parameter value, not needed for boolean parameters
        """

        #set value to None is is not avlid
        if validate_param(param, value, self.param_mappings) is False: 
            print(f"Warning: Invalid value {value} for parameter {param}")
            value = None
        
        # Check if parameter exists in any category
        param_found = False
        for category, params in self.param_mappings.items():
            if param in params:
                param_found = True
                if category == 'bool_params':
                    # Boolean parameters only need the flag
                    self.solver_options.append(f"--{param}")
                else: 
                    # Other parameters need both flag and value
                    if value is not None:
                        self.solver_options.extend([f"--{param}", str(value)])
                    else:
                        print(f"Warning: Value required for {param} ({category})")
                break
        
        if not param_found:
            print(f"Warning: Unknown parameter {param}")

    def solve_smt2_file(self, filename):
        """
        Solve the given SMT2 file using cvc5
        Args:
            filename (str): Path to the SMT2 file
        Returns:
            str: Output from cvc5
        """
        try:
            command =  ['cvc5'] + self.solver_options + ['--produce-models'] + [filename]
            # Run cvc5 directly on the SMT2 file with model generation
            process = subprocess.run(command, 
                                capture_output=True, 
                                text=True,
                                check=True)
            
            return process.stdout
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"CVC5 error: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Solve SMT2 file using cvc5')
    parser.add_argument('file', help='Path to SMT2 file')
    
    args = parser.parse_args()

    try:
        solver = CVC5Solver()
        solver.set_option("uf-ss-fair")
        solver.set_option("sygus-si", "ll")
        output = solver.solve_smt2_file(args.file)
        print(output)
                
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
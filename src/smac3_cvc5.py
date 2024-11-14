from ConfigSpace import Configuration, ConfigurationSpace, Float, Integer, Categorical
from smac import HyperparameterOptimizationFacade, Scenario
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional
from get_params import get_parameter_mappings
import numpy as np

class CVC5Optimizer:
    def __init__(self, smt2_file: str, timeout: int = 300):
        """
        Initialize CVC5 parameter optimizer
        
        Args:
            smt2_file (str): Path to SMT2 file to optimize for
            timeout (int): Maximum time (in seconds) for each CVC5 run
        """
        self.smt2_file = smt2_file
        self.timeout = timeout
        self.param_mappings = get_parameter_mappings()
        self.configspace = self._create_configuration_space()

    def _create_configuration_space(self) -> ConfigurationSpace:
        """
        Create SMAC configuration space from CVC5 parameters
        """
        cs = ConfigurationSpace()

        # Add numeric parameters
        for param, info in self.param_mappings['int_params'].items():
            # Only add parameters with defined bounds
            if info['min'] is not None and info['max'] is not None:
                cs.add(
                    Integer(param, bounds = (info['min'], info['max']), default=info['default'])
                )

        # Add float parameters
        for param, info in self.param_mappings['float_params'].items():
            if info['min'] is not None and info['max'] is not None:
                cs.add(
                    Float(param, bounds = (info['min'], info['max']), default=info['default'])
                )

        # Add categorical parameters (mode parameters)
        for param, modes in self.param_mappings['mode_params'].items():
            if modes:  # Only add if we have valid modes
                cs.add(
                    Categorical(param, modes)
                )

        # Add selected boolean parameters that might affect performance
        important_bool_params = [
            'produce-models',
            'incremental',
            'strings-exp',
            'use-approx',
            'simp-ite-compress',
            'simplification'
        ]
        
        for param in important_bool_params:
            if param in self.param_mappings['bool_params']:
                cs.add(
                    Categorical(param, [True, False], 
                              default=self.param_mappings['bool_params'][param])
                )

        return cs

    def _run_cvc5(self, config: Configuration, seed: int = 0) -> float:
        """
        Run CVC5 with given configuration and return execution time
        
        Args:
            config (Configuration): Parameter configuration to test
            seed (int): Random seed for reproducibility
        Returns:
            float: Execution time in seconds (or timeout value if failed)
        """
        command = ['cvc5']
        
        # Add parameters based on their types
        for param, value in config.items():
            if param in self.param_mappings['bool_params']:
                if value:  # Only add flag if True
                    command.append(f'--{param}')
            else:
                command.extend([f'--{param}', str(value)])

        # Add random seed
        command.extend(['--random-seed', str(seed)])

        command.append(self.smt2_file)

        try:
            start_time = time.time()
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            end_time = time.time()
            
            if process.returncode == 0:
                return end_time - start_time
            else:
                return self.timeout
                
        except subprocess.TimeoutExpired:
            return self.timeout
        except Exception as e:
            print(f"Error running CVC5: {str(e)}")
            return self.timeout

    def optimize(self, n_trials: int = 100, n_workers: int = 1) -> Dict[str, Any]:
        """
        Run SMAC optimization to find best parameters
        
        Args:
            n_trials (int): Number of configurations to try
            n_workers (int): Number of parallel workers
            
        Returns:
            Dict[str, Any]: Best parameter configuration found
        """
        # Define the optimization scenario
        scenario = Scenario(
            configspace=self.configspace,
            deterministic=False,
            n_trials=n_trials,
            n_workers=n_workers,
            output_directory=Path("smac_output")
        )

        # Create optimization facade
        smac = HyperparameterOptimizationFacade(
            scenario=scenario,
            target_function=self._run_cvc5,
            overwrite=True
        )

        # Run optimization
        incumbent = smac.optimize()
        
        return incumbent

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Optimize CVC5 parameters using SMAC3')
    parser.add_argument('file', help='Path to SMT2 file')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout for each CVC5 run (seconds)')
    parser.add_argument('--trials', type=int, default=1000,
                       help='Number of configurations to try')
    parser.add_argument('--workers', type=int, default=1,
                       help='Number of parallel workers')
    
    args = parser.parse_args()

    optimizer = CVC5Optimizer(args.file, args.timeout)
    
    print("Starting parameter optimization...")
    best_config = optimizer.optimize(n_trials=args.trials, n_workers=args.workers)
    
    print("\nBest configuration found:")
    for param, value in best_config.items():
        print(f"{param}: {value}")

if __name__ == "__main__":
    main()
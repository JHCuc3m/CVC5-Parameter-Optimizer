from cvc5.pythonic import *
from typing import Dict, Any, List, Union, Optional

def get_parameter_mappings():
    """
    Creates mappings of CVC5 parameters categorized by their types.
    For numeric parameters (int and float), includes min/max bounds if available.
    """
    solver = Solver()
    
    param_types = {
        'bool_params': {},
        'int_params': {},  # Will store dict with 'default', 'min', 'max'
        'float_params': {},  # Will store dict with 'default', 'min', 'max'
        'string_params': {},
        'mode_params': {}
    }
    
    # Get all option names
    option_names = solver.getOptionNames()
    
    # Categorize each parameter
    for option in option_names:
        try:
            info = solver.getOptionInfo(option)
            
            if info['type'] == bool:
                param_types['bool_params'][option] = info['default']
            
            elif info['type'] == int:
                param_types['int_params'][option] = {
                    'default': info['default'],
                    'min': info.get('minimum'),
                    'max': info.get('maximum')
                }
            
            elif info['type'] == float:
                param_types['float_params'][option] = {
                    'default': info['default'],
                    'min': info.get('minimum'),
                    'max': info.get('maximum')
                }
            
            elif info['type'] == str:
                param_types['string_params'][option] = info['default']
            
            elif info['type'] == 'mode':
                param_types['mode_params'][option] = info['modes']
                
        except Exception as e:
            print(f"Error processing option {option}: {str(e)}")
            continue
    
    return param_types

def print_param_info():
    """Prints parameter information in a readable format"""
    params = get_parameter_mappings()
    
    print("Boolean Parameters (with defaults):")
    print("-" * 50)
    for param, value in sorted(params['bool_params'].items()):
        print(f"{param}: {value}")
    
    print("\nInteger Parameters (with defaults and bounds):")
    print("-" * 50)
    for param, info in sorted(params['int_params'].items()):
        bounds = f"min: {info['min'] if info['min'] is not None else 'None'}, " \
                f"max: {info['max'] if info['max'] is not None else 'None'}"
        print(f"{param}: default={info['default']}, {bounds}")
    
    print("\nFloat Parameters (with defaults and bounds):")
    print("-" * 50)
    for param, info in sorted(params['float_params'].items()):
        bounds = f"min: {info['min'] if info['min'] is not None else 'None'}, " \
                f"max: {info['max'] if info['max'] is not None else 'None'}"
        print(f"{param}: default={info['default']}, {bounds}")
    
    print("\nString Parameters (with defaults):")
    print("-" * 50)
    for param, value in sorted(params['string_params'].items()):
        print(f"{param}: {value}")
    
    print("\nMode Parameters (with possible values):")
    print("-" * 50)
    for param, values in sorted(params['mode_params'].items()):
        print(f"{param}: {values}")

def validate_param(param_name: str, value: Any, param_mappings: Dict) -> bool:
    """
    Validates if a parameter value is valid according to its type and bounds.
    """
    for category, params in param_mappings.items():
        if param_name in params:
            if category == 'bool_params':
                if value is None: 
                    return True
                return isinstance(value, bool)
            
            elif category == 'int_params':
                if not isinstance(value, int):
                    return False
                info = params[param_name]
                if info['min'] is not None and value < info['min']:
                    return False
                if info['max'] is not None and value > info['max']:
                    return False
                return True
            
            elif category == 'float_params':
                if not isinstance(value, (int, float)):
                    return False
                info = params[param_name]
                if info['min'] is not None and value < info['min']:
                    return False
                if info['max'] is not None and value > info['max']:
                    return False
                return True
            
            elif category == 'string_params':
                return isinstance(value, str)
            
            elif category == 'mode_params':
                return value in params[param_name]
    return False

if __name__ == "__main__":
    print_param_info()
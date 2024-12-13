import ast
from itertools import zip_longest

class ModelEval:
    #parse output from model
    def parse_model_output(output_string):
        parsed_output = []
        
        for line in output_string.strip().splitlines():
            # Split function name and arguments string
            func_name, args_str = line.split("(", 1)
            args_str = args_str.rstrip(")")  # Remove the closing parenthesis
            
            positional_args = []
            named_args = {}
            
            # Split arguments by commas
            for arg in args_str.split(","):
                arg = arg.strip()
                if "=" in arg:  # Named argument
                    key, value = map(str.strip, arg.split("=", 1))
                    try:
                        named_args[key] = ast.literal_eval(value)  # Safely parse named argument value
                    except Exception:
                        named_args[key] = value  # If parsing fails, keep it as a string
                else:  # Positional argument
                    try:
                        positional_args.append(ast.literal_eval(arg))  # Safely parse positional argument
                    except Exception:
                        positional_args.append(arg)  # If parsing fails, keep it as a string
            
            # Combine positional and named arguments
            args = positional_args + [f"{key}={value}" for key, value in named_args.items()]
            
            # Append the parsed function
            parsed_output.append((func_name, args))
        
        return parsed_output
    
    def find_expected_args(parsed_output, function_name):
        for func_name, args in parsed_output:
            if func_name == function_name:
                return args
        return None

    def calculate_accuracy(model_output, expected_output):
        total_functions = max(len(model_output), len(expected_output))
        function_matches = 0
        total_arguments = 0
        argument_matches = 0

        # Iterate over both model and expected outputs
        for (func_name, args), (expected_func, expected_args) in zip_longest(model_output, expected_output, fillvalue=(None, [])):
            # Check function name match
            if func_name == expected_func:
                function_matches += 1

            
            # Check arguments match
            exp_args= ModelEval.find_expected_args(expected_output, func_name)
            if exp_args != None:
                total_arguments += max(len(exp_args), len(args))
                argument_matches += sum( 1 for arg, 
                                        exp_arg in zip_longest(args, exp_args, fillvalue=None) if isinstance(arg, str) and isinstance(exp_arg, str) and arg.lower() == exp_arg.lower())

        # Compute accuracies
        function_accuracy = function_matches / total_functions if total_functions > 0 else 0
        argument_accuracy = argument_matches / total_arguments if total_arguments > 0 else 0
        overall_accuracy = (function_accuracy + argument_accuracy) / 2

        return {
            "function_accuracy": function_accuracy,
            "argument_accuracy": argument_accuracy,
            "overall_accuracy": overall_accuracy,
        }
    
    def evaluate_model_with_accuracy(expected_output, model_output):
        results = {}
            
        # Parse the model output
        modelOutDict = ModelEval.parse_model_output(expected_output)
        expOutDict = ModelEval.parse_model_output(model_output)
        # Calculate accuracy
        accuracy = ModelEval.calculate_accuracy(modelOutDict, expOutDict)
    
        # Display results
        print(f"Function Accuracy: {accuracy['function_accuracy']:.2f}")
        print(f"Argument Accuracy: {accuracy['argument_accuracy']:.2f}")
        print(f"Overall Accuracy: {accuracy['overall_accuracy']:.2f}\n")

        return accuracy

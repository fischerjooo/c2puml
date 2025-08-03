import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.models import ProjectModel
import tempfile

class TestFunctionParameterParsing:
    """Test function parameter parsing issues"""
    
    def test_function_parameter_parsing(self):
        """Test that function parameters are correctly parsed and not labeled as unnamed"""
        
        # Test code with function that has named parameters
        test_code = """
        int execute_operations(
            int value,
            math_ops_array_t ops,
            int op_count
        );
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            
            # Add to project model
            project_model.files[file_model.name] = file_model
            
            # Check that we have functions
            assert len(file_model.functions) > 0, "No functions found"
            
            # Find the execute_operations function
            execute_func = None
            for func in file_model.functions:
                if func.name == "execute_operations":
                    execute_func = func
                    break
            
            assert execute_func is not None, "execute_operations function not found"
            
            # Check parameters
            assert len(execute_func.parameters) == 3, f"Expected 3 parameters, got {len(execute_func.parameters)}"
            
            # Print actual parameters for debugging
            print(f"Actual function parameters: {[(p.name, p.type) for p in execute_func.parameters]}")
            
            # Check each parameter
            expected_params = [
                ("value", "int"),
                ("ops", "math_ops_array_t"), 
                ("op_count", "int")
            ]
            
            for i, (expected_name, expected_type) in enumerate(expected_params):
                param = execute_func.parameters[i]
                assert param.name == expected_name, f"Parameter {i} name mismatch: expected '{expected_name}', got '{param.name}'"
                assert param.type == expected_type, f"Parameter {i} type mismatch: expected '{expected_type}', got '{param.type}'"
            
            print(f"Function parameters: {[(p.name, p.type) for p in execute_func.parameters]}")
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_complex_function_parameters(self):
        """Test complex function parameters with various types"""
        
        test_code = """
        void process_data(
            const char* filename,
            int* result_count,
            struct config_t* config,
            void (*callback)(int, char*)
        );
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            
            # Add to project model
            project_model.files[file_model.name] = file_model
            
            # Find the process_data function
            process_func = None
            for func in file_model.functions:
                if func.name == "process_data":
                    process_func = func
                    break
            
            assert process_func is not None, "process_data function not found"
            
            # Check parameters
            assert len(process_func.parameters) == 4, f"Expected 4 parameters, got {len(process_func.parameters)}"
            
            # Check that all parameters have names
            for i, param in enumerate(process_func.parameters):
                assert param.name, f"Parameter {i} should have a name"
            
            print(f"Complex function parameters: {[(p.name, p.type) for p in process_func.parameters]}")
            
        finally:
            # Clean up
            os.unlink(temp_file)

if __name__ == "__main__":
    test = TestFunctionParameterParsing()
    test.test_function_parameter_parsing()
    test.test_complex_function_parameters()
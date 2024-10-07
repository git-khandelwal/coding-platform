import sys
import json

def execute_code(func_name, code, serialized_input):
    exec_globals = {}
    exec(code, exec_globals)
    func = exec_globals.get(func_name)
    if not func:
        return json.dumps({"status": "Error", "result": "Function not found"})
    # print(type(serialized_input), "Type of serialized input inside execute code function")
    inputs = json.loads(serialized_input)
    # print(type(inputs), " Type of input after json loads")
    try:
        output = func(**inputs)
        # print(output,": This is the output, code run successfully")
        return json.dumps({"status": "Success", "result": output})
    except Exception as e:
        # print("Inside Exception")
        return json.dumps({"status": "Error", "result": str(e)})

if __name__ == "__main__":
    func_name = sys.argv[1]
    code = sys.argv[2]
    # print("Before arg3")
    serialized_input = json.loads(sys.argv[3])
    # print(type(sys.argv[3]), " Type of sys argv3")
    # print("Before Execute code function")
    result = execute_code(func_name, code, sys.argv[3])
    print(result)

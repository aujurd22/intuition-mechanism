def follows_rule(code_str: str) -> bool:
    import ast
    
    tree = ast.parse(code_str)
    
    # Check for any function definitions inside (we only care about the top-level function)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for any assignments to arguments (mutation)
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Assign):
                    for target in subnode.targets:
                        if isinstance(target, ast.Name) and target.id in [arg.arg for arg in node.args.args]:
                            return False
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id in [arg.arg for arg in node.args.args]:
                            return False
                if isinstance(subnode, ast.AugAssign):
                    if isinstance(subnode.target, ast.Name) and subnode.target.id in [arg.arg for arg in node.args.args]:
                        return False
                    if isinstance(subnode.target, ast.Attribute) and isinstance(subnode.target.value, ast.Name) and subnode.target.value.id in [arg.arg for arg in node.args.args]:
                        return False
                # Check for calls to external functions that might have side effects
                if isinstance(subnode, ast.Call):
                    # Heuristic: any call to a function not defined in the code is considered impure
                    # (except built-in pure functions like len, print is impure)
                    if isinstance(subnode.func, ast.Name):
                        if subnode.func.id not in dir(__builtins__) or subnode.func.id in ['print', 'input', 'open', 'exec', 'eval']:
                            return False
                    elif isinstance(subnode.func, ast.Attribute):
                        # Method calls on arguments are considered impure
                        if isinstance(subnode.func.value, ast.Name) and subnode.func.value.id in [arg.arg for arg in node.args.args]:
                            return False
                        # Any method call that's not a known pure method (like .append is impure)
                        if subnode.func.attr in ['append', 'extend', 'insert', 'remove', 'pop', 'sort', 'reverse', 'update', 'add', 'discard', 'clear']:
                            return False
            # Check for global/nonlocal statements
            for subnode in ast.walk(node):
                if isinstance(subnode, (ast.Global, ast.Nonlocal)):
                    return False
    return True

import json
code_str = "def with_discounts(cart):\n    return [{**item, 'price': item['price'] * 0.9} for item in cart]\n"
result = follows_rule(code_str)
print('PURE' if result else 'IMPURE')

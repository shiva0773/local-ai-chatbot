import ast
import operator


# Supported mathematical operations
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculator(expression: str):
    """
    Safely evaluate basic mathematical expressions.
    """

    def evaluate(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

        elif isinstance(node, ast.BinOp):
            operation = OPERATORS.get(type(node.op))

            if operation:
                return operation(
                    evaluate(node.left),
                    evaluate(node.right)
                )

        elif isinstance(node, ast.UnaryOp):
            operation = OPERATORS.get(type(node.op))

            if operation:
                return operation(evaluate(node.operand))

        raise ValueError("Unsupported mathematical expression")

    try:
        parsed_expression = ast.parse(expression, mode="eval")
        result = evaluate(parsed_expression.body)
        return result

    except ZeroDivisionError:
        return "Error: Division by zero"

    except Exception as exc:
        return f"Calculation error: {exc}"
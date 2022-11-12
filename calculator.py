import sys

def is_math_symbol(character):
    return character == '*' \
        or character == '/' \
        or character == '-' \
        or character == '+' \
        or character == '^' \

def is_symbol(character):
    return character == '*' \
        or character == '/' \
        or character == '-' \
        or character == '+' \
        or character == '^' \
        or character == '_' \
        or character == '(' \
        or character == ')' \
        or character == '[' \
        or character == ']'

def tokenize(expression):
    expression = expression + " "

    tokens = []
    buffer = ""
    for character in expression:
        if is_symbol(character):
            if buffer:
                tokens.append(buffer)
            tokens.append(character)
            buffer = ""
        elif character == ' ':
            if buffer:
                tokens.append(buffer)
            buffer = ""
        else:
            buffer += character

    return tokens

class Rule:
    pass

def parse_rules(rules):
    rules_out = {}

    for rule in rules.split('\n'):
        if rule:
            rule_split = rule.split(' ')
            rule_type = rule_split[0]

            rule_data = " ".join(rule_split[1:])
            input = rule_data[0 : rule_data.index("=>")].strip()
            output = rule_data[rule_data.index("=>") + 2 : ].strip()

            if not rule_type in rules_out:
                rules_out[rule_type] = []

            rules_out[rule_type].append((tokenize(input), tokenize(output)))

    return rules_out

def get_binding(expression, index, continues):
    if continues:
        multiple_tokens = []
        inside_parenthesis = 1
        while inside_parenthesis > 0:
            if expression[index] == "(" or expression[index] == "[":
                inside_parenthesis += 1
            elif expression[index] == ")" or expression[index] == "]":
                inside_parenthesis -= 1

            multiple_tokens.append(expression[index])

            index += 1

        return multiple_tokens[0:-1], index - 1
    elif expression[index] == '(':
        binding = ["("]
        inside_parenthesis = 1
        index += 1
        while inside_parenthesis > 0:
            binding.append(expression[index])

            if expression[index] == '(':
                inside_parenthesis += 1
            elif expression[index] == ')':
                inside_parenthesis -= 1

            index += 1

        return binding, index
    else:
        return [expression[index]], index + 1

def apply_bindings(expression, bindings):
    expression_output = []

    for token in expression:
        if token in bindings:
            expression_output.extend(bindings[token])
        else:
            expression_output.append(token)

    return expression_output

def is_str_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def apply(expression, rules, command_in):
    command = expression[0]
    valid = False
    if command in rules:
        valid, expression = apply(expression[2:-1], rules, command)

    if command_in and command_in in rules:
        return apply_rule(expression, rules, command_in)

    return valid, expression

def apply_rule(expression, rules, rule_type):
    for rule in rules[rule_type]:
        rule_input = rule[0]
        expression_index = 0

        bindings = {}

        rule_invalid = False

        for input in rule_input:
            if expression_index >= len(expression):
                rule_invalid = True
                break

            if is_symbol(input):
                if expression[expression_index] == input:
                    expression_index += 1
                else:
                    rule_invalid = True
                    break
            else:
                binding, expression_index = get_binding(expression, expression_index, input.endswith(".."))
                is_constant = True
                for token in binding:
                    if not is_str_int(token) or not token == "(" or not token == ")" or not is_symbol(token):
                        is_constant = False

                if input.isupper() and is_constant:
                    rule_invalid = True
                    break
                elif input.islower() and not (len(binding) == 1 and not is_str_int(binding[0])):
                    rule_invalid = True
                    break

                bindings[input] = binding

        if not rule_invalid and expression_index == len(expression):
            rule_output = rule[1]
            applied_bindings = apply_bindings(rule_output, bindings)
            applied_bindings_new = []

            index = 0
            while index < len(applied_bindings):
                if applied_bindings[index] in rules:
                    cached_expression = []

                    cached_expression.append(applied_bindings[index])
                    cached_expression.append(applied_bindings[index + 1])
                    index += 2

                    inside_parenthesis = 1
                    while inside_parenthesis > 0:
                        if applied_bindings[index] == "(":
                            inside_parenthesis += 1
                        elif applied_bindings[index] == ")":
                            inside_parenthesis -= 1

                        cached_expression.append(applied_bindings[index])

                        index += 1

                    applied, applied_result = apply(cached_expression, rules, None)
                    if applied and applied_result:
                        applied_bindings_new.extend(applied_result)
                    else:
                        return False, None
                else:
                    applied_bindings_new.append(applied_bindings[index])
                    index += 1

            return True, applied_bindings_new

    return False, None

rules = """
derivative Aa+Bb => derivative(Aa)+derivative(Bb)
derivative Aa-Bb => derivative(Aa)-derivative(Bb)
derivative (Aa..) => (derivative(Aa..))
derivative A*b^C => (A*C)*b^(C-1)
derivative a^B => B*a^(B-1)
derivative A*b => A
derivative b => 1
derivative A => 0
derivative Aa*Bb => Aa*derivative(Bb)+Bb*derivative(Aa)
derivative Aa/Bb => (Bb*derivative(Aa)-Aa*derivative(Bb))/Bb^2
derivative A^b => A^b*(derivative(b)*ln(A))
derivative log_A[Bb..] => log_A[Bb..]*((derivative(Bb..))*(1/ln[A]))

antiderivative a => (1/2)*a^2
antiderivative A*b^C => ((1/(C+1))*(A))*b^(C+1)
"""

def simplify(tokens):
    done_anything = True
    while done_anything:
        tokens, _, done_anything = simplify_inner(tokens, 0)

    return tokens

def simplify_inner(tokens, index):
    tokens_new = []
    done_anything = False

    while index < len(tokens):
        if tokens[index] == "(":
            simplified, index, done_anything_temp = simplify_inner(tokens, index + 1)

            if len(simplified) == 1:
                tokens_new.append(simplified[0])
            else:
                if done_anything_temp:
                    done_anything = True

                has_extra_parenthesis = False

                if simplified[0] == "(":
                    has_extra_parenthesis = True

                    inside_parenthesis = 1
                    for token in simplified[1:]:
                        if inside_parenthesis == 0:
                            has_extra_parenthesis = False

                        if token == "(":
                            inside_parenthesis += 1
                        elif token == ")":
                            inside_parenthesis -= 1

                if not has_extra_parenthesis:
                    tokens_new.append("(")
                tokens_new.extend(simplified)
                if not has_extra_parenthesis:
                    tokens_new.append(")")

            index += 1

        elif tokens[index] == ")":
            break
        else:
            tokens_new.append(tokens[index])
            index += 1

    tokens_new, done_anything_temp = simplify_mathematics(tokens_new)
    if done_anything_temp:
        done_anything = True

    return tokens_new, index, done_anything

def simplify_mathematics(tokens_new):
    done_anything = False

    if len(tokens_new) == 3 and is_str_int(tokens_new[0]) and is_math_symbol(tokens_new[1]) and is_str_int(tokens_new[2]):
        first_number = int(tokens_new[0])
        second_number = int(tokens_new[2])
        symbol = tokens_new[1]
        done_anything = True
        match symbol:
            case "+":
                tokens_new = [str(first_number + second_number)]
            case "-":
                tokens_new = [str(first_number - second_number)]
            case "*":
                tokens_new = [str(first_number * second_number)]
            case "/":
                tokens_new = [str(int(first_number / second_number))]
            case "^":
                tokens_new = [str(first_number ** second_number)]
    else:
        removal_patterns = [("*", "1"), ("^", "1")]

        index_temp = 0
        while index_temp < len(tokens_new) - 1:
            for pattern in removal_patterns:
                if tokens_new[index_temp] == pattern[0] and tokens_new[index_temp + 1] == pattern[1]:
                    done_anything = True
                    del tokens_new[index_temp]
                    del tokens_new[index_temp]
                else:
                    index_temp += 1

    return tokens_new, done_anything

if __name__ == "__main__":
    command = sys.argv[1]
    if command == "transform":
        rules = parse_rules(rules)
        expression = " ".join(sys.argv[2:])
        tokens = tokenize(expression)

        applied, tokens = apply(tokens, rules, None)

        if applied and tokens:
            print("".join(tokens))
        else:
            print("Could not make transformation")
    elif command == "simplify":
        if len(sys.argv) > 2:
            expression = " ".join(sys.argv[2:])
        else:
            expression = sys.stdin.readline()[0:-1]

        tokens = tokenize(expression)
        tokens = simplify(tokens)
        print("".join(tokens))

import sys
from enum import Enum

class RuleType(Enum):
    INDIVIDUAL_CONSTANT = 0
    MULTIPLE_CONSTANT = 1
    INDIVIDUAL_VARIABLE = 2
    MULTIPLE_VARIABLE = 3
    INVALID = 4

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
        or character == ']' \
        or character == '{' \
        or character == '}' 

def tokenize(expression):
    expression = expression + " "

    tokens = []
    buffer = ""
    previous_character = None
    is_negative = False

    for index, character in enumerate(expression):
        if is_symbol(character) and (not character == '-' or not previous_character == '(') and (not character == '(' or not expression[index + 1] == '-') and (not character == ')' or not is_negative):
            if buffer:
                tokens.append(buffer)
            tokens.append(character)
            buffer = ""
        elif character == ' ':
            if buffer:
                tokens.append(buffer)
            buffer = ""
        else:
            if character == '(':
                is_negative = True
            elif character == ')':
                is_negative = False

            buffer += character
        previous_character = character

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

mathematical_functions = ["log"]

def get_binding(expression, index, continues):
    if continues:
        multiple_tokens = []
        inside_parenthesis = 1
        while inside_parenthesis > 0 and index < len(expression):
            if expression[index] == "(" or expression[index] == "[":
                inside_parenthesis += 1
            elif expression[index] == ")" or expression[index] == "]":
                inside_parenthesis -= 1

            multiple_tokens.append(expression[index])

            index += 1

        return multiple_tokens[0:-1 if inside_parenthesis == 0 else len(multiple_tokens)], index - (1 if inside_parenthesis == 0 else 0)
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
    elif expression[index] in mathematical_functions:
        binding = []
        while not expression[index] == "[":
            binding.append(expression[index])
            index += 1

        binding.append("[")
        index += 1

        inside_parenthesis = 1
        while inside_parenthesis > 0:
            binding.append(expression[index])

            if expression[index] == "[":
                inside_parenthesis += 1
            elif expression[index] == "]":
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

def is_str_number(string):
    return is_str_int(string) or string == "e" or (string[0] == '(' and is_str_int(string[1:-1]))

def get_int_from_str(string):
    if string[0] == '(':
        return int(string[1:-1])
    else:
        return int(string)

def apply_internals(expression, rules):
    new_expression = []
    index = 0
    while index < len(expression):
        if expression[index] == "evaluate":
            first = get_int_from_str(expression[2])
            second = get_int_from_str(expression[4])
            operation = expression[3]

            result = str(apply_math_operation(operation, first, second))
            if result.startswith("-"):
                result = "(" + result + ")"
            new_expression.append(result)

            index += 6
        elif expression[index] == "complete":
            index += 2
            inside_brackets = 1
            temp_expression = []

            command = expression[index]
            index += 2

            while inside_brackets > 0:
                if expression[index] == "[":
                    inside_brackets += 1
                elif expression[index] == "]":
                    inside_brackets -= 1

                if inside_brackets > 0:
                    temp_expression.append(expression[index])

                index += 1

            index += 2

            temp_expression_cached = []
            while True:
                _, temp_expression = apply(temp_expression, rules, command)

                if temp_expression_cached == temp_expression:
                    break

                temp_expression_cached = temp_expression

            new_expression.extend(temp_expression)
        else:
            new_expression.append(expression[index])
            index += 1

    return new_expression

def apply(expression, rules, command_in):
    command = expression[0]
    valid = True

    expression = apply_internals(expression, rules)

    if command in rules:
        expression_new = []
        index = 0
        while index < len(expression):
            if expression[index] in rules:
                command = expression[index]

                count = 1
                if expression[index + 1] == "^":
                    count = int(expression[index + 2])
                    index += 2

                temp_expression = []
                index += 2
                inside_parenthesis = 1
                while inside_parenthesis > 0:
                    if expression[index] == "[":
                        inside_parenthesis += 1
                    elif expression[index] == "]":
                        inside_parenthesis -= 1

                    temp_expression.append(expression[index])

                    index += 1
                
                temp_expression = temp_expression[0:-1]

                i = 0
                while i < count and valid:
                    valid, temp_expression = apply(temp_expression, rules, command)

                    if temp_expression:
                        temp_expression = apply_internals(temp_expression, rules)
                    i += 1

                expression_new.extend(temp_expression)
            else:
                expression_new.append(expression[index])
                index += 1

        expression = expression_new

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
            elif input in mathematical_functions:
                if expression[expression_index] == input:
                    expression_index += 1
                else:
                    rule_invalid = True
                    break
            elif is_str_number(input):
                if expression[expression_index] == input:
                    expression_index += 1
                else:
                    rule_invalid = True
                    break
            else:
                binding, expression_index = get_binding(expression, expression_index, input.endswith(".."))

                type = None

                if len(binding) == 1:
                    if binding[0][0] == '-':
                        type = RuleType.INVALID
                    else:
                        if is_str_number(binding[0]) or binding[0] == "e":
                            type = RuleType.INDIVIDUAL_CONSTANT
                        else:
                            type = RuleType.INDIVIDUAL_VARIABLE
                else:
                    is_constant = True
                    for token in binding:
                        if not is_str_number(token) and not token == "(" and not token == ")" and not is_symbol(token):
                            is_constant = False
                    
                    if is_constant:
                        type = RuleType.MULTIPLE_CONSTANT
                    else:
                        type = RuleType.MULTIPLE_VARIABLE

                if input.isupper() and (type == RuleType.INDIVIDUAL_VARIABLE or type == RuleType.MULTIPLE_VARIABLE):
                    rule_invalid = True
                    break
                elif input.isupper() and len(input) == 1 and not type == RuleType.INDIVIDUAL_CONSTANT:
                    rule_invalid = True
                    break
                elif input.islower() and not (type == RuleType.INDIVIDUAL_VARIABLE or type == RuleType.MULTIPLE_VARIABLE):
                    rule_invalid = True
                    break
                elif input.islower() and len(input) == 1 and type == RuleType.MULTIPLE_VARIABLE:
                    rule_invalid = True
                    break
                elif type == RuleType.INVALID:
                    rule_invalid = True
                    break

                if input in bindings and not bindings[input] == binding:
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

                    if applied_bindings[index + 1] == "^":
                        cached_expression.append(applied_bindings[index + 2])
                        cached_expression.append(applied_bindings[index + 3])
                        index += 2

                    index += 2

                    inside_parenthesis = 1
                    while inside_parenthesis > 0:
                        if applied_bindings[index] == "[":
                            inside_parenthesis += 1
                        elif applied_bindings[index] == "]":
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

def apply_math_operation(operation, first, second):
    match operation:
        case "+":
            return first + second
        case "-":
            return first - second
        case "*":
            return first * second
        case "/":
            return int(first / second)
        case "^":
            return first ** second

if __name__ == "__main__":
    rules_file = sys.argv[1]
    rules = parse_rules(open(rules_file).read())
    expression = " ".join(sys.argv[2:])
    tokens = tokenize(expression)

    applied, tokens = apply(tokens, rules, None)

    if applied and tokens:
        print("".join(tokens))
    else:
        print("Could not make transformation")

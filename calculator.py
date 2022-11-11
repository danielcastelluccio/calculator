import sys

def is_symbol(character):
    return character == '*' \
        or character == '/' \
        or character == '-' \
        or character == '+' \
        or character == '^' \
        or character == '(' \
        or character == ')'

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
            if expression[index] == "(":
                inside_parenthesis += 1
            elif expression[index] == ")":
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

def apply(expression, rules):
    command = expression[0]
    if command in rules:
        return apply_rule(expression[2:-1], rules, command)
    return False, None

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
                if input.isupper() and not (len(binding) == 1 and is_str_int(binding[0])):
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

                    applied, applied_result = apply(cached_expression, rules)
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
derivative A*b^C => A*C*b^(C-1)
derivative a^B => B*a^(B-1)
derivative A*b => A
derivative b => 1
derivative A => 0
derivative Aa*Bb => Aa*derivative(Bb)+Bb*derivative(Aa)
derivative Aa/Bb => (Bb*derivative(Aa)-Aa*derivative(Bb))/Bb^2
"""

if __name__ == "__main__":
    rules = parse_rules(rules)
    expression = " ".join(sys.argv[1:])
    tokens = tokenize(expression)

    applied, tokens = apply(tokens, rules)

    if applied and tokens:
        print("".join(tokens))
    else:
        print("Could not take command")

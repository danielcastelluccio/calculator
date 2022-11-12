# Calculator

Probably the strangest calculator you have ever seen. In reality this 'calculator' is little more than macros that are used to apply transformations to an expression. The inspiration came for this from calculus, where finding the derivative of an expression is usually just using a specific formula which I thought would be fun to implement.

Currently the two main supported features are derivatives and expression simplification. Integrals would also be something that is logical to support, along with other various things.

Rules are provided in a file passed in through the command line.

## Example Usage:
```
python calculator.py rules.rule derivative[x^2]
// Output: 2*(x^(2-1))
```
In this case the output expression is not simplified whatsoever, so usually I would apply the 'simplify' rule after taking a derivative.
```
python calculator.py rules.rules simplify[derivative[x^2]]
// Output: 2*(x^(1))
```
The output has been partially simplified, however there are still many more simplifications to do. These can be done by calling simplify again on the result. This would get quite repetitive so we have a special syntax for running a transformation multiple times!
```
python calculator.py rules.rule simplify^4[derivative[x^2]]
// Output: 2*x
```
Now the output is finally completely simplified!

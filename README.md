PICL → PIC16 compiler ([BlackBox](http://www.oberon.ch/blackbox.html) subsystem), based on N. Wirth [PICL](http://people.inf.ethz.ch/wirth/PICL/index.html) compiler

Only PIC16F177{3,6,8} is currently supported and tested

Features:
* memory banks switching implemented
* bit access indices may be named numeric constants
* SLEEP, CLRWDT and RESET commands added
* "*" operator added for integer operands (addition with carry)
* "/" operator added for integer operands (substraction with borrow)

Subsystems:
* [Pic](Pic): compiler
* [Pobx](Pobx): examples

Alexander V. Shiryaev, 2019

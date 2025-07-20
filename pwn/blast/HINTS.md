# Hints

If they haven't found the bug yet:

- How are arrays in Fortran indexed? Keep in mind Fortran was designed for
  numerical and scientific computing, where conventions may differ from usual
  software conventions.
  
If they've found the bug, but don't know how to leverage it

- The `MATVECMUL` subroutine performs matrix vector multiplication. Using a
  little bit of math, you can apply it in one direction to get an out of bounds
  read, or apply it in the opposite direction to get an out of bounds write.
  
If they've gained initial control of the instruction pointer but don't know
where to go from there

- The write you get is quite small. Usually when one only has limited space for
  ROP, one can use [stack pivots]
  (https://ir0nstone.gitbook.io/notes/binexp/stack/stack-pivoting) to move the
  stack frame to another location and gain more space.
  
  Do you see anywhere you can move the stack frame which would be advantageous
  to reading the flag?



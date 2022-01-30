import qsharp
from Qrng import QuantumRandomNumberGenerator 

def qrng(max):
  output = max + 1 
  while output > max:
      # Initialize a list to store the bits that will define the random integer
      bit_string = [] 
      # Call the quantum operation as many times as there are bits
      for i in range(0, max.bit_length()):  
          # Call the quantum operation and store the random bit in the list
          bit_string.append(QuantumRandomNumberGenerator.simulate()) 
      # Transform bit string to integer
      output = int("".join(str(x) for x in bit_string), 2) 
  return output
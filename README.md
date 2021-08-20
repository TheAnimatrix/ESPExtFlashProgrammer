

# ESPExtFlashProgrammer

Use your PC coupled with an arduino compatible microcontroller to program an external spi flash module!

*File transfer from PC to MCU takes place over a Serial connection.*

Tested with the following devices
---------------------------------
NodeMCU V2.0 (ESP 12-E)

Depenencies:
------------
1. Arduino Framework
2. [SPIMemory library](https://github.com/Marzogh/SPIMemory) for Arduino ([https://github.com/Marzogh/SPIMemory](https://github.com/Marzogh/SPIMemory))
3. Python3

Steps:
-------
1. Replace `SS` in line 3 of main.cpp `#DEFINE SSP SS` with Chip Select pin of your choice 
2. Flash `main.cpp` to your microcontroller of choice.
3. Keep your microcontroller connected to your PC
4. Run `write_flash.py` with python3
   ex:
>         python3 write_flash.py
>         python write_flash.py

Script Arguements
-------------------

> **--file=<file_name> (Required)**

        Specify the path of the file you want to flash to your external flash module

> **--port=<port_name> (Optional)**

        Specifying this can remove the step where the script asks you to choose your port from a list

> **--offset=<offset_in_hex> (Optional, defaults to 0x0)**

        Specify the address where you want your file to be flashed    

> **-f (force) (Optional)**

        Skip some confirmation messages

CAVEATS
------
1. This is constantly evolving.
   Use this at your own discretion.
2. Erases the entire chip before writing specified contents 
   (feel free to fork and tweak this)


LICENSE
-------
Copyright 2021 TheAnimatrix

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

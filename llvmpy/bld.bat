set LLVMPY_DYNLINK=0
set INCLUDE=%LIBRARY_INC%
set LIBPATH=%LIBRARY_LIB%
set LIB=%LIBRARY_LIB%
:: Python 2.x uses the LLVM build from conda
if %CONDA_PY% EQU 27  goto INSTALL
if %CONDA_PY% EQU 26  goto INSTALL
:: Use Our custom LLVM build for python 3
set LLVM_TBLGEN_PATH=%HOMEPATH%\dev\llvm-3.3\bin
:INSTALL
%PYTHON% setup.py install
if errorlevel 1 exit 1

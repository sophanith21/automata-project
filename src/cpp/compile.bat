@echo off
echo Compiling FA Processor with MySQL support...

REM You may need to adjust these paths based on your MySQL installation
set MYSQL_INCLUDE_DIR=C:\Program Files\MySQL\MySQL Server 8.0\include
set MYSQL_LIB_DIR=C:\Program Files\MySQL\MySQL Server 8.0\lib

REM Compile with MySQL support
g++ -std=c++17 -I"%MYSQL_INCLUDE_DIR%" -L"%MYSQL_LIB_DIR%" ^
    -o fa_processor.exe fa_processor.cpp ^
    -lmysqlclient -lws2_32 -ladvapi32

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful! fa_processor.exe created.
) else (
    echo Compilation failed! Please check your MySQL installation and paths.
)

pause 
# Automata Processor

Automata Processor is an application that allows you to: 
- Define Finite Automata and save them to your database
- Test input strings of the automata
- Convert NFA into DFA
- Minimize the DFA to reduce redundant states


## Installation
To run the application, you need some requirements:
- Have a Python interpreter with the latest version if possible
- Have a database named automatadb and run the SQL script in automata-project/src/database/automatadb.sql to create the necessary tables (Note: the script is for MySQL DBMS)
- Have a C++ compiler

Instructions to install the necessary modules for Python
```bash
pip install kivy
pip install mysql-connector-python
```

Instruction to compile the C++ file on Window: (Make sure your current directory is at automata-project/src/cpp)
```bash
g++ -I ../../json-develop/include fa_processor.cpp -o fa_proccessor
g++ -I ../../json-develop/include check_fa_type.cpp -o check_fa_type
```

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

Clone the repository
```bash
git clone https://github.com/sophanith21/automata-project.git
```

Instructions to install the necessary modules for Python
```bash
pip install kivy
pip install mysql-connector-python
```

Instructions to compile the C++ file on Windows: (Make sure your current directory is at automata-project/src/cpp)
```bash
g++ -I ../../json-develop/include fa_processor.cpp -o fa_proccessor
g++ -I ../../json-develop/include check_fa_type.cpp -o check_fa_type
```

Now with everything done, you can run the code in "automata-project/GUI/main.py"

# Database Integration for Finite Automata

This document explains how to use the MySQL database integration for storing and managing finite automata.

## Database Schema

The database uses 4 main tables to store finite automata:

### 1. `fa_headers` - Main automaton information
```sql
CREATE TABLE fa_headers(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(10) NOT NULL,           -- "DFA" or "NFA"
    start_state_name VARCHAR(255) NOT NULL,
    description TEXT
);
```

### 2. `fa_states` - Individual states
```sql
CREATE TABLE fa_states(
    id INT PRIMARY KEY AUTO_INCREMENT,
    fa_id INT NOT NULL,                  -- Foreign key to fa_headers
    name VARCHAR(255) NOT NULL,          -- State name like "q0", "A"
    is_accepting BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(fa_id, name),
    FOREIGN KEY (fa_id) REFERENCES fa_headers(id)
);
```

### 3. `fa_symbols` - Alphabet symbols
```sql
CREATE TABLE fa_symbols(
    id INT PRIMARY KEY AUTO_INCREMENT,
    fa_id INT NOT NULL,                  -- Foreign key to fa_headers
    symbol_char VARCHAR(50) NOT NULL,    -- Symbols like "a", "b", "ep" (epsilon)
    UNIQUE(fa_id, symbol_char)
);
```

### 4. `fa_transitons` - Transitions
```sql
CREATE TABLE fa_transitons(
    id INT PRIMARY KEY AUTO_INCREMENT,
    fa_id INT NOT NULL,                  -- Foreign key to fa_headers
    from_state_name VARCHAR(255) NOT NULL,
    symbol_char VARCHAR(50) NOT NULL,
    to_state_name VARCHAR(255) NOT NULL,
    UNIQUE(fa_id, from_state_name, symbol_char, to_state_name)
);
```

## Setup Instructions

### 1. Install MySQL
- Download and install MySQL Server (8.0 or later recommended)
- Make sure MySQL service is running

### 2. Install MySQL C++ Connector
- Download MySQL C++ Connector from MySQL website
- Extract to a known location
- Update the paths in `compile.bat` if needed

### 3. Install Python MySQL Connector
```bash
pip install mysql-connector-python
```

### 4. Set up the Database
```bash
cd src/database
python setup_database.py
```

### 5. Compile the C++ Program
```bash
cd src/cpp
compile.bat
```

## Usage Examples

### 1. Save an Automaton to Database

**Input JSON:**
```json
{
    "name": "MyDFA",
    "type": "DFA",
    "start_state": "q0",
    "states": [
        {"name": "q0", "is_accepting": true},
        {"name": "q1", "is_accepting": false}
    ],
    "alphabet": ["a", "b"],
    "transitions": [
        {"from": "q0", "symbol": "a", "to": ["q1"]},
        {"from": "q0", "symbol": "b", "to": ["q0"]},
        {"from": "q1", "symbol": "a", "to": ["q0"]},
        {"from": "q1", "symbol": "b", "to": ["q1"]}
    ],
    "saveToDB": true,
    "dbHost": "localhost",
    "dbUser": "root",
    "dbPassword": "",
    "dbDatabase": "automatadb",
    "dbPort": 3306
}
```

**Command:**
```bash
echo '{"name":"MyDFA",...}' | fa_processor.exe
```

### 2. List All Automata in Database

**Input JSON:**
```json
{
    "listDB": true,
    "dbHost": "localhost",
    "dbUser": "root",
    "dbPassword": "",
    "dbDatabase": "automatadb",
    "dbPort": 3306
}
```

**Output:**
```json
{
    "status": "success",
    "automata_in_database": ["MyDFA", "TestDFA"]
}
```

### 3. Load an Automaton from Database

**Input JSON:**
```json
{
    "loadFromDB": true,
    "dbAutomatonName": "MyDFA",
    "dbHost": "localhost",
    "dbUser": "root",
    "dbPassword": "",
    "dbDatabase": "automatadb",
    "dbPort": 3306,
    "toConvertNFA": false,
    "toTestInput": true,
    "toMinimize": true
}
```

### 4. Complete Workflow Example

**Save, Minimize, and Test:**
```json
{
    "name": "ComplexDFA",
    "type": "DFA",
    "start_state": "q0",
    "states": [
        {"name": "q0", "is_accepting": true},
        {"name": "q1", "is_accepting": false},
        {"name": "q2", "is_accepting": true},
        {"name": "q3", "is_accepting": false}
    ],
    "alphabet": ["a", "b"],
    "transitions": [
        {"from": "q0", "symbol": "a", "to": ["q1"]},
        {"from": "q0", "symbol": "b", "to": ["q2"]},
        {"from": "q1", "symbol": "a", "to": ["q0"]},
        {"from": "q1", "symbol": "b", "to": ["q3"]},
        {"from": "q2", "symbol": "a", "to": ["q3"]},
        {"from": "q2", "symbol": "b", "to": ["q0"]},
        {"from": "q3", "symbol": "a", "to": ["q2"]},
        {"from": "q3", "symbol": "b", "to": ["q1"]}
    ],
    "toConvertNFA": false,
    "toTestInput": true,
    "toMinimize": true,
    "saveToDB": true,
    "dbHost": "localhost",
    "dbUser": "root",
    "dbPassword": "",
    "dbDatabase": "automatadb",
    "dbPort": 3306
}
```

## Data Flow Explanation

### 1. JSON Input → C++ Data Structures
```cpp
// JSON parsing
std::vector<FAState> states = json_data.at("states").get<std::vector<FAState>>();
std::vector<FATransition> transitions = json_data.at("transitions").get<std::vector<FATransition>>();

// Data placement
FiniteAutomaton fa(name, type, start_state, states, alphabet, transitions);
```

### 2. C++ → Database
```cpp
// Save to database
fa.saveToDatabase(db);

// This creates:
// 1. Entry in fa_headers
// 2. Multiple entries in fa_states
// 3. Multiple entries in fa_symbols
// 4. Multiple entries in fa_transitons
```

### 3. Database → C++
```cpp
// Load from database
auto fa = FiniteAutomaton::loadFromDatabase(db, "MyDFA");

// This reconstructs:
// 1. FAState objects from fa_states table
// 2. Alphabet from fa_symbols table
// 3. FATransition objects from fa_transitons table
```

## Separating Accepting and Non-Accepting States

The system automatically separates accepting and non-accepting states:

### In C++:
```cpp
std::vector<std::string> accepting_states, non_accepting_states;
for (const auto& s : original_fa.getStates()) {
    if (s.is_accepting) accepting_states.push_back(s.name);
    else non_accepting_states.push_back(s.name);
}
```

### In Database:
```sql
-- Get accepting states
SELECT name FROM fa_states WHERE fa_id = ? AND is_accepting = 1;

-- Get non-accepting states
SELECT name FROM fa_states WHERE fa_id = ? AND is_accepting = 0;
```

### In JSON Output:
```json
{
    "accepting_states": ["q0", "q2"],
    "non_accepting_states": ["q1", "q3"]
}
```

## Error Handling

The system includes comprehensive error handling:

1. **Database Connection Errors**: Check MySQL service and credentials
2. **SQL Errors**: Check table structure and data integrity
3. **JSON Parsing Errors**: Validate input format
4. **Automaton Validation**: Ensure consistent state references

## Performance Considerations

1. **Indexes**: The database schema includes appropriate unique constraints
2. **Batch Operations**: Multiple transitions are inserted efficiently
3. **Memory Management**: Proper cleanup of MySQL result sets
4. **Connection Pooling**: Single connection per operation

## Troubleshooting

### Common Issues:

1. **Compilation Errors**: Check MySQL library paths in `compile.bat`
2. **Connection Errors**: Verify MySQL service is running
3. **Permission Errors**: Check database user privileges
4. **Data Integrity**: Ensure all referenced states exist

### Debug Mode:
The C++ program outputs debug information to stderr, which can help identify issues.

## Future Enhancements

1. **Connection Pooling**: For high-performance applications
2. **Transaction Support**: For atomic operations
3. **Versioning**: Track automaton versions
4. **Search/Filter**: Query automata by properties
5. **Export Formats**: Support for other formats (XML, YAML) 
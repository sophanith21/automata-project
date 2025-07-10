#!/usr/bin/env python3
"""
Database setup and management script for Finite Automata project.
This script helps set up the MySQL database and provides examples of usage.
"""

import mysql.connector
import json
import subprocess
import sys
import os

def setup_database():
    """Set up the MySQL database with the required tables."""
    try:
        # Connect to MySQL (adjust credentials as needed)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Add your password here
            autocommit=True
        )
        
        cursor = connection.cursor()
        
        # Read and execute the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), "automatadb.sql")
        with open(sql_file_path, 'r') as file:
            sql_commands = file.read()
        
        # Split and execute commands
        for command in sql_commands.split(';'):
            if command.strip():
                cursor.execute(command)
        
        print("Database setup completed successfully!")
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database setup failed: {err}")
        return False
    
    return True

def test_database_integration():
    """Test the database integration with a sample automaton."""
    
    # Sample DFA for testing
    sample_dfa = {
        "name": "TestDFA",
        "type": "DFA",
        "start_state": "q0",
        "states": [
            {"name": "q0", "is_accepting": True},
            {"name": "q1", "is_accepting": False},
            {"name": "q2", "is_accepting": True}
        ],
        "alphabet": ["a", "b"],
        "transitions": [
            {"from": "q0", "symbol": "a", "to": ["q1"]},
            {"from": "q0", "symbol": "b", "to": ["q2"]},
            {"from": "q1", "symbol": "a", "to": ["q0"]},
            {"from": "q1", "symbol": "b", "to": ["q1"]},
            {"from": "q2", "symbol": "a", "to": ["q2"]},
            {"from": "q2", "symbol": "b", "to": ["q0"]}
        ],
        "toConvertNFA": False,
        "toTestInput": True,
        "toMinimize": True,
        "saveToDB": True,
        "dbHost": "localhost",
        "dbUser": "root",
        "dbPassword": "",
        "dbDatabase": "automatadb",
        "dbPort": 3306
    }
    
    # Convert to JSON string
    json_input = json.dumps(sample_dfa)
    
    try:
        # Run the C++ program
        cpp_path = os.path.join(os.path.dirname(__file__), "..", "cpp", "fa_processor.exe")
        result = subprocess.run([cpp_path], input=json_input, text=True, capture_output=True)
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            print("✅ Database integration test successful!")
            print(f"Status: {output.get('status')}")
            print(f"Database message: {output.get('database_message')}")
            
            if 'minimized_dfa' in output:
                print(f"Minimized DFA has {len(output['minimized_dfa']['states'])} states")
            
            return True
        else:
            print("❌ Database integration test failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def list_automata_in_database():
    """List all automata stored in the database."""
    
    list_request = {
        "listDB": True,
        "dbHost": "localhost",
        "dbUser": "root",
        "dbPassword": "",
        "dbDatabase": "automatadb",
        "dbPort": 3306
    }
    
    json_input = json.dumps(list_request)
    
    try:
        cpp_path = os.path.join(os.path.dirname(__file__), "..", "cpp", "fa_processor.exe")
        result = subprocess.run([cpp_path], input=json_input, text=True, capture_output=True)
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            automata = output.get('automata_in_database', [])
            
            if automata:
                print("📋 Automata in database:")
                for i, name in enumerate(automata, 1):
                    print(f"  {i}. {name}")
            else:
                print("📋 No automata found in database.")
            
            return True
        else:
            print(f"❌ Failed to list automata: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ List operation failed: {e}")
        return False

def load_automaton_from_database(name):
    """Load a specific automaton from the database."""
    
    load_request = {
        "loadFromDB": True,
        "dbAutomatonName": name,
        "dbHost": "localhost",
        "dbUser": "root",
        "dbPassword": "",
        "dbDatabase": "automatadb",
        "dbPort": 3306,
        "toConvertNFA": False,
        "toTestInput": False,
        "toMinimize": False
    }
    
    json_input = json.dumps(load_request)
    
    try:
        cpp_path = os.path.join(os.path.dirname(__file__), "..", "cpp", "fa_processor.exe")
        result = subprocess.run([cpp_path], input=json_input, text=True, capture_output=True)
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            print(f"✅ Successfully loaded automaton '{name}' from database")
            print(f"Type: {output.get('original_fa_type')}")
            print(f"States: {len(output.get('accepting_states', [])) + len(output.get('non_accepting_states', []))}")
            return True
        else:
            print(f"❌ Failed to load automaton: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Load operation failed: {e}")
        return False

def main():
    """Main function to run database operations."""
    print("🔧 Finite Automata Database Management")
    print("=" * 40)
    
    # Check if MySQL is available
    try:
        mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        print("✅ MySQL connection successful")
    except mysql.connector.Error as err:
        print(f"❌ MySQL connection failed: {err}")
        print("Please make sure MySQL is running and accessible.")
        return
    
    # Setup database
    print("\n📊 Setting up database...")
    if not setup_database():
        return
    
    # Test integration
    print("\n🧪 Testing database integration...")
    if not test_database_integration():
        return
    
    # List automata
    print("\n📋 Listing automata in database...")
    list_automata_in_database()
    
    # Load automaton (if any exist)
    print("\n📥 Loading automaton from database...")
    load_automaton_from_database("TestDFA")
    
    print("\n✅ All operations completed successfully!")

if __name__ == "__main__":
    main() 
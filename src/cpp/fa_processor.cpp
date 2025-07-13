#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <nlohmann/json.hpp>
#include <queue>     // For BFS in epsilon closure
#include <algorithm> // For remove, sort, etc.
#include <sstream>   // For building DFA state names
#include <optional>  // For optional return types (C++17)
using namespace std;
// Define a constant for our epsilon symbol, consistent with Python
const string EPSILON_SYMBOL = "ep";

// --- C++ Data Structures ---

struct FAState
{
    string name;
    bool is_accepting;

    // Helper for debugging/printing
    string toString() const
    {
        return name + (is_accepting ? "*" : "");
    }

    // For using FAState directly in sets/maps if ever needed
    bool operator<(const FAState &other) const
    {
        return name < other.name; // Comparison based on name
    }
    bool operator==(const FAState &other) const
    {
        return name == other.name; // Equality based on name
    }
};

struct FATransition
{
    string from_state;
    string symbol;
    string to_state; // Using set for unique to_states (NFA)
};

// --- Helper functions for nlohmann/json serialization/deserialization ---
// These functions must be defined before they are used (e.g., in main)
// by nlohmann::json::get<T>() or nlohmann::json(T)
void from_json(const nlohmann::json &j, FAState &s)
{
    j.at("name").get_to(s.name);
    int temp = j.at("is_accepting").get<int>();
    s.is_accepting = (temp != 0);
}

void from_json(const nlohmann::json &j, FATransition &t)
{
    j.at("from_state_name").get_to(t.from_state);
    j.at("symbol_char").get_to(t.symbol);
    j.at("to_state_name").get_to(t.to_state);
}

void to_json(nlohmann::json &j, const FAState &s)
{
    j = nlohmann::json{{"name", s.name}, {"is_accepting", s.is_accepting}};
}

void to_json(nlohmann::json &j, const FATransition &t)
{
    j = nlohmann::json{{"from_state_name", t.from_state}, {"symbol_char", t.symbol}, {"to_state_name", t.to_state}};
}

// --- FiniteAutomaton Class Definition (all in one file) ---

class FiniteAutomaton
{
public:
    // Constructors
    FiniteAutomaton() : name_("Unnamed_FA"), type_("NFA"), start_state_("") {} // Default constructor

    // Main constructor for building from parsed data
    FiniteAutomaton(const string &name, const string &type,
                    const string &start_state, const vector<FAState> &states,
                    const vector<string> &alphabet,
                    const vector<FATransition> &raw_transitions)
        : name_(name), type_(type), start_state_(start_state), states_(states),
          alphabet_(alphabet), raw_transitions_list_(raw_transitions)
    {
        buildTransitionsMap(); // Populate the map on construction
    }

    // Public methods for FA operations
    bool testInput(const string &input_string) const;

    // NFA to DFA Conversion Method
    // Returns a new FiniteAutomaton object representing the converted DFA
    optional<FiniteAutomaton> convertNfaToDfa() const;
    void parsedSetOfStatesToState();

    // Getter methods for accessing private members
    const string &getName() const { return name_; }
    const string &getType() const { return type_; }
    const string &getStartState() const { return start_state_; }
    const vector<FAState> &getStates() const { return states_; }
    const vector<string> &getAlphabet() const { return alphabet_; }
    const map<pair<string, string>, set<string>> &getTransitionsMap() const { return transitions_map_; }
    const vector<FATransition> &getRawTransitionsList() const { return raw_transitions_list_; }

    // Helper for debugging/printing
    void printDefinition() const;

private:
    string name_;
    string type_; // "DFA" or "NFA"
    string start_state_;
    vector<FAState> states_;
    vector<string> alphabet_; // List of symbols

    // A map for efficient transition lookup
    map<pair<string, string>, set<string>> transitions_map_;

    // Original list of transitions (useful for maintaining original structure)
    vector<FATransition> raw_transitions_list_;

    // Private helper methods for internal class logic
    void buildTransitionsMap();                            // Populates transitions_map_ from raw_transitions_list_
    bool isAcceptingState(const string &state_name) const; // Checks if a given state is accepting

    // Helper functions for NFA to DFA conversion (private as they are internal to the algorithm)
    set<string> getEpsilonClosure(const set<string> &nfa_states) const;
    set<string> move(const set<string> &nfa_states, const string &symbol) const;
    bool containsAcceptingStateForSet(const set<string> &nfa_states) const; // Checks if any NFA state in a set is accepting
    string createDfaStateName(const set<string> &nfa_states) const;
};

// --- FiniteAutomaton Class Method Implementations ---

void FiniteAutomaton::buildTransitionsMap()
{
    transitions_map_.clear();
    for (const auto &trans : raw_transitions_list_)
    {
        transitions_map_[{trans.from_state, trans.symbol}].insert(
            trans.to_state);
    }
}

bool FiniteAutomaton::isAcceptingState(const string &state_name) const
{
    for (const auto &state : states_)
    {
        if (state.name == state_name)
        {
            return state.is_accepting;
        }
    }
    return false; // State not found
}

bool FiniteAutomaton::testInput(const string &input_string) const
{
    if (type_ != "DFA")
    {
        cerr << "Warning: testInput is currently only accurate for DFA type. "
             << "This automaton is of type " << type_ << "." << endl;
        return false; // Indicate not implemented for NFA behavior
    }

    string current_state = start_state_;
    for (char symbol_char : input_string)
    {
        string symbol(1, symbol_char); // Convert char to string
        auto it = transitions_map_.find({current_state, symbol});
        if (it == transitions_map_.end() || it->second.empty())
        {
            return false; // No transition or dead end
        }
        // For DFA, there should be exactly one next state
        current_state = *it->second.begin();
    }
    return isAcceptingState(current_state);
}

void FiniteAutomaton::printDefinition() const
{
    cerr << "Automaton Name: " << name_ << endl;
    cerr << "Type: " << type_ << endl;
    cerr << "Start State: " << start_state_ << endl;
    cerr << "States: ";
    for (const auto &state : states_)
    {
        cerr << state.toString() << " ";
    }
    cerr << endl;
    cerr << "Alphabet: ";
    for (const auto &symbol : alphabet_)
    {
        cerr << symbol << " ";
    }
    cerr << endl;
    cerr << "Transitions:" << endl;
    for (const auto &pair : transitions_map_)
    {
        cerr << "   (" << pair.first.first << ", " << pair.first.second << ") -> {";
        bool first = true;
        for (const auto &to_state : pair.second)
        {
            if (!first)
                cerr << ", ";
            cerr << to_state;
            first = false;
        }
        cerr << "}" << endl;
    }
}

// --- NFA to DFA Helper Functions Implementations (within the class) ---

set<string> FiniteAutomaton::getEpsilonClosure(const set<string> &nfa_states) const
{
    set<string> closure = nfa_states;
    queue<string> q;

    for (const string &state : nfa_states)
    {
        q.push(state);
    }

    while (!q.empty())
    {
        string current_state = q.front();
        q.pop();

        auto it = transitions_map_.find({current_state, EPSILON_SYMBOL});
        if (it != transitions_map_.end())
        {
            for (const string &next_state : it->second)
            {
                if (closure.find(next_state) == closure.end())
                {
                    closure.insert(next_state);
                    q.push(next_state);
                }
            }
        }
    }
    return closure;
}

set<string> FiniteAutomaton::move(const set<string> &nfa_states, const string &symbol) const
{
    set<string> reachable_states;
    for (const string &state : nfa_states)
    {
        auto it = transitions_map_.find({state, symbol});
        if (it != transitions_map_.end())
        {
            reachable_states.insert(it->second.begin(), it->second.end());
        }
    }
    return reachable_states;
}

bool FiniteAutomaton::containsAcceptingStateForSet(const set<string> &nfa_states) const
{
    for (const string &nfa_state_name : nfa_states)
    {
        if (isAcceptingState(nfa_state_name))
        { // Reusing the private helper
            return true;
        }
    }
    return false;
}

string FiniteAutomaton::createDfaStateName(const set<string> &nfa_states) const
{
    if (nfa_states.empty())
    {
        return "{}";
    }
    ostringstream oss;
    oss << "{";
    bool first = true;
    for (const string &state : nfa_states)
    {
        if (!first)
        {
            oss << ",";
        }
        oss << state;
        first = false;
    }
    oss << "}";
    return oss.str();
}
void FiniteAutomaton::parsedSetOfStatesToState()
{
    map<string, string> SetStateToState;
    int iterator = 0;
    for (FAState& state : states_)
    {

        if (state.name != "Dead")
        {
            char char_val = static_cast<char>(iterator + 'A');
            SetStateToState[state.name] = string(1, char_val);
            state.name = string(1, char_val);
            iterator++;
        }
        else
        {
            SetStateToState["Dead"] = "Dead";
        }
    }

    for (FATransition &transition : raw_transitions_list_)
    {
        transition.from_state = SetStateToState.at(transition.from_state);
        transition.to_state = SetStateToState.at(transition.to_state);
    }
    start_state_ = SetStateToState.at(start_state_);
}

// --- Main NFA to DFA Conversion Algorithm (Subset Construction) ---
optional<FiniteAutomaton> FiniteAutomaton::convertNfaToDfa() const
{
    if (type_ == "DFA")
    {
        cerr << "Warning: This automaton is already a DFA. No conversion performed." << endl;
        return *this; // Return a copy of itself
    }

    string new_fa_name = name_ + "_DFA";
    string new_fa_type = "DFA";
    vector<string> dfa_alphabet = alphabet_;

    // Remove EPSILON_SYMBOL from DFA alphabet if it was present
    dfa_alphabet.erase(remove(dfa_alphabet.begin(), dfa_alphabet.end(), EPSILON_SYMBOL), dfa_alphabet.end());

    vector<FAState> dfa_states;
    vector<FATransition> dfa_raw_transitions;

    map<set<string>, string> dfa_state_names; // Maps NFA state sets to DFA state names
    queue<set<string>> unprocessed_dfa_states_q;

    // 1. Initial DFA state: Epsilon closure of the NFA's start state
    set<string> initial_nfa_states_set = {start_state_};
    set<string> dfa_start_set = getEpsilonClosure(initial_nfa_states_set);

    if (dfa_start_set.empty())
    {
        cerr << "Error: NFA start state has an empty epsilon closure. Cannot convert to DFA." << endl;
        return nullopt;
    }

    string dfa_start_state_name = createDfaStateName(dfa_start_set);

    dfa_state_names[dfa_start_set] = dfa_start_state_name; // Perform insertion of the {dfa_start_set, dfa_start_state_name} into the map
    unprocessed_dfa_states_q.push(dfa_start_set);

    // Add initial DFA state
    dfa_states.push_back({dfa_start_state_name,
                          containsAcceptingStateForSet(dfa_start_set)});

    // 2. Process states from the queue
    while (!unprocessed_dfa_states_q.empty())
    {
        set<string> current_dfa_set = unprocessed_dfa_states_q.front();
        unprocessed_dfa_states_q.pop();

        string current_dfa_name = dfa_state_names[current_dfa_set];

        for (const string &symbol : dfa_alphabet)
        {
            set<string> moved_nfa_states = move(current_dfa_set, symbol);
            set<string> next_dfa_set = getEpsilonClosure(moved_nfa_states);

            string next_dfa_state_name;

            if (next_dfa_set.empty())
            {
                // If it leads to the empty set, it goes to the Dead state
                next_dfa_state_name = "Dead";
                if (dfa_state_names.find(next_dfa_set) == dfa_state_names.end())
                {
                    // Only discover the 'Dead' state once
                    dfa_state_names[next_dfa_set] = next_dfa_state_name;
                    dfa_states.push_back({
                        next_dfa_state_name,
                        false // Dead state is never accepting
                    });
                    // Push the empty set onto the queue so its transitions (self-loops) are processed
                    unprocessed_dfa_states_q.push(next_dfa_set);
                }
            }
            else
            {
                // This is a regular, non-empty DFA state
                if (dfa_state_names.find(next_dfa_set) == dfa_state_names.end())
                {
                    // New DFA state discovered
                    next_dfa_state_name = createDfaStateName(next_dfa_set);
                    dfa_state_names[next_dfa_set] = next_dfa_state_name;

                    dfa_states.push_back({next_dfa_state_name,
                                          containsAcceptingStateForSet(next_dfa_set)});
                    unprocessed_dfa_states_q.push(next_dfa_set); // Add to queue for processing
                }
                else
                {
                    // Existing DFA state
                    next_dfa_state_name = dfa_state_names[next_dfa_set];
                }
            }

            FATransition new_transition;
            new_transition.from_state = current_dfa_name;
            new_transition.symbol = symbol;
            new_transition.to_state = (next_dfa_state_name); // DFA transitions to a single state
            dfa_raw_transitions.push_back(new_transition);
        }
    }
    FiniteAutomaton newDFA = FiniteAutomaton(new_fa_name, new_fa_type, dfa_start_state_name,
                                             dfa_states, dfa_alphabet, dfa_raw_transitions);
    newDFA.parsedSetOfStatesToState();

    // Create and return the new DFA object
    return newDFA;
}

// --- General Utility Functions (for stdin/stdout JSON) ---

string readStdinToString()
{
    string json_input_str;
    string line;
    while (getline(cin, line))
    {
        json_input_str += line;
    }
    return json_input_str;
}

nlohmann::json createErrorJson(const string &message, const string &details = "")
{
    nlohmann::json error_output;
    error_output["status"] = "error";
    error_output["message"] = message;
    if (!details.empty())
    {
        error_output["details"] = details;
    }
    return error_output;
}

// --- Function to create FiniteAutomaton from parsed JSON ---
// This could be a static factory method of FiniteAutomaton if preferred,
// but for a single-file setup, a free function is fine.
optional<FiniteAutomaton> createAutomatonFromJson(const nlohmann::json &json_data)
{
    try
    {
        string name = json_data.at("fa_header").at(0).at("name").get<string>();
        string type = json_data.at("fa_header").at(0).at("type").get<string>();
        string start_state = json_data.at("fa_header").at(0).at("start_state_name").get<string>();

        // Use nlohmann/json's get<>() with our custom from_json overloads
        vector<FAState> states = json_data.at("fa_states").get<vector<FAState>>();
        vector<string> alphabet;
        for (const auto &symbol_obj : json_data.at("fa_symbols"))
        {
            alphabet.push_back(symbol_obj.at("symbol_char").get<string>());
        }
        vector<FATransition> raw_transitions = json_data.at("fa_transitions").get<vector<FATransition>>();

        return FiniteAutomaton(name, type, start_state, states, alphabet, raw_transitions);
    }
    catch (const nlohmann::json::exception &e)
    {
        cerr << "Error parsing automaton JSON structure: " << e.what() << endl;
        return nullopt;
    }
}

// --- Main Program Logic ---

int main()
{
    // Read the entire JSON input from stdin
    string json_input_str = readStdinToString();
    bool toConvertNFA = false;
    bool toTestInput = false;
    bool toMinimize = false;

    // Basic error handling for empty input
    if (json_input_str.empty())
    {
        cerr << "Error: No JSON input received from stdin." << endl;
        cout << createErrorJson("No JSON input received.").dump(4) << endl;
        return 1;
    }

    // Parse the JSON string
    nlohmann::json parsed_json;
    try
    {
        parsed_json = nlohmann::json::parse(json_input_str);
    }
    catch (const nlohmann::json::parse_error &e)
    {
        cerr << "JSON Parse Error: " << e.what() << endl;
        // Print first 500 chars of received JSON for debugging
        cerr << "Received JSON (first 500 chars):\n"
             << json_input_str.substr(0, min((size_t)500, json_input_str.length())) << "..." << endl;

        cout << createErrorJson("Failed to parse input JSON.", e.what()).dump(4) << endl;
        return 1;
    }

    toConvertNFA = parsed_json.at("toConvertNFA").get<bool>();
    toTestInput = parsed_json.at("toTestInput").get<bool>();
    toMinimize = parsed_json.at("toMinimize").get<bool>();

    // Create FiniteAutomaton object from parsed JSON
    optional<FiniteAutomaton> fa_opt = createAutomatonFromJson(parsed_json);

    if (!fa_opt)
    {
        cout << createErrorJson("Failed to create automaton from JSON.", "Missing or malformed fields in FA definition.").dump(4) << endl;
        return 1;
    }

    FiniteAutomaton original_fa = *fa_opt;

    // ALL DEBUG/INFO OUTPUT TO CERR
    cerr << "--- Original Automaton Definition ---" << endl;
    original_fa.printDefinition();
    cerr << endl;

    // --- NFA to DFA Conversion Logic ---
    nlohmann::json output_json;
    output_json["status"] = "success";
    output_json["original_fa_name"] = original_fa.getName();
    output_json["original_fa_type"] = original_fa.getType();
    output_json["message"] = "FA data successfully received and parsed by C++.";

    if (original_fa.getType() == "NFA" && toConvertNFA)
    {
        cerr << "\n--- Attempting NFA to DFA Conversion ---" << endl;
        optional<FiniteAutomaton> dfa_automaton_opt = original_fa.convertNfaToDfa();

        if (dfa_automaton_opt)
        {
            FiniteAutomaton dfa_automaton = *dfa_automaton_opt;
            cerr << "Conversion successful! Converted DFA:" << endl;
            dfa_automaton.printDefinition();
            cerr << endl;

            // Prepare JSON output for the converted DFA
            nlohmann::json converted_fa_json;
            nlohmann::json fa_header;
            fa_header["name"] = dfa_automaton.getName();
            fa_header["type"] = dfa_automaton.getType();
            fa_header["start_state_name"] = dfa_automaton.getStartState();
            fa_header["description"] = "";

            converted_fa_json["fa_header"] = fa_header;
            converted_fa_json["fa_states"] = nlohmann::json(dfa_automaton.getStates());
            converted_fa_json["fa_symbols"] = dfa_automaton.getAlphabet();
            converted_fa_json["fa_transitions"] = nlohmann::json(dfa_automaton.getRawTransitionsList());

            output_json["converted_dfa"] = converted_fa_json;
            output_json["conversion_message"] = "NFA successfully converted to DFA.";

            // Example: Test the converted DFA
            if (toTestInput)
            {
                cerr << "\n--- Testing Converted DFA ---" << endl;
                string test_str1 = "a";
                string test_str2 = "ab";
                string test_str3 = "b";
                string test_str4 = "aaabb";

                cerr << "Test '" << test_str1 << "': " << (dfa_automaton.testInput(test_str1) ? "Accepted" : "Rejected") << endl;
                cerr << "Test '" << test_str2 << "': " << (dfa_automaton.testInput(test_str2) ? "Accepted" : "Rejected") << endl;
                cerr << "Test '" << test_str3 << "': " << (dfa_automaton.testInput(test_str3) ? "Accepted" : "Rejected") << endl;
                cerr << "Test '" << test_str4 << "': " << (dfa_automaton.testInput(test_str4) ? "Accepted" : "Rejected") << endl;
            }
        }
        else
        {
            cerr << "NFA to DFA Conversion failed (check console for details)." << endl;
            output_json["conversion_message"] = "NFA to DFA Conversion failed.";
        }
    }
    else if (original_fa.getType() == "DFA" && toConvertNFA)
    {
        output_json["message"] = "Automaton is already a DFA. No conversion needed.";
        output_json["minimization_prompt"] = "DFA minimization logic would run here.";

        // Test the existing DFA as well
        if (toTestInput)
        {
            cerr << "\n--- Testing Original DFA ---" << endl;
            string test_str1 = "a";
            string test_str2 = "ab";
            string test_str3 = "b";
            string test_str4 = "aaabb";

            cerr << "Test '" << test_str1 << "': " << (original_fa.testInput(test_str1) ? "Accepted" : "Rejected") << endl;
            cerr << "Test '" << test_str2 << "': " << (original_fa.testInput(test_str2) ? "Accepted" : "Rejected") << endl;
            cerr << "Test '" << test_str3 << "': " << (original_fa.testInput(test_str3) ? "Accepted" : "Rejected") << endl;
            cerr << "Test '" << test_str4 << "': " << (original_fa.testInput(test_str4) ? "Accepted" : "Rejected") << endl;
        }
    }

    // Print the final JSON output to stdout. Python will capture this.
    cout << output_json.dump(4) << endl;

    return 0;
}
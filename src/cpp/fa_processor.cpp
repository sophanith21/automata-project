#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <nlohmann/json.hpp>
#include <queue>             // For BFS in epsilon closure
#include <algorithm>         // For std::remove, std::sort, etc.
#include <sstream>           // For building DFA state names
#include <optional>          // For std::optional return types (C++17)

// Define a constant for our epsilon symbol, consistent with Python
const std::string EPSILON_SYMBOL = "ep";

// --- C++ Data Structures ---

struct FAState {
    std::string name;
    bool is_accepting;

    // Helper for debugging/printing
    std::string toString() const {
        return name + (is_accepting ? "*" : "");
    }

    // For using FAState directly in sets/maps if ever needed
    bool operator<(const FAState& other) const {
        return name < other.name; // Comparison based on name
    }
    bool operator==(const FAState& other) const {
        return name == other.name; // Equality based on name
    }
};

struct FATransition {
    std::string from_state;
    std::string symbol;
    std::set<std::string> to_states; // Using std::set for unique to_states (NFA)
};

// --- Helper functions for nlohmann/json serialization/deserialization ---
// These functions must be defined before they are used (e.g., in main)
// by nlohmann::json::get<T>() or nlohmann::json(T)
void from_json(const nlohmann::json& j, FAState& s) {
    j.at("name").get_to(s.name);
    j.at("is_accepting").get_to(s.is_accepting);
}

void from_json(const nlohmann::json& j, FATransition& t) {
    j.at("from").get_to(t.from_state);
    j.at("symbol").get_to(t.symbol);
    j.at("to").get_to(t.to_states);
}

void to_json(nlohmann::json& j, const FAState& s) {
    j = nlohmann::json{{"name", s.name}, {"is_accepting", s.is_accepting}};
}

void to_json(nlohmann::json& j, const FATransition& t) {
    j = nlohmann::json{{"from", t.from_state}, {"symbol", t.symbol}, {"to", t.to_states}};
}


// --- FiniteAutomaton Class Definition (all in one file) ---

class FiniteAutomaton {
public:
    // Constructors
    FiniteAutomaton() : name_("Unnamed_FA"), type_("NFA"), start_state_("") {} // Default constructor

    // Main constructor for building from parsed data
    FiniteAutomaton(const std::string& name, const std::string& type,
                    const std::string& start_state, const std::vector<FAState>& states,
                    const std::vector<std::string>& alphabet,
                    const std::vector<FATransition>& raw_transitions)
        : name_(name), type_(type), start_state_(start_state), states_(states),
          alphabet_(alphabet), raw_transitions_list_(raw_transitions)
    {
        buildTransitionsMap(); // Populate the map on construction
    }

    // Public methods for FA operations
    bool testInput(const std::string& input_string) const;

    // NFA to DFA Conversion Method
    // Returns a new FiniteAutomaton object representing the converted DFA
    std::optional<FiniteAutomaton> convertNfaToDfa() const;
    std::optional<FiniteAutomaton> minimizeDfa() const; // DFA minimization

    // Getter methods for accessing private members
    const std::string& getName() const { return name_; }
    const std::string& getType() const { return type_; }
    const std::string& getStartState() const { return start_state_; }
    const std::vector<FAState>& getStates() const { return states_; }
    const std::vector<std::string>& getAlphabet() const { return alphabet_; }
    const std::map<std::pair<std::string, std::string>, std::set<std::string>>& getTransitionsMap() const { return transitions_map_; }
    const std::vector<FATransition>& getRawTransitionsList() const { return raw_transitions_list_; }

    // Helper for debugging/printing
    void printDefinition() const;

private:
    std::string name_;
    std::string type_; // "DFA" or "NFA"
    std::string start_state_;
    std::vector<FAState> states_;
    std::vector<std::string> alphabet_; // List of symbols

    // A map for efficient transition lookup
    std::map<std::pair<std::string, std::string>, std::set<std::string>> transitions_map_;

    // Original list of transitions (useful for maintaining original structure)
    std::vector<FATransition> raw_transitions_list_;

    // Private helper methods for internal class logic
    void buildTransitionsMap(); // Populates transitions_map_ from raw_transitions_list_
    bool isAcceptingState(const std::string& state_name) const; // Checks if a given state is accepting

    // Helper functions for NFA to DFA conversion (private as they are internal to the algorithm)
    std::set<std::string> getEpsilonClosure(const std::set<std::string>& nfa_states) const;
    std::set<std::string> move(const std::set<std::string>& nfa_states, const std::string& symbol) const;
    bool containsAcceptingStateForSet(const std::set<std::string>& nfa_states) const; // Checks if any NFA state in a set is accepting
    std::string createDfaStateName(const std::set<std::string>& nfa_states) const;
};

// --- FiniteAutomaton Class Method Implementations ---

void FiniteAutomaton::buildTransitionsMap() {
    transitions_map_.clear();
    for (const auto& trans : raw_transitions_list_) {
        transitions_map_[{trans.from_state, trans.symbol}].insert(
            trans.to_states.begin(), trans.to_states.end()
        );
    }
}

bool FiniteAutomaton::isAcceptingState(const std::string& state_name) const {
    for (const auto& state : states_) {
        if (state.name == state_name) {
            return state.is_accepting;
        }
    }
    return false; // State not found
}

bool FiniteAutomaton::testInput(const std::string& input_string) const {
    if (type_ != "DFA") {
        std::cerr << "Warning: testInput is currently only accurate for DFA type. "
                  << "This automaton is of type " << type_ << "." << std::endl;
        return false; // Indicate not implemented for NFA behavior
    }

    std::string current_state = start_state_;
    for (char symbol_char : input_string) {
        std::string symbol(1, symbol_char); // Convert char to string
        auto it = transitions_map_.find({current_state, symbol});
        if (it == transitions_map_.end() || it->second.empty()) {
            return false; // No transition or dead end
        }
        // For DFA, there should be exactly one next state
        current_state = *it->second.begin();
    }
    return isAcceptingState(current_state);
}

void FiniteAutomaton::printDefinition() const {
    std::cerr << "Automaton Name: " << name_ << std::endl; // Changed to cerr
    std::cerr << "Type: " << type_ << std::endl; // Changed to cerr
    std::cerr << "Start State: " << start_state_ << std::endl; // Changed to cerr
    std::cerr << "States: "; // Changed to cerr
    for (const auto& state : states_) {
        std::cerr << state.toString() << " "; // Changed to cerr
    }
    std::cerr << std::endl; // Changed to cerr
    std::cerr << "Alphabet: "; // Changed to cerr
    for (const auto& symbol : alphabet_) {
        std::cerr << symbol << " "; // Changed to cerr
    }
    std::cerr << std::endl; // Changed to cerr
    std::cerr << "Transitions:" << std::endl; // Changed to cerr
    for (const auto& pair : transitions_map_) {
        std::cerr << "   (" << pair.first.first << ", " << pair.first.second << ") -> {"; // Changed to cerr
        bool first = true;
        for (const auto& to_state : pair.second) {
            if (!first) std::cerr << ", "; // Changed to cerr
            std::cerr << to_state; // Changed to cerr
            first = false;
        }
        std::cerr << "}" << std::endl; // Changed to cerr
    }
}

// --- NFA to DFA Helper Functions Implementations (within the class) ---

std::set<std::string> FiniteAutomaton::getEpsilonClosure(const std::set<std::string>& nfa_states) const {
    std::set<std::string> closure = nfa_states;
    std::queue<std::string> q;

    for (const std::string& state : nfa_states) {
        q.push(state);
    }

    while (!q.empty()) {
        std::string current_state = q.front();
        q.pop();

        auto it = transitions_map_.find({current_state, EPSILON_SYMBOL});
        if (it != transitions_map_.end()) {
            for (const std::string& next_state : it->second) {
                if (closure.find(next_state) == closure.end()) {
                    closure.insert(next_state);
                    q.push(next_state);
                }
            }
        }
    }
    return closure;
}

std::set<std::string> FiniteAutomaton::move(const std::set<std::string>& nfa_states, const std::string& symbol) const {
    std::set<std::string> reachable_states;
    for (const std::string& state : nfa_states) {
        auto it = transitions_map_.find({state, symbol});
        if (it != transitions_map_.end()) {
            reachable_states.insert(it->second.begin(), it->second.end());
        }
    }
    return reachable_states;
}

bool FiniteAutomaton::containsAcceptingStateForSet(const std::set<std::string>& nfa_states) const {
    for (const std::string& nfa_state_name : nfa_states) {
        if (isAcceptingState(nfa_state_name)) { // Reusing the private helper
            return true;
        }
    }
    return false;
}

std::string FiniteAutomaton::createDfaStateName(const std::set<std::string>& nfa_states) const {
    if (nfa_states.empty()) {
        return "{}";
    }
    std::ostringstream oss;
    oss << "{";
    bool first = true;
    for (const std::string& state : nfa_states) {
        if (!first) {
            oss << ",";
        }
        oss << state;
        first = false;
    }
    oss << "}";
    return oss.str();
}

// --- Main NFA to DFA Conversion Algorithm (Subset Construction) ---
std::optional<FiniteAutomaton> FiniteAutomaton::convertNfaToDfa() const {
    if (type_ == "DFA") {
        std::cerr << "Warning: This automaton is already a DFA. No conversion performed." << std::endl;
        return *this; // Return a copy of itself
    }

    std::string new_fa_name = name_ + "_DFA";
    std::string new_fa_type = "DFA";
    std::vector<std::string> dfa_alphabet = alphabet_;

    // Remove EPSILON_SYMBOL from DFA alphabet if it was present
    dfa_alphabet.erase(std::remove(dfa_alphabet.begin(), dfa_alphabet.end(), EPSILON_SYMBOL), dfa_alphabet.end());

    std::vector<FAState> dfa_states;
    std::vector<FATransition> dfa_raw_transitions;

    std::map<std::set<std::string>, std::string> dfa_state_names; // Maps NFA state sets to DFA state names
    std::queue<std::set<std::string>> unprocessed_dfa_states_q;

    // 1. Initial DFA state: Epsilon closure of the NFA's start state
    std::set<std::string> initial_nfa_states_set = {start_state_};
    std::set<std::string> dfa_start_set = getEpsilonClosure(initial_nfa_states_set);

    if (dfa_start_set.empty()) {
        std::cerr << "Error: NFA start state has an empty epsilon closure. Cannot convert to DFA." << std::endl;
        return std::nullopt;
    }

    std::string dfa_start_state_name = createDfaStateName(dfa_start_set);

    dfa_state_names[dfa_start_set] = dfa_start_state_name; // Perform insertion of the {dfa_start_set, dfa_start_state_name} into the map
    unprocessed_dfa_states_q.push(dfa_start_set);

    // Add initial DFA state
    dfa_states.push_back({
        dfa_start_state_name,
        containsAcceptingStateForSet(dfa_start_set)
    });

    // 2. Process states from the queue
    while (!unprocessed_dfa_states_q.empty()) {
        std::set<std::string> current_dfa_set = unprocessed_dfa_states_q.front();
        unprocessed_dfa_states_q.pop();

        std::string current_dfa_name = dfa_state_names[current_dfa_set];

        for (const std::string& symbol : dfa_alphabet) {
            std::set<std::string> moved_nfa_states = move(current_dfa_set, symbol);
            std::set<std::string> next_dfa_set = getEpsilonClosure(moved_nfa_states);

            std::string next_dfa_state_name;

            if (next_dfa_set.empty()) {
                // If it leads to the empty set, it goes to the Dead state
                next_dfa_state_name = "Dead";
                if (dfa_state_names.find(next_dfa_set) == dfa_state_names.end()) {
                    // Only discover the 'Dead' state once
                    dfa_state_names[next_dfa_set] = next_dfa_state_name;
                    dfa_states.push_back({
                        next_dfa_state_name,
                        false // Dead state is never accepting
                    });
                    // Push the empty set onto the queue so its transitions (self-loops) are processed
                    unprocessed_dfa_states_q.push(next_dfa_set);
                }
            } else {
                // This is a regular, non-empty DFA state
                if (dfa_state_names.find(next_dfa_set) == dfa_state_names.end()) {
                    // New DFA state discovered
                    next_dfa_state_name = createDfaStateName(next_dfa_set);
                    dfa_state_names[next_dfa_set] = next_dfa_state_name;
                    
                    dfa_states.push_back({
                        next_dfa_state_name,
                        containsAcceptingStateForSet(next_dfa_set)
                    });
                    unprocessed_dfa_states_q.push(next_dfa_set); // Add to queue for processing
                } else {
                    // Existing DFA state
                    next_dfa_state_name = dfa_state_names[next_dfa_set];
                }
            }

            FATransition new_transition;
            new_transition.from_state = current_dfa_name;
            new_transition.symbol = symbol;
            new_transition.to_states.insert(next_dfa_state_name); // DFA transitions to a single state
            dfa_raw_transitions.push_back(new_transition);
        }
    }

    // Create and return the new DFA object
    return FiniteAutomaton(new_fa_name, new_fa_type, dfa_start_state_name,
                           dfa_states, dfa_alphabet, dfa_raw_transitions);
}

// --- DFA Minimization Algorithm (Hopcroft's Algorithm, simplified) ---
std::optional<FiniteAutomaton> FiniteAutomaton::minimizeDfa() const {
    if (type_ != "DFA") {
        std::cerr << "Error: Minimization only applies to DFA." << std::endl;
        return std::nullopt;
    }
    // 1. Separate accepting and non-accepting states
    std::set<std::string> accepting, non_accepting;
    for (const auto& s : states_) {
        if (s.is_accepting) accepting.insert(s.name);
        else non_accepting.insert(s.name);
    }
    // 2. Initial partition
    std::vector<std::set<std::string>> partitions;
    if (!accepting.empty()) partitions.push_back(accepting);
    if (!non_accepting.empty()) partitions.push_back(non_accepting);
    // 3. Refinement
    bool changed = true;
    while (changed) {
        changed = false;
        std::vector<std::set<std::string>> new_partitions;
        for (const auto& group : partitions) {
            std::map<std::vector<int>, std::set<std::string>> splitter;
            for (const auto& state : group) {
                std::vector<int> sig;
                for (const auto& symbol : alphabet_) {
                    auto it = transitions_map_.find({state, symbol});
                    std::string dest = (it != transitions_map_.end() && !it->second.empty()) ? *it->second.begin() : "";
                    int part_idx = -1;
                    for (size_t i = 0; i < partitions.size(); ++i) {
                        if (!dest.empty() && partitions[i].count(dest)) { part_idx = (int)i; break; }
                    }
                    sig.push_back(part_idx);
                }
                splitter[sig].insert(state);
            }
            if (splitter.size() == 1) {
                new_partitions.push_back(group);
            } else {
                changed = true;
                for (const auto& kv : splitter) {
                    new_partitions.push_back(kv.second);
                }
            }
        }
        partitions = new_partitions;
    }
    // 4. Build new DFA
    std::map<std::string, int> state_to_partition;
    for (size_t i = 0; i < partitions.size(); ++i) {
        for (const auto& s : partitions[i]) {
            state_to_partition[s] = (int)i;
        }
    }
    // New state names
    std::vector<FAState> min_states;
    std::vector<FATransition> min_transitions;
    std::string min_start_state;
    for (size_t i = 0; i < partitions.size(); ++i) {
        bool is_accepting = false;
        for (const auto& s : partitions[i]) {
            if (accepting.count(s)) { is_accepting = true; break; }
        }
        std::string state_name = "Q" + std::to_string(i);
        min_states.push_back({state_name, is_accepting});
        if (partitions[i].count(start_state_)) min_start_state = state_name;
    }
    // Build transitions
    for (size_t i = 0; i < partitions.size(); ++i) {
        std::string from_name = "Q" + std::to_string(i);
        const auto& rep = *partitions[i].begin(); // representative
        for (const auto& symbol : alphabet_) {
            auto it = transitions_map_.find({rep, symbol});
            if (it != transitions_map_.end() && !it->second.empty()) {
                std::string dest = *it->second.begin();
                int dest_idx = state_to_partition[dest];
                std::string to_name = "Q" + std::to_string(dest_idx);
                FATransition t;
                t.from_state = from_name;
                t.symbol = symbol;
                t.to_states.insert(to_name);
                min_transitions.push_back(t);
            }
        }
    }
    // Return minimized DFA
    return FiniteAutomaton(name_ + "_min", "DFA", min_start_state, min_states, alphabet_, min_transitions);
}

// --- General Utility Functions (for stdin/stdout JSON) ---

std::string readStdinToString() {
    std::string json_input_str;
    std::string line;
    while (std::getline(std::cin, line)) {
        json_input_str += line;
    }
    return json_input_str;
}

nlohmann::json createErrorJson(const std::string& message, const std::string& details = "") {
    nlohmann::json error_output;
    error_output["status"] = "error";
    error_output["message"] = message;
    if (!details.empty()) {
        error_output["details"] = details;
    }
    return error_output;
}

// --- Function to create FiniteAutomaton from parsed JSON ---
// This could be a static factory method of FiniteAutomaton if preferred,
// but for a single-file setup, a free function is fine.
std::optional<FiniteAutomaton> createAutomatonFromJson(const nlohmann::json& json_data) {
    try {
        std::string name = json_data.at("name").get<std::string>();
        std::string type = json_data.at("type").get<std::string>();
        std::string start_state = json_data.at("start_state").get<std::string>();

        // Use nlohmann/json's get<>() with our custom from_json overloads
        std::vector<FAState> states = json_data.at("states").get<std::vector<FAState>>();
        std::vector<std::string> alphabet = json_data.at("alphabet").get<std::vector<std::string>>();
        std::vector<FATransition> raw_transitions = json_data.at("transitions").get<std::vector<FATransition>>();

        return FiniteAutomaton(name, type, start_state, states, alphabet, raw_transitions);

    } catch (const nlohmann::json::exception& e) {
        std::cerr << "Error parsing automaton JSON structure: " << e.what() << std::endl;
        return std::nullopt;
    }
}


// --- Main Program Logic ---

int main() {
    // Read the entire JSON input from stdin
    std::string json_input_str = readStdinToString();
    bool toConvertNFA = false;
    bool toTestInput = false;
    bool toMinimize = false;

    // Basic error handling for empty input
    if (json_input_str.empty()) {
        std::cerr << "Error: No JSON input received from stdin." << std::endl;
        std::cout << createErrorJson("No JSON input received.").dump(4) << std::endl;
        return 1;
    }

    // Parse the JSON string
    nlohmann::json parsed_json;
    try {
        parsed_json = nlohmann::json::parse(json_input_str);
    } catch (const nlohmann::json::parse_error& e) {
        std::cerr << "JSON Parse Error: " << e.what() << std::endl;
        // Print first 500 chars of received JSON for debugging
        std::cerr << "Received JSON (first 500 chars):\n" << json_input_str.substr(0, std::min((size_t)500, json_input_str.length())) << "..." << std::endl;

        std::cout << createErrorJson("Failed to parse input JSON.", e.what()).dump(4) << std::endl;
        return 1;
    }
    
    toConvertNFA = parsed_json.at("toConvertNFA").get<bool>();
    toTestInput = parsed_json.at("toTestInput").get<bool>();
    toMinimize = parsed_json.at("toMinimize").get<bool>();

    // Create FiniteAutomaton object from parsed JSON
    std::optional<FiniteAutomaton> fa_opt = createAutomatonFromJson(parsed_json);

    if (!fa_opt) {
        std::cout << createErrorJson("Failed to create automaton from JSON.", "Missing or malformed fields in FA definition.").dump(4) << std::endl;
        return 1;
    }

    FiniteAutomaton original_fa = *fa_opt;

    // ALL DEBUG/INFO OUTPUT TO STD::CERR
    std::cerr << "--- Original Automaton Definition ---" << std::endl; // Changed to cerr
    original_fa.printDefinition();
    std::cerr << std::endl; // Changed to cerr

    // --- NFA to DFA Conversion Logic ---
    nlohmann::json output_json;
    output_json["status"] = "success";
    output_json["original_fa_name"] = original_fa.getName();
    output_json["original_fa_type"] = original_fa.getType();
    output_json["message"] = "FA data successfully received and parsed by C++.";

    if (original_fa.getType() == "NFA" && toConvertNFA) {
        std::cerr << "\n--- Attempting NFA to DFA Conversion ---" << std::endl; // Changed to cerr
        std::optional<FiniteAutomaton> dfa_automaton_opt = original_fa.convertNfaToDfa();

        if (dfa_automaton_opt) {
            FiniteAutomaton dfa_automaton = *dfa_automaton_opt;
            std::cerr << "Conversion successful! Converted DFA:" << std::endl; // Changed to cerr
            dfa_automaton.printDefinition(); // This function also needs modification
            std::cerr << std::endl; // Changed to cerr

            // Prepare JSON output for the converted DFA
            nlohmann::json converted_fa_json;
            converted_fa_json["name"] = dfa_automaton.getName();
            converted_fa_json["type"] = dfa_automaton.getType();
            converted_fa_json["start_state"] = dfa_automaton.getStartState();

            converted_fa_json["states"] = nlohmann::json(dfa_automaton.getStates());
            converted_fa_json["alphabet"] = dfa_automaton.getAlphabet();
            converted_fa_json["transitions"] = nlohmann::json(dfa_automaton.getRawTransitionsList());

            output_json["converted_dfa"] = converted_fa_json;
            output_json["conversion_message"] = "NFA successfully converted to DFA.";

            // Example: Test the converted DFA
            if (toTestInput){
                std::cerr << "\n--- Testing Converted DFA ---" << std::endl; // Changed to cerr
                std::string test_str1 = "a";
                std::string test_str2 = "ab";
                std::string test_str3 = "b";
                std::string test_str4 = "aaabb";

                std::cerr << "Test '" << test_str1 << "': " << (dfa_automaton.testInput(test_str1) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
                std::cerr << "Test '" << test_str2 << "': " << (dfa_automaton.testInput(test_str2) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
                std::cerr << "Test '" << test_str3 << "': " << (dfa_automaton.testInput(test_str3) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
                std::cerr << "Test '" << test_str4 << "': " << (dfa_automaton.testInput(test_str4) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
            }

        } else {
            std::cerr << "NFA to DFA Conversion failed (check console for details)." << std::endl; // Changed to cerr
            output_json["conversion_message"] = "NFA to DFA Conversion failed.";
        }
    } else if (original_fa.getType() == "DFA" && toConvertNFA) {
        output_json["message"] = "Automaton is already a DFA. No conversion needed.";
        output_json["minimization_prompt"] = "DFA minimization logic would run here.";

        // Test the existing DFA as well
        if (toTestInput){
            std::cerr << "\n--- Testing Original DFA ---" << std::endl; // Changed to cerr
            std::string test_str1 = "a";
            std::string test_str2 = "ab";
            std::string test_str3 = "b";
            std::string test_str4 = "aaabb";

            std::cerr << "Test '" << test_str1 << "': " << (original_fa.testInput(test_str1) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
            std::cerr << "Test '" << test_str2 << "': " << (original_fa.testInput(test_str2) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
            std::cerr << "Test '" << test_str3 << "': " << (original_fa.testInput(test_str3) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
            std::cerr << "Test '" << test_str4 << "': " << (original_fa.testInput(test_str4) ? "Accepted" : "Rejected") << std::endl; // Changed to cerr
        }
    }

    // DFA Minimization logic
    if (original_fa.getType() == "DFA" && toMinimize) {
        std::cerr << "\n--- Attempting DFA Minimization ---" << std::endl;
        std::optional<FiniteAutomaton> min_dfa_opt = original_fa.minimizeDfa();
        if (min_dfa_opt) {
            FiniteAutomaton min_dfa = *min_dfa_opt;
            std::cerr << "Minimization successful! Minimized DFA:" << std::endl;
            min_dfa.printDefinition();
            nlohmann::json min_fa_json;
            min_fa_json["name"] = min_dfa.getName();
            min_fa_json["type"] = min_dfa.getType();
            min_fa_json["start_state"] = min_dfa.getStartState();
            min_fa_json["states"] = nlohmann::json(min_dfa.getStates());
            min_fa_json["alphabet"] = min_dfa.getAlphabet();
            min_fa_json["transitions"] = nlohmann::json(min_dfa.getRawTransitionsList());
            output_json["minimized_dfa"] = min_fa_json;
            output_json["minimization_message"] = "DFA successfully minimized.";
            // Output accepting and non-accepting states as arrays
            std::vector<std::string> accepting_states, non_accepting_states;
            for (const auto& s : min_dfa.getStates()) {
                if (s.is_accepting) accepting_states.push_back(s.name);
                else non_accepting_states.push_back(s.name);
            }
            output_json["accepting_states"] = accepting_states;
            output_json["non_accepting_states"] = non_accepting_states;
        } else {
            std::cerr << "DFA Minimization failed." << std::endl;
            output_json["minimization_message"] = "DFA Minimization failed.";
        }
    }
    // Example: Separate accepting and non-accepting states (for user)
    std::vector<std::string> accepting_states, non_accepting_states;
    for (const auto& s : original_fa.getStates()) {
        if (s.is_accepting) accepting_states.push_back(s.name);
        else non_accepting_states.push_back(s.name);
    }
    output_json["accepting_states"] = accepting_states;
    output_json["non_accepting_states"] = non_accepting_states;

    // Print the final JSON output to stdout. Python will capture this.
    std::cout << output_json.dump(4) << std::endl; // This is good, leave it as cout

    return 0;
}
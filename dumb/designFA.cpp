#include<iostream>
#include<stdio.h>
#include<string>
#include <nlohmann/json.hpp>
#include <sstream>
#include <fstream>

using namespace std;
using json = nlohmann::json;


// function to print the dash line 
void dashLine(int boxwidth){ 
    for (int i = 0; i<boxwidth; i++){
        cout << "-";
    }
    cout << endl;
}

int main(){
    int numOfState;
    int numOfSymbol;
    vector<char> symbol;

    do{
        cout << "Please enter number of state: ";
        cin >> numOfState;
    }while(numOfState < 1);

    do{
        cout << "Please enter the number of symbol: ";
        cin >> numOfSymbol;
    }while(numOfSymbol < 1);

    
    char symbolTemp;
    for(int i = 0; i < numOfSymbol; i++){
        cout << "Please enter the symbol " << i + 1 << ": ";
        cin.clear();
        cin.ignore();  // how cin.clear() and cin.ignore() work together?
        cin >> symbolTemp;
        symbol.push_back(symbolTemp);
    }
    
    char epsilonDecision;
    do{
        cout << "Do the FA include epsilon?" << endl;
        cout << "Yes (Y), No (N): ";
        cin.clear();
        cin.ignore();
        cin >> epsilonDecision;
    } while (epsilonDecision != 'Y' && epsilonDecision != 'N');

    bool hasEpsilon = false;
    if(epsilonDecision == 'Y'){
        cout << "'e' means epsilon " << endl;
        hasEpsilon = true;
    }

    vector<string> state;
    for(int i = 0; i<numOfState; i++){
        char letter = 'A' + i;
        // state[i] = toupper(letter);
        state.push_back(string(1, letter)); 
    }

    int acceptingStates;
    do{
        cout << "Please enter the amount of accepting state: ";
        cin >> acceptingStates;
    } while(acceptingStates > numOfState || acceptingStates < 1); 

    vector<char> acceptingState(acceptingStates);
    for( int i = 0; i < acceptingStates; i++){
        cout << "Please enter final state " << i + 1 << " : ";
        cin >> acceptingState[i];
    }
    
    int boxWidth = 50;
    for(int i = 0; i< boxWidth ;i++){
        cout << "-";
    }

    cout << endl;

    dashLine(50);
    vector<string> nextState(numOfState * symbol.size()); // use string because NFA contain multiple next states
    cout << "Please enter the next state for every inputs." << endl;
    cout << "This symbol '-' means no transition" << endl;

    int totalSymbols = symbol.size() + (hasEpsilon ? 1 : 0);
    for(int i = 0; i < numOfState; i++){
        cout << "State ' " << state[i] << " '" <<endl;
        for(int j = 0; j < symbol.size(); j++){
            cout << "\tS(" << state[i] << ", " << symbol[j] << ") = ";
            cin >> nextState[i * totalSymbols + j];
        }

        if(hasEpsilon){
            cout << "\tS(" << state[i] << ", e) = ";
            cin >> nextState[i * totalSymbols + symbol.size()]; 
        }
    }

    string faType = "DFA";
    for(int i = 0; i<numOfState * symbol.size(); i++){
        if(nextState[i] == "-" || nextState[i].length() > 1 || epsilonDecision == 'Y'){
            faType = "NFA";
            break;
        }
    }

    // finite summary
    cout << endl;
    dashLine(50);
    cout << "FA summary" << endl;
    cout << "->A is the start state" << endl;
    cout << "Any state contain * is the accepting state." << endl;
    dashLine(50);
    cout << " state \t\t";
    for (int i = 0; i < symbol.size(); i++){ // this loop is for create alphabets columns  
        cout << symbol[i] << "\t";
    }
    cout << endl; 

    dashLine(50);

    for(int i = 0; i< numOfState; i++){
        bool isAccepting = false;
        for(int j = 0; j<acceptingStates; j++){
            if(state[i][0] == acceptingState[j]){
                isAccepting = true;
                break;
            }
        }

        if(i == 0){
            cout << " ->";
        }
        else{
            cout << "  ";
        }

        if(isAccepting){
            cout << state[i] << "*" << "\t\t" ;
        }else{
            cout << state[i] << "\t\t";
        }

        for (int j = 0; j < symbol.size(); j++) {
            cout << nextState[i * symbol.size() + j] << "\t";
        }
        cout << endl;

    }
    
    dashLine(50);

    cout << "This FA states are: ";
    for(int i=0; i<numOfState; i++){
        cout << state[i];
        
        if(i < numOfState - 1){
            cout << ",";
        }
    }
    cout << endl;

    cout << "This is the transition" << endl;
    for(int i = 0; i< numOfState; i++){
        cout << " [ ";
        for(int j = 0; j<symbol.size(); j++){
            cout  << nextState[i * symbol.size() + j];
            cout << "; ";
        }
        cout << "]";
    }
    cout << endl; 

    cout << "The FA type is: " << faType << endl;
    cout << "number of symbol: " << numOfSymbol << endl;
    cout << "The symbol are: ";
    for(char s : symbol){
        cout << s << " ";
    }
    cout << endl;

    char saveToDatabaseDecision;
    cout << "Do you want to save data into the database?"<< endl;
    cout << "Yes (Y), No (N): ";
    cin >> saveToDatabaseDecision;

    string faName;



    return 0;
}
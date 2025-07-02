#include<iostream>
#include<stdio.h>
#include<string>
#include "json.hpp"
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
    int numOfacceptingState;
    vector<string>states;
    vector<string>symbols;
    vector<string>nextState;
    vector<vector<string>> transition;
    vector<char> acceptingStates;
    char epsilonDecision;
    bool hasEpsilon = false;
    string faType = "DFA";

    do{
        cout << "Please enter number of state: ";
        cin >> numOfState;
    }while(numOfState < 1);

    do{
        cout << "Please enter the number of symbol: ";
        cin >> numOfSymbol;
    }while(numOfSymbol < 1);

    string symbolTemp;
    for(int i = 0; i < numOfSymbol; i++){
        cout << "Please enter the symbol " << i + 1 << ": ";
        cin.clear();
        cin.ignore();  // how cin.clear() and cin.ignore() work together?
        cin >> symbolTemp;
        symbols.push_back(symbolTemp);
    }
    
    do{
        cout << "Do the FA include epsilon?" << endl;
        cout << "Yes (Y), No (N): ";
        cin.clear();
        cin.ignore();
        cin >> epsilonDecision;
    } while (epsilonDecision != 'Y' && epsilonDecision != 'N');

   
    if(epsilonDecision == 'Y'){
        cout << "'e' means epsilon " << endl;
        hasEpsilon = true;
    }

    for(int i = 0; i< numOfState; i++){
        char letter = 'A' + i;
        string state(1, letter);
        states.push_back(state);
    }

    do{
        cout << "Please enter the amount of accepting state: ";
        cin >> numOfacceptingState;
    } while(numOfacceptingState > numOfState || numOfacceptingState < 1); 

    for(int i = 0; i < numOfacceptingState; i++){
        char temp;
        bool isValid = false;

        do{
            cout << "Please enter final state " << i + 1 << " : ";
            cin >> temp;

            for(int j = 0; j< states.size(); j++){
                if(temp == states[j][0]){
                    isValid = true;
                    break;
                }
            }
        }while(!isValid);

        acceptingStates.push_back(temp);
    }


    for(int i = 0; i< states.size(); i++){
        bool isAccepting = false;
        for(int j = 0; j<acceptingStates.size(); j++){
            if(states[i][0] == acceptingStates[j]){
                isAccepting = true;
                break;
            }
        }

        if(isAccepting){
            states[i] += "*";
        }
    }

    int includeEpsilon = hasEpsilon ? (symbols.size() + 1) : symbols.size();
    nextState.resize(numOfState * includeEpsilon); 

    // input next state
    for( int i = 0; i < numOfState; i++){
        cout << "State ' " << states[i] << " '" <<endl;
        for(int j = 0; j < symbols.size(); j++){
            cout << "\tS(" << states[i] << ", " << symbols[j] << ") = ";
            cin >> nextState[i * includeEpsilon + j];
        }
        if(hasEpsilon){
            cout << "\tS(" << states[i] << ", e) = ";
            cin >> nextState[i * includeEpsilon + symbols.size()]; 
        }
    }

    for(int i = 0; i<states.size() * symbols.size(); i++){
        if(nextState[i] == "-" || nextState[i].length() > 1 || epsilonDecision == 'Y'){
            faType = "NFA";
            break;
        }
    }

    // arrange next state into an array of transition;
    int row = states.size();
    int column;
    if(hasEpsilon){ 
        column = includeEpsilon;
    }
    else{
         column = symbols.size();
    };
    transition.resize(row, vector<string>(column));

    int k = 0;
    for(int i = 0; i < transition.size(); i++){
        for(int j = 0; j< transition[i].size(); j++){
            transition[i][j] = nextState[k++];
        }
    }
    cout << endl;

    dashLine(50);

    // FA Summary
    cout << "FA summary" << endl;
    cout << "A is the start state" << endl;
    cout << "Any state contain * is the accepting state." << endl;
    dashLine(50);
    cout << " state \t\t";
    for (int i = 0; i < symbols.size(); i++){ // this loop is for create alphabets columns  
        cout << symbols[i] << "\t";
    }
    if(hasEpsilon){
        cout << "e\t";
    }
    cout << endl; 
    dashLine(50);

    for (int i = 0; i < states.size(); i++) {
        cout << states[i] << "\t\t";
        for (int j = 0; j < includeEpsilon; j++) {
            cout << nextState[i * includeEpsilon + j] << "\t";
        }
        cout << endl;
    }

    // for display every state
    for(int i = 0; i< states.size(); i++){
        cout <<"This FA states: " << states[i] << ",";
    }
    cout << endl;


    // for display the FA type
    cout << "FA type is: " << faType << endl;
    
    // cout transition
    cout << "This is te transition" << endl;
    for(int i = 0; i < transition.size(); i++){
        for(int j = 0; j< transition[i].size(); j++){
            cout << transition[i][j] << ";"; 
        }
        cout << endl;
    }
    dashLine(50);
    char saveToDatabaseDecision;
    do{
        cout << "Do you want to save data into the database?"<< endl;
        cout << "Yes (Y), No (N): ";
        cin >> saveToDatabaseDecision;
    }while ( saveToDatabaseDecision != 'Y' && saveToDatabaseDecision != 'N');
    
    string faName;
    if( saveToDatabaseDecision == 'Y'){
        cout << "Please give this FA name: ";
        cin >> faName;
        json outputData;
        outputData["fa_name"]=faName;
        outputData["numOfStates"] = states.size();
        outputData["numOfSymbols"] = symbols.size();
        outputData["states"] = states;
        outputData["symbols"] = symbols;
        outputData["fa_type"] = faType;
        outputData["transition"] = transition;

        ofstream outFile("designFA.json");
        if(!outFile){
            cout << "The file is unable to open";
            return 1;
        }
        outFile << outputData.dump(4);
        outFile.close();
        cout << "FA data saved to json file successfully " << endl;
        
    }
    return 0;
}
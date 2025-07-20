#include<iostream>
#include<stdio.h>
#include<string>
#include <nlohmann/json.hpp>
#include <fstream>

using namespace std;
using json = nlohmann::json;

string checkFaType(const json& faData){
    const json& transitions = faData["transitions"];
    string faType = "DFA";

    if(faData["hasEpsilon"]){
        faType = "NFA";
    }
    for (auto& [state, transMap] : transitions.items()) {
        for (auto& [symbol, nextStates] : transMap.items()) {
            if (nextStates.is_array() && nextStates.size() == 1) {
                string nextTransition = nextStates[0];
                if(nextTransition.find(',') != string::npos){
                    faType = "NFA";
                }
                else if(nextTransition.find('-')!= string::npos){
                    faType = "NFA";
                }
            }
        }
    }

    return faType;

}
int main(){
    string inputData((istreambuf_iterator<char>(cin)), istreambuf_iterator<char>());
    json faData = json::parse(inputData);
    string faType = checkFaType(faData);
    cout << faType << endl;
    return 0;
}
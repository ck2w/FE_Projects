#ifndef MainEngine_H
#define MainEngine_H

#include "StockData.h"
#include "Utils.h"
#include "CalendarManager.h"
#include "Matrix.h"
#include <time.h>

using namespace std;

class MainEngine
{
public:
	int N;
	int weight_choice;   // Weights for AARt. 1: equal weights, 2: IWB weights
	CalendarManager calendar;
	vector<StockData*> stock_list;
	map<string, double> weights_map;
	map<string, StockData*> stock_map;
	vector<string> groups;
	map<string, map<string, Vector>> research_result;
	vector<vector<Vector>> research_result_matrix;


	MainEngine(): N(30) { };
	MainEngine(int N_) : N(N_) { };

	void SetN(int N_) { N = N_; };

	void Initialize();

	void LoadStockData();
	void LoadWeightData();
	void RetrieveDataSingleThread();
	void RetrieveDataMultiThread();

	map<string, map<string, Vector>> RunResearch();

	Vector CalReturnForGroup(vector<StockData*> stock_list);
	Vector GetWeights(vector<StockData*> stock_list);


	void RunMenu();

	void ClearAll();
};


#endif
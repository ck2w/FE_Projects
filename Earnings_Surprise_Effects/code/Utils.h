#ifndef Utils_H
#define Utils_H

#include <stdio.h>
#include <stdlib.h>

#include <string>
#include <vector>
#include <map>
#include <sstream> 
#include <fstream>
#include <iostream>
#include <random>  
#include <time.h>  
#include <mutex> 
#include <deque>
#include <condition_variable>
#include "StockData.h"
#include "Configure.h"
#include "curl/curl.h"

using namespace std;

typedef struct MyData
{
	StockData* sd;
	CURL* handle;
	map<string, double> benchmark_mapping;
	int size;
	string sCrumb;
	string sCookies;
}MYDATA;

//mutex display_data_mutex;

vector<StockData*> load_stock_data(string filename, string group);

vector<StockData*> combine_stock_list(vector<StockData*> stock_list_miss, vector<StockData*> stock_list_meet, vector<StockData*> stock_list_beat);

map<string, StockData*> create_stock_map(vector<StockData*> stock_list);

void thread_producer(MYDATA* md);

int thread_consumer();

bool cmp(pair<StockData*, double> a, pair<StockData*, double> b);

map<string, vector<StockData*>> bootstrapping(vector<StockData*> stock_list, int i);

void plot_caar(map<string, Vector> research_result, string type);

#endif

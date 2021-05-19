#define _CRT_SECURE_NO_WARNINGS
#ifndef FetchData_H
#define FetchData_H

#include <stdio.h>
#include <string>
#include <iostream>
#include <sstream>
#include <vector>
#include <locale>
#include <iomanip>
#include <fstream>
#include <thread>
#include <map>

#include "StockData.h"
//#include "curl.h"
#include "curl/curl.h"
//#include "Utils.h"

using namespace std;


struct MemoryStruct {
	char* memory;
	size_t size;
};


#endif
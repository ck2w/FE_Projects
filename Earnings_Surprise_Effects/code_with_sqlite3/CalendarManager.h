
#ifndef CalendarManager_H
#define CalendarManager_H

#include <string>
#include <vector>
#include <sstream> 
#include <fstream>
#include <iostream>
#include <algorithm>
#include "Configure.h"

using namespace std;

class CalendarManager
{
public:
	vector<string> trading_days;

	void LoadData()
	{
		ifstream inFile(CALENDAR_FILE, ios::in);
		string line;

		getline(inFile, line);

		while (getline(inFile, line)) trading_days.push_back(line);
	}

	vector<string>::iterator CalendarFind(string target)
	{	
		// some firms release report on weekends (eg: CE, ON), so we will need to adjust the day0 to next trading day.
		vector<string>::iterator iter = trading_days.begin();
		for (; iter != trading_days.end(); iter++)
		{
			if (*iter >= target) return iter;
		}
		return iter;
	}

	string NextNDays(string day0, int N)
	{
		auto it = CalendarFind(day0);
		int loc = distance(begin(trading_days), it);
		int dis = trading_days.size() - loc;
		if (it == trading_days.end())
		{
			cout << "can not find trading day" << endl;
			return "";
		}

		if (dis > N)
		{
			return trading_days[loc + N];
		}
		else
		{
			cout << "N too large for future days" << endl;
			return trading_days[trading_days.size()-1];
		}
	}

	string PrevNDays(string day0, int N)
	{
		auto it = CalendarFind(day0);
		int loc = distance(begin(trading_days), it);
		if (it == trading_days.end())
		{
			cout << "can not find trading day" << endl;
			return "";
		}

		if (loc > N)
		{
			return trading_days[loc - N];
		}
		else
		{
			cout << "N too large for previous days" << endl;
			return trading_days[0];
		}			
	}

	void DisplayDates()
	{
		for (auto iter : trading_days) cout << iter << endl;
	}
};

#endif
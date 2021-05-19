
#ifndef StockData_H
#define StockData_H

#include <string>
#include "FetchData.h"
#include "Vector.h"
#include "CalendarManager.h"


using namespace std;

class StockData
{
public:
	string ticker;
	string group;
	string announce_day;
	string period_end;
	double estimate_eps;
	double actual_eps;
	double eps_surprise;
	double eps_surprise_percent;

	string startTime;
	string endTime;
	int N;

	bool fetch_success;

	vector<string> dates;
	Vector adjclose;
	Vector adjreturn;
	Vector cum_adjreturn;


	vector<string> dates_benchmark;
	Vector adjclose_benchmark;
	Vector adjreturn_benchmark;
	Vector cum_adjreturn_benchmark;

	Vector abnormal_return;


	//struct MemoryStruct data;

	StockData() {};
	StockData(string ticker_);
	~StockData() {};

	// setters
	void SetTicker(string ticker_) { ticker = ticker_; };
	void SetGroup(string group_) { group = group_; };

	void SetAnnounceDay(string announce_day_) { announce_day = announce_day_; };
	void SetPeriodEnd(string period_end_) { period_end = period_end_; };
	void SetEstimateEPS(double estimate_eps_) { estimate_eps = estimate_eps_; };
	void SetActualEPS(double actual_eps_) { actual_eps = actual_eps_; };
	void SetEPSSurprise(double eps_surprise_) { eps_surprise = eps_surprise_; };
	void SetEPSSurprisePercent(double eps_surprise_percent_) { eps_surprise_percent = eps_surprise_percent_; };

	void RetrieveDataSetting(int N, CalendarManager* calendar);
	void RetrieveDataSanityCheck();
	void CalDailyReturns();

	// getters
	string GetTicker() const { return ticker; };


	void DisplayAttribute() const;
	void DisplayData() const;

private:

};

#endif
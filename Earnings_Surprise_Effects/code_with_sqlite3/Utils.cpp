#define _CRT_SECURE_NO_WARNINGS

#include "Utils.h"

mutex display_data_mutex;
mutex queue_not_empty_mutex;
mutex curl_perform;
deque<MyData> q;
condition_variable cond;


extern int write_data2(void* ptr, size_t size, size_t nmemb, void* data);

extern string getTimeinSeconds(string Time);

vector<StockData*> load_stock_data(string filename, string group)
{
	// load data from local grouped EPS files.
	// initiliaze StockData instances using data.

	//cout << filename << endl;
	ifstream inFile(filename, ios::in);
	string line;

	vector<StockData*> stock_list;

	while (getline(inFile, line))
	{
		//cout << line << endl;

		StockData* stock = new StockData();
		stock->SetGroup(group);

		stock->SetTicker(line.substr(0, line.find_first_of(',')));

		stock->SetEPSSurprisePercent(stod(line.substr(line.find_last_of(',') + 1)));
		line.erase(line.find_last_of(','));

		stock->SetEPSSurprise(stod(line.substr(line.find_last_of(',') + 1)));
		line.erase(line.find_last_of(','));

		stock->SetActualEPS(stod(line.substr(line.find_last_of(',') + 1)));
		line.erase(line.find_last_of(','));

		stock->SetEstimateEPS(stod(line.substr(line.find_last_of(',') + 1)));
		line.erase(line.find_last_of(','));

		stock->SetPeriodEnd(line.substr(line.find_last_of(',') + 1));
		line.erase(line.find_last_of(','));

		stock->SetAnnounceDay(line.substr(line.find_last_of(',') + 1));

		//stock.ShowAttribute();
		stock_list.push_back(stock);
	}

	return stock_list;
}

vector<StockData*> combine_stock_list(vector<StockData*> stock_list_miss, vector<StockData*> stock_list_meet, vector<StockData*> stock_list_beat)
{
	// combine stock instances from three groups

	vector<StockData*> stock_list;
	for (auto iter : stock_list_miss)
	{
		stock_list.push_back(iter);
	}
	
	for (auto iter : stock_list_meet)
	{
		stock_list.push_back(iter);
	}

	for (auto iter : stock_list_beat)
	{
		stock_list.push_back(iter);
	}

	return stock_list;
}

std::map<string, StockData*> create_stock_map(vector<StockData*> stock_list)
{
	std::map<string, StockData*> stock_map;
	for (auto iter : stock_list)
	{
		stock_map[iter->GetTicker()] = iter;
	}
	return stock_map;
}


void thread_producer(MYDATA* md)
{
	int count = md->size;
	for (int i = 0; i < count; i++)
	{
		unique_lock<mutex> unique(queue_not_empty_mutex);
		q.push_front(md[i]);
		//this_thread::sleep_for(100ms);

		unique.unlock();
		cout << "producer a value: " << md[i].sd->ticker << endl;
		cond.notify_all();
	}

	// poison pill to terminate consumers
	MYDATA pill = md[0];
	pill.size = 0;

	unique_lock<mutex> unique(queue_not_empty_mutex);
	q.push_front(pill);
	unique.unlock();
	cout << "producer a pill" << endl;
	cond.notify_all();
	//this_thread::sleep_for(chrono::seconds(10));
}


int thread_consumer()
{
	MYDATA mydt;

	CURL* handle;

	CURLcode result;

	// curl_easy_init() returns a CURL easy handle 
	handle = curl_easy_init();

	if (handle)
	{
		while (1)
		{
			unique_lock<mutex> unique(queue_not_empty_mutex);
			while (q.empty())
				cond.wait(unique);
			mydt = q.back();
			if (mydt.size == 0)
			{
				// receive poison pill: finish all tasks, terminate current thread
				cout << "thread receive poison pill" << endl;
				unique.unlock();
				curl_easy_cleanup(handle);
				return 0;
			}
			q.pop_back();
			unique.unlock();

			StockData* sd = mydt.sd;
			//CURL* handle = mydt.handle;
			map<string, double> benchmark_mapping = mydt.benchmark_mapping;
			string sCrumb = mydt.sCrumb;
			string sCookies = mydt.sCookies;


			struct MemoryStruct data;
			data.memory = NULL;
			data.size = 0;

			string startTime = getTimeinSeconds(sd->startTime);
			string endTime = getTimeinSeconds(sd->endTime);
			string symbol = sd->ticker;

			cout << "fetch: fetching " << symbol << " from " << sd->startTime << " to " << sd->endTime << endl;


			string urlA = "https://query1.finance.yahoo.com/v7/finance/download/";
			string urlB = "?period1=";
			string urlC = "&period2=";
			string urlD = "&interval=1d&events=history&crumb=";
			string url = urlA + symbol + urlB + startTime + urlC + endTime + urlD + sCrumb;
			const char* cURL = url.c_str();
			const char* cookies = sCookies.c_str();
			curl_easy_setopt(handle, CURLOPT_COOKIE, cookies);
			curl_easy_setopt(handle, CURLOPT_URL, cURL);

			curl_easy_setopt(handle, CURLOPT_ENCODING, "");

			curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data2);
			curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void*)&data);
			result = curl_easy_perform(handle);

			if (result != CURLE_OK)
			{
				// if errors have occurred, tell us what is wrong with 'result'
				fprintf(stderr, "curl_easy_perform() failed: % s\n", curl_easy_strerror(result));
				return 1;
			}

			//cout << "fetch: storing " << symbol << " from " << sd->startTime << " to " << sd->endTime << endl;

			stringstream sData;
			sData.str(data.memory);
			string sValue, sDate;
			double dValue = 0;
			string line;
			getline(sData, line);

			//cout << "fetch: finish storing " << symbol << " from " << sd->startTime << " to " << sd->endTime << endl;

			try
			{
				while (getline(sData, line))
				{
					sDate = line.substr(0, line.find_first_of(','));
					line.erase(line.find_last_of(','));
					sValue = line.substr(line.find_last_of(',') + 1);
					dValue = strtod(sValue.c_str(), NULL);

					sd->dates.push_back(sDate);
					sd->adjclose.push_back(dValue);
					sd->dates_benchmark.push_back(sDate);
					sd->adjclose_benchmark.push_back(benchmark_mapping[sDate]);
				}
			}
			catch (out_of_range& exc)
			{
				cout << exc.what() << " Line:" << __LINE__ << " File:" << __FILE__ << endl;
			}
			catch (...)
			{
				cout << "other error." << " Line:" << __LINE__ << " File:" << __FILE__ << endl;
			}
			free(data.memory);
			data.size = 0;
		}
	}
	else
	{
		fprintf(stderr, "Curl init failed!\n");
		return 1;
	}


}

bool cmp(pair<StockData*, double> a, pair<StockData*, double> b) 
{
	return a.second < b.second;
}

map<string, vector<StockData*>> bootstrapping(vector<StockData*> stock_list, int seed)
{
	int bootstrap_num = BOOTSTRAP_NUM;
	default_random_engine random(time(NULL) + seed);
	std::uniform_real_distribution<double> dist(0.0, 1.0);

	vector< pair<StockData*, double> > vec;
	for (int i = 0; i < stock_list.size(); i++)
	{
		vec.push_back(pair<StockData*, double>(stock_list[i], dist(random)));
	}

	sort(vec.begin(), vec.end(), cmp);
	//cout << "start beat" << endl;
	// Beat
	vector<StockData*> beat_result;
	for (auto iter : vec)
	{
		if ((iter.first->group == "Beat") && (iter.first->fetch_success))
		{
			beat_result.push_back(iter.first);
			if (beat_result.size() == bootstrap_num) break;
		}
	}

	//cout << "start meet" << endl;
	// Meet
	vector<StockData*> meet_result;
	for (auto iter : vec)
	{
		if ((iter.first->group == "Meet") && (iter.first->fetch_success))
		{
			meet_result.push_back(iter.first);
			if (meet_result.size() == bootstrap_num) break;
		}
	}

	//cout << "start miss" << endl;
	// Miss
	vector<StockData*> miss_result;
	for (auto iter : vec)
	{
		if ((iter.first->group == "Miss") && (iter.first->fetch_success))
		{
			miss_result.push_back(iter.first);
			if (miss_result.size() == bootstrap_num) break;
		}
	}

	map<string, vector<StockData*>> bootstrap_result;
	bootstrap_result["Beat"] = beat_result;
	bootstrap_result["Meet"] = meet_result;
	bootstrap_result["Miss"] = miss_result;

	return bootstrap_result;
}

void plot_caar(map<string, Vector> research_result, string type) 
{
	int dataSize = research_result["Beat"].size();
	int N = (dataSize >> 1) + 1;
	FILE* gnuplotPipe, * tempDataFile;
	const char* tempDataFileName1 = "Beat";
	const char* tempDataFileName2 = "Meet";
	const char* tempDataFileName3 = "Miss";
	double x, y, x2, y2, x3, y3;
	int i;

	gnuplotPipe = _popen(GNU_PATH, "w");
	if (gnuplotPipe) {

		tempDataFile = fopen(tempDataFileName1, "w");
		for (i = 0; i < dataSize; i++) {
			x = i - N;
			if (type == "CAAR mean"){
				y = research_result["Beat"][i] - research_result["Beat"][N + 1];
			}else{
				y = research_result["Beat"][i];
			}
			fprintf(tempDataFile, "%lf %lf\n", x, y);
		}
		fclose(tempDataFile);

		tempDataFile = fopen(tempDataFileName2, "w");
		for (i = 0; i < dataSize; i++) {
			x2 = i - N;
			if (type == "CAAR mean") {
				y2 = research_result["Meet"][i] - research_result["Meet"][N + 1];
			}
			else {
				y2 = research_result["Meet"][i];
			}
			fprintf(tempDataFile, "%lf %lf\n", x2, y2);
		}
		fclose(tempDataFile);

		tempDataFile = fopen(tempDataFileName3, "w");
		for (i = 0; i < dataSize; i++) {
			x3 = i - N;
			if (type == "CAAR mean") {
				y3 = research_result["Miss"][i] - research_result["Miss"][N + 1];
			}
			else {
				y3 = research_result["Miss"][i];
			}
			fprintf(tempDataFile, "%lf %lf\n", x3, y3);
		}
		fclose(tempDataFile);


		fprintf(gnuplotPipe, "set term wxt\n");
		fprintf(gnuplotPipe, "set grid\n");
		fprintf(gnuplotPipe, "set xlabel 'N - Number of days'\n");
		fprintf(gnuplotPipe, "set ylabel '%s'\n", type.c_str());
		fprintf(gnuplotPipe, "set title '%s of all groups'\n", type.c_str());
		fprintf(gnuplotPipe, "set key left top\n");
		fprintf(gnuplotPipe, "plot \"%s\" with lines, \"%s\" with lines, \"%s\" with lines\n", tempDataFileName1, tempDataFileName2, tempDataFileName3);
		fflush(gnuplotPipe);

		this_thread::sleep_for(2s); // speed bump

		printf("press enter to continue...");
		//getchar();
		system("pause");
		remove(tempDataFileName1);
		remove(tempDataFileName2);
		remove(tempDataFileName3);
		fprintf(gnuplotPipe, "exit \n");
	}
	else {
		printf("gnuplot not found...");
	}
}


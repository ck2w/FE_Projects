
#include "MainEngine.h"

extern int fetch_data_list_single(vector<StockData*> stock_list);

extern int fetch_data_list_multi(vector<StockData*> stock_list);


void MainEngine::Initialize()
{
	// init calendar
	calendar.LoadData();

	// init stock list
	LoadStockData();
	LoadWeightData();
	stock_map = create_stock_map(stock_list);

	db.UpdateStockInfo(stock_list);

	// init groups
	groups.push_back("Beat");
	groups.push_back("Meet");
	groups.push_back("Miss");

}

void MainEngine::LoadStockData()
{
	vector<StockData*> stock_list_miss = load_stock_data(MISS_FILE, "Miss");
	vector<StockData*> stock_list_meet = load_stock_data(MEET_FILE, "Meet");
	vector<StockData*> stock_list_beat = load_stock_data(BEAT_FILE, "Beat");

	cout << "stock list Miss size: " << stock_list_miss.size() << endl;
	cout << "stock list Meet size: " << stock_list_meet.size() << endl;
	cout << "stock list Beat size: " << stock_list_beat.size() << endl;

	stock_list = combine_stock_list(stock_list_miss, stock_list_meet, stock_list_beat);

	cout << "stock list size: " << stock_list.size() << endl;
}

void MainEngine::LoadWeightData()
{
	ifstream inFile(WEIGHTS_FILE, ios::in);
	string line;

	getline(inFile, line);

	while (getline(inFile, line))
	{
		string ticker = line.substr(0, line.find_first_of(','));
		double weight = stod(line.substr(line.find_last_of(',') + 1));
		weights_map[ticker] = weight/100;
	}
}

void MainEngine::RetrieveDataSingleThread()
{

	cout << "start retrieve data (single-thread)..." << endl << endl;

	clock_t time1 = clock();

	for (auto iter : stock_list)  iter->RetrieveDataSetting(N, &calendar);

	fetch_data_list_single(stock_list);

	for (auto iter : stock_list)
	{
		cout << iter->ticker << endl;
		iter->RetrieveDataSanityCheck();
		iter->CalDailyReturns();
		//iter->DisplayData();
	}

	clock_t time2 = clock();
	double secs = (double)(time2 - time1) / CLOCKS_PER_SEC;
	cout << "run time : " << secs << " seconds" << endl;

	// update db
	//db.Connect();
	//db.DeleteTable("MarketData");
	//db.Close();
	//db.UpdateMarketData(stock_list);
	//db.UpdateMarketDataBenchmark(stock_list);
}


void MainEngine::RetrieveDataMultiThread()
{
	cout << "start retrieve data (multi-thread)..." << endl << endl;

	clock_t time1 = clock();

	for (auto iter : stock_list)  iter->RetrieveDataSetting(N, &calendar);

	fetch_data_list_multi(stock_list);

	for (auto iter : stock_list)
	{
		cout << iter->ticker << endl;
		iter->RetrieveDataSanityCheck();
		iter->CalDailyReturns();
		//iter->DisplayData();
	}

	clock_t time2 = clock();
	double secs = (double)(time2 - time1) / CLOCKS_PER_SEC;
	cout << "run time : " << secs << " seconds" << endl;

	// update db
	//db.Connect();
	//db.DeleteTable("MarketData");
	//db.Close();
	//db.UpdateMarketData(stock_list);
	//db.UpdateMarketDataBenchmark(stock_list);
}


void MainEngine::RetrieveDataFromDB()
{
	cout << "start retrieve data (from database)..." << endl << endl;

	clock_t time1 = clock();

	for (auto iter : stock_list)  iter->RetrieveDataSetting(N, &calendar);

	for (auto iter : stock_list) db.GetMarketData(iter);

	for (auto iter : stock_list)
	{
		cout << iter->ticker << endl;
		iter->RetrieveDataSanityCheck();
		iter->CalDailyReturns();
		//iter->DisplayData();
	}

	clock_t time2 = clock();
	double secs = (double)(time2 - time1) / CLOCKS_PER_SEC;
	cout << "run time : " << secs << " seconds" << endl;
}

map<string, map<string, Vector>> MainEngine::RunResearch()
{	
	map<string, vector<Vector>> AAR;
	map<string, vector<Vector>> CAAR;

	map<string, map<string, Vector>> result;

	for (int i = 0; i < RUN_BOOTSTRAP_NUM; i++)
	{
		// run bootstrap
		cout << "bootstrapping trial: " << i+1 << endl;
		map<string, vector<StockData*>> bootstrap_result = bootstrapping(stock_list, i);
		cout << bootstrap_result["Beat"][1]->ticker << endl;
		//cout << "bootstrapping finish" << endl;
		for (auto iter : groups)
		{
			AAR[iter].push_back(CalReturnForGroup(bootstrap_result[iter]));
			CAAR[iter].push_back(AAR[iter].back().cumsum());
		}

		//cout << "AAR CAAR finish" << endl;
	}

	vector<vector<Vector>> result_matrix;

	// combine bootstrap results
	for (auto iter : groups)
	{
		Matrix AAR_mean(AAR[iter]);
		Matrix CAAR_mean(CAAR[iter]);
		//cout << AAR_mean << endl; // check if random see valid
		result["AAR_mean"][iter] = Matrix(AAR[iter]).mean();
		result["CAAR_mean"][iter] = Matrix(CAAR[iter]).mean();
		result["AAR_std"][iter] = Matrix(AAR[iter]).std();
		result["CAAR_std"][iter] = Matrix(CAAR[iter]).std();
		
		vector<Vector> result_row;
		result_row.push_back(result["AAR_mean"][iter]);
		result_row.push_back(result["AAR_std"][iter]);
		result_row.push_back(result["CAAR_mean"][iter]);
		result_row.push_back(result["CAAR_std"][iter]);
		result_matrix.push_back(result_row);
	}

	research_result_matrix = result_matrix;
	research_result = result;
	return result;
}

Vector MainEngine::CalReturnForGroup(vector<StockData*> stock_list)
{
	Matrix mat(stock_list);
	Vector weights = GetWeights(stock_list);
	Vector AARt;
	if (weight_choice == 1)
	{
		AARt = mat.mean();
	}
	else if(weight_choice == 2)
	{
		AARt = mat.weighted_mean(weights);
	}
	else
	{
		cout << "Invalid weight choice, use equal weights." << endl;
		AARt = mat.mean();
	}
	
	return AARt;
}

Vector MainEngine::GetWeights(vector<StockData*> stock_list)
{
	Vector weights;
	for (auto iter : stock_list)
	{
		weights.push_back(weights_map[iter->ticker]);
	}
	return weights;
}

void MainEngine::RunMenu()
{
	while (1)
	{
		// display items
		cout << endl;
		cout << "----------Menu--------------" << endl;
		cout << "1. (Must execute before using other options) Enter N." << endl
			 << "2. Pull information for one stock." << endl
			 << "3. Show AAR, AAR-SD, CAAR and CAAR-STD for one group." << endl
			 << "4. Show the gnuplot graph with CAAR for all 3 groups." << endl
			 << "5. Exit menu." << endl << endl;

		// get input
		int choice;
		cin >> choice;

		if (choice == 1)
		{
			cout << "Please enter N:" << endl;
			int N;
			cin >> N;
			if ((N < 30) || (N > 60))
			{
				cout << "Invalid N, automatically set to N=30." << endl;
				SetN(30);
			}
			else
			{
				SetN(N);
			}

			cout << "Please enter single/multi thread download (1 for single-thread, 2 for multi-thread, 3 for db):" << endl;
			int thread_choice;
			cin >> thread_choice;

			cout << "Please enter weights for ARR (1 for equal weights, 2 for IWB weights (market-cap weights)):" << endl;
			cin >> weight_choice;

			if (thread_choice == 1)
			{
				RetrieveDataSingleThread();
			}
			else if (thread_choice == 2)
			{
				RetrieveDataMultiThread();
			}
			else if (thread_choice == 3)
			{
				RetrieveDataFromDB();
			}
			else
			{
				cout << "Invalid thread choice, use single-thread." << endl;
				RetrieveDataSingleThread();
			}
			RunResearch();
		}
		else if (choice == 2)
		{
			cout << "Please enter stock ticker:" << endl;
			string ticker;
			cin >> ticker;
			if (stock_map[ticker]) { 
				stock_map[ticker]->DisplayAttribute();
				stock_map[ticker]->DisplayData(); 
			}
			else cout << "Please enter a valid ticker. " << endl;
		}
		else if (choice == 3)
		{
			cout << "Please enter the group selection: " << endl
				<< "1. Beat group" << endl
				<< "2. Meet group" << endl
				<< "3. Miss group" << endl
				<< "4. Go back to the previous menu" << endl;

			int group_choice;
			int row_choice;
			string group_name = "";
			cin >> group_choice;
			switch (group_choice) {
			case 1:
				group_name = "Beat";
				row_choice = 0;
				break;
			case 2:
				group_name = "Meet";
				row_choice = 1;
				break;
			case 3:
				group_name = "Miss";
				row_choice = 2;
				break;
			case 4:
				break;
			default:
				cout << "Please enter a valid choice." << endl;
				continue;
			}

			vector<Vector> result_row = research_result_matrix[row_choice];

			cout << std::setw(10);
			cout << setw(6) << "Expected AAR"
				<< setw(15) << "AAR STD"
				<< setw(15) << "Expected CAAR"
				<< setw(15) << "CAAR STD"				
				<< endl;
			
			for (int i = 0; i <= result_row[0].size(); i++)
			{
				cout << setw(6) << result_row[0][i]
					<< setw(15) << result_row[1][i]
					<< setw(15) << result_row[2][i]
					<< setw(15) << result_row[3][i]					
					<< endl;
			}

		}
		else if (choice == 4)
		{
			cout << "Plotting CAAR with GNU plot..." << endl;
			plot_caar(research_result["CAAR_mean"], "CAAR mean");
			plot_caar(research_result["CAAR_std"], "CAAR std");
			plot_caar(research_result["AAR_mean"], "AAR mean");
			plot_caar(research_result["AAR_std"], "AAR std");
			
		}
		else if (choice == 5)
		{
			cout << "Exit menu." << endl;
			break;
		}
		else
		{
			cout << "Please enter a valid choice." << endl;
		}


	}

}

void MainEngine::ClearAll()
{
	for (auto itr : stock_list)
	{
		delete itr;
		itr = NULL;
	};
}

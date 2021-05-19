
#include <stdio.h>
#include <sqlite3.h>
#include "StockData.h"


static int callback(void* NotUsed, int argc, char** argv, char** azColName) {
    int i;
    for (i = 0; i < argc; i++) {
        printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
    }
    //printf("\n");
    return 0;
}

static int select_callback(void* sd, int argc, char** argv, char** azColName) 
{
    StockData* sdd = (StockData*) sd;
    for (int i = 0; i < argc; i++) 
    {
        string column = azColName[i];
        if (column == "Date")
        {
            sdd->dates.push_back(argv[i]);
        }
        else if(column == "Adj_Close")
        {
            sdd->adjclose.push_back(stod(argv[i]));
        }
        else
        {}
    }
    return 0;
}

static int select_benchmark_callback(void* sd, int argc, char** argv, char** azColName) 
{
    StockData* sdd = (StockData*)sd;
    for (int i = 0; i < argc; i++)
    {
        string column = azColName[i];
        if (column == "Date")
        {
            sdd->dates_benchmark.push_back(argv[i]);
        }
        else if (column == "Adj_Close")
        {
            sdd->adjclose_benchmark.push_back(stod(argv[i]));
        }
        else
        {
        }
    }
    return 0;
}


class DBManager
{
public:
    sqlite3* db;

    DBManager() {};

    void Connect()
    {
       
        char* zErrMsg = 0;
        int rc;

        rc = sqlite3_open("finance.db", &db);

        if (rc) {
            fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));            
        }
        else {
            //fprintf(stderr, "Opened database successfully\n");
        }
    }

    void DeleteTable(string table)
    {
        string sql;
        char* zErrMsg = 0;
        int rc;


        sql = "delete from " + table;           
        cout << sql << endl;

        rc = sqlite3_exec(db, sql.c_str(), callback, 0, &zErrMsg);
        if (rc != SQLITE_OK) {
            fprintf(stderr, "SQL error: %s\n", zErrMsg);
            sqlite3_free(zErrMsg);
        }
        else {
            //fprintf(stdout, "Records created successfully\n");
        }
    }

    void Close()
    {
        sqlite3_close(db);
    }


    void UpdateStockInfo(vector<StockData*> stock_list)
    {
        Connect();
        DeleteTable("StockInfo");
        for (auto iter : stock_list)
        {
            string sql;
            char* zErrMsg = 0;
            int rc;

            sql = "INSERT INTO StockInfo (Ticker,EPS_Estimate,EPS_Actual,EPS_Surprise,EPS_Surprise_Percent,Stock_Group,Announce_Day,Period_End) VALUES ('"               
                + iter->ticker + "',"
                + to_string(iter->estimate_eps) + ","
                + to_string(iter->actual_eps) + ","
                + to_string(iter->eps_surprise) + ","
                + to_string(iter->eps_surprise_percent) + ",'"
                + iter->group + "','"
                + iter->announce_day + "','"
                + iter->period_end + "'"
                + ")";                
           
            //cout << sql << endl;
                
            rc = sqlite3_exec(db, sql.c_str(), callback, 0, &zErrMsg);
            if (rc != SQLITE_OK) {
                fprintf(stderr, "SQL error: %s\n", zErrMsg);
                sqlite3_free(zErrMsg);
            }
            else {
                //fprintf(stdout, "Records created successfully\n");
            }
                
        }
        Close();
    }


    void UpdateMarketData(vector<StockData*> stock_list)
    {
        Connect();
        //DeleteTable("MarketData");
        for (auto iter : stock_list)
        {
            string sql;
            char* zErrMsg = 0;
            int rc;

            for (int i=0; i < iter->dates.size(); i++)
            {
                sql = "INSERT INTO MarketData (Ticker,Date,Adj_Close) VALUES ('"
                    + iter->ticker + "','"
                    + iter->dates[i] + "',"
                    + to_string(iter->adjclose[i])                    
                    + ")";

                //cout << sql << endl;

                rc = sqlite3_exec(db, sql.c_str(), callback, 0, &zErrMsg);
                if (rc != SQLITE_OK) {
                    fprintf(stderr, "SQL error: %s\n", zErrMsg);
                    sqlite3_free(zErrMsg);
                }
                else {
                    //fprintf(stdout, "Records created successfully\n");
                }
            }

        }
        Close();
    }

    void UpdateMarketDataBenchmark(vector<StockData*> stock_list)
    {
        Connect();
        //DeleteTable("MarketData");
        for (auto iter : stock_list)
        {
            string sql;
            char* zErrMsg = 0;
            int rc;

            for (int i = 0; i < iter->dates_benchmark.size(); i++)
            {
                sql = "INSERT INTO MarketData (Ticker,Date,Adj_Close) VALUES ('IWB','"
                    + iter->dates_benchmark[i] + "',"
                    + to_string(iter->adjclose_benchmark[i])
                    + ")";
                //sql = "INSERT INTO MarketData (Ticker,Date,Adj_Close) VALUES ('EQAL','"
                //    + iter->dates_benchmark[i] + "',"
                //    + to_string(iter->adjclose_benchmark[i])
                //    + ")";

                //cout << sql << endl;

                rc = sqlite3_exec(db, sql.c_str(), callback, 0, &zErrMsg);
                if (rc != SQLITE_OK) {
                    fprintf(stderr, "SQL error: %s\n", zErrMsg);
                    sqlite3_free(zErrMsg);
                }
                else {
                    //fprintf(stdout, "Records created successfully\n");
                }
            }

        }
        Close();
    }

    void GetMarketData(StockData* sd)
    {
        Connect();
        string ticker = sd->ticker;
        string start_time = sd->startTime;
        string end_time = sd->endTime;
        
        string sql;
        char* zErrMsg = 0;
        int rc;
       
        sql = "select Date, Adj_Close from MarketData where Ticker='" + ticker + "' and Date>='" + start_time + "' and Date<='" + end_time + "';";
            
        rc = sqlite3_exec(db, sql.c_str(), select_callback, sd, &zErrMsg);
        if (rc != SQLITE_OK) {
            fprintf(stderr, "SQL error: %s\n", zErrMsg);
            sqlite3_free(zErrMsg);
        }
        else {
            //fprintf(stdout, "Records created successfully\n");
        }

        sql = "select Date, Adj_Close from MarketData where Ticker='IWB' and Date>='" + start_time + "' and Date<='" + end_time + "';";
        //sql = "select Date, Adj_Close from MarketData where Ticker='EQAL' and Date>='" + start_time + "' and Date<='" + end_time + "';";

        rc = sqlite3_exec(db, sql.c_str(), select_benchmark_callback, sd, &zErrMsg);
        if (rc != SQLITE_OK) {
            fprintf(stderr, "SQL error: %s\n", zErrMsg);
            sqlite3_free(zErrMsg);
        }
        else {
            //fprintf(stdout, "Records created successfully\n");
        }
        Close();
    }


};

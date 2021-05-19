
#ifndef Constant_H
#define Constant_H

#include <string>
using namespace std;

// global
#define CALENDAR_FILE ".\\data\\US_cal.csv"
#define WEIGHTS_FILE ".\\data\\IWB_weights.csv"
#define TEST_FILE ".\\data\\Test.csv"
//#define GNU_PATH "C:\\Programs\\gnuplot\\bin\\gnuplot.exe" // wzh
#define GNU_PATH "D:\\programs\\gnuplot\\bin\\gnuplot.exe" // ck
#define THREAD_NUM 10     // number of threads for multithreading fetch data from Yahoo
#define TIME_ZONE "NYC"   // NYC=New York City, SH=Shanghai, CT=Connecticut
#define BENCHMARK_TICKER "IWB"  // IWB/EQAL

// live
#define MISS_FILE ".\\data\\Miss.csv"
#define MEET_FILE ".\\data\\Meet.csv"
#define BEAT_FILE ".\\data\\Beat.csv"
#define BOOTSTRAP_NUM 50
#define RUN_BOOTSTRAP_NUM 40

// test
//#define MISS_FILE ".\\data\\Miss_Test.csv"
//#define MEET_FILE ".\\data\\Meet_Test.csv"
//#define BEAT_FILE ".\\data\\Beat_Test.csv"
//#define BOOTSTRAP_NUM 20
//#define RUN_BOOTSTRAP_NUM 5


#endif
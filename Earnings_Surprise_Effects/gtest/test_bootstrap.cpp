#include <gtest/gtest.h>
#include "StockData.h"
#include "Utils.h"

class BootstrapTest : public ::testing::Test {
protected:
    static void SetUpTestCase() {
        //std::cout << "SetUpTestCase\n";
    }
    static void TearDownTestCase() {
        //std::cout << "TearDownTestCase\n";
    }
    virtual void SetUp() {
        //std::cout << "SetUp\n";
        stock_list_miss = load_stock_data(MISS_FILE, "Miss");
        stock_list_meet = load_stock_data(MEET_FILE, "Meet");
        stock_list_beat = load_stock_data(BEAT_FILE, "Beat");
        stock_list = combine_stock_list(stock_list_miss, stock_list_meet, stock_list_beat);
        bootstrap_result = bootstrapping(stock_list, 1);
    }
    virtual void TearDown() {
        //std::cout << "TearDown\n";
    }
    vector<StockData*> stock_list_miss, stock_list_meet, stock_list_beat, stock_list;
    map<string, vector<StockData*>> bootstrap_result;
};

TEST_F(BootstrapTest, resultSize) {

    EXPECT_EQ(50, bootstrap_result["Beat"].size());
    EXPECT_EQ(50, bootstrap_result["Meet"].size());
    EXPECT_EQ(50, bootstrap_result["Miss"].size());
}


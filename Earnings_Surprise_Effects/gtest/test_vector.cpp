#include <gtest/gtest.h>
#include "Vector.h"

class VectorTest : public ::testing::Test {
protected:
    static void SetUpTestCase() {
        //std::cout << "SetUpTestCase\n";
    }
    static void TearDownTestCase() {
        //std::cout << "TearDownTestCase\n";
    }
    virtual void SetUp() {
    }
    virtual void TearDown() {
        //std::cout << "TearDown\n";
    }

};

TEST_F(VectorTest, size) {
    vector<double> data = { 100,101,102,103,104 };
    vector<double> data2 = { 99,100,101,102,103,1 };
    Vector adjclose(data);
    Vector adjclose2(data2);

    EXPECT_EQ(5, adjclose.size());
    EXPECT_EQ(6, adjclose2.size());
}

TEST_F(VectorTest, pushBack) {
    vector<double> data = { 100,101,102,103,104 };
    Vector adjclose(data);
    adjclose.push_back(1);

    EXPECT_EQ(6, adjclose.size());

    adjclose.push_back(2);

    EXPECT_EQ(7, adjclose.size());
}

TEST_F(VectorTest, operatorOverload) {
    vector<double> data = { 100,101,102,103,104 };
    vector<double> data2 = { 99,100,101,102,103 };
    Vector adjclose(data);
    Vector adjclose2(data2);
    Vector sum = adjclose + adjclose2;
    Vector diff = adjclose - adjclose2;

    EXPECT_EQ(199, sum[0]);
    EXPECT_EQ(1, diff[1]);
}

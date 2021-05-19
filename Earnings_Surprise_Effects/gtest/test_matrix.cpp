#include <gtest/gtest.h>
#include "Vector.h"
#include "Matrix.h"

class MatrixTest : public ::testing::Test {
protected:
    static void SetUpTestCase() {
        //std::cout << "SetUpTestCase\n";
    }
    static void TearDownTestCase() {
        //std::cout << "TearDownTestCase\n";
    }
    virtual void SetUp() {
        vector<double> data1 = { 100,101,102,103,104 };
        vector<double> data2 = { 99,100,101,102,103 };
        Vector vec1(data1);
        Vector vec2(data2);
        vec_vec.push_back(vec1);
        vec_vec.push_back(vec2);
        mat = Matrix(vec_vec);

    }
    virtual void TearDown() {
        //std::cout << "TearDown\n";
    }

    vector<Vector> vec_vec;
    Matrix mat;
};

TEST_F(MatrixTest, sum) {
    
    EXPECT_EQ(199, mat.sum()[0]);
    EXPECT_EQ(201, mat.sum()[1]);
}

TEST_F(MatrixTest, mean) {

    EXPECT_EQ(99.5, mat.mean()[0]);
    EXPECT_EQ(100.5, mat.mean()[1]);
}

TEST_F(MatrixTest, weighted_mean) {

    vector<double> w = { 1,3 };
    Vector weight(w);
    EXPECT_EQ(100.25, mat.weighted_mean(weight)[1]);
    EXPECT_EQ(103.25, mat.weighted_mean(weight)[4]);
}

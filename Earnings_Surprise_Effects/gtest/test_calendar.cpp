#include <gtest/gtest.h>
#include "CalendarManager.h"

class CalendarManagerTest : public ::testing::Test {
protected:
    static void SetUpTestCase() {
        //std::cout << "SetUpTestCase\n";
    }
    static void TearDownTestCase() {
        //std::cout << "TearDownTestCase\n";
    }
    virtual void SetUp() {
        //CalendarManager calendar;
        calendar.LoadData();
        //std::cout << "SetUp\n";
    }
    virtual void TearDown() {
        //std::cout << "TearDown\n";
    }
    CalendarManager calendar;
};

TEST_F(CalendarManagerTest, prevDays) {
    EXPECT_EQ("2018-12-11", calendar.PrevNDays("2018-12-14", 3));
    EXPECT_EQ("2020-10-16", calendar.PrevNDays("2020-12-14", 40));
}

TEST_F(CalendarManagerTest, nextDays) {
    EXPECT_EQ("2021-04-22", calendar.NextNDays("2021-04-19", 3));
    EXPECT_EQ("2020-07-15", calendar.NextNDays("2020-04-19", 60));
}

TEST_F(CalendarManagerTest, nextDaysOutOfBound) {
    EXPECT_EQ("2021-04-27", calendar.NextNDays("2021-04-10", 30));
    EXPECT_EQ("2021-04-27", calendar.NextNDays("2021-04-19", 60));
}
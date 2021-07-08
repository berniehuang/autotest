#include"Sample_Math.h"
#include <gtest/gtest.h>

class Test_Sample_Math: public testing::Test
{
    protected:
        Sample_Math*  _p_a;

    virtual void SetUp()
    {
        this->_p_a = new Sample_Math(1);
    }
    virtual void TearDown()
    {
        delete this->_p_a;
    }
};

TEST_F(Test_Sample_Math, add)
{
    EXPECT_EQ(1, _p_a->getA());
    _p_a->add(3);
    EXPECT_EQ(4, _p_a->getA());
}

TEST_F(Test_Sample_Math, dec)
{
    EXPECT_EQ(1, _p_a->getA());
    _p_a->dec(100);
    EXPECT_EQ(-99, _p_a->getA());
}

TEST_F(Test_Sample_Math, check_private_data )
{
    _p_a->_a = 100;
    EXPECT_EQ(110, _p_a->AccessPrivate(10));
}

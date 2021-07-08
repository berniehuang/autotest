#include <limits.h>
#include "Sample_Algorithm.h"
#include <gtest/gtest.h>

TEST(Test_Sample_Algorithm, Factorial_Negative)
{
  EXPECT_EQ(1, Factorial(-5));
  EXPECT_TRUE(Factorial(-10) > 0);
}

TEST(Test_Sample, Factorial_Zero)
{
  EXPECT_EQ(1, Factorial(0));
}

TEST(Test_Sample, Factorial_Positive)
{
  EXPECT_EQ(1, Factorial(1));
  EXPECT_EQ(2, Factorial(2));
  EXPECT_EQ(6, Factorial(3));
  EXPECT_EQ(40320, Factorial(8));
}

TEST(Test_Sample, IsPrime_Negative) {
  EXPECT_FALSE(IsPrime(-2));
  EXPECT_FALSE(IsPrime(INT_MIN));
}

TEST(Test_Sample, IsPrime_Trivial) {
  EXPECT_FALSE(IsPrime(0));
  EXPECT_TRUE(IsPrime(2));
  EXPECT_TRUE(IsPrime(3));
  EXPECT_FALSE(IsPrime(9));
  EXPECT_TRUE(IsPrime(13));
}

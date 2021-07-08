#include <iostream>
#include "Sample_Math.h"

using namespace std;

Sample_Math::Sample_Math(int a)
{
    this->_a = a;
}

Sample_Math::~Sample_Math()
{
}

void Sample_Math::add(int a)
{
    this->_a += a;
}

int Sample_Math::getA()
{
    return this->_a;
}

void Sample_Math::dec(int a)
{
    this->_a -= a;
}

int Sample_Math::AccessPrivate(int b)
{
    cout << "b=" << b << ", _a=" <<this->_a<< ", b+_a=" << b+this->_a << endl;
    return b+this->_a;
}

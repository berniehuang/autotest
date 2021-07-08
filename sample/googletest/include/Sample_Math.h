#ifndef _SAMPLE_MATH_H
#define _SAMPLE_MATH_H

class Sample_Math
{
private:
    int _a;
    virtual int AccessPrivate(int b);

public:
    Sample_Math();
    Sample_Math(int a);
    virtual ~Sample_Math();
    virtual void add(int a);
    virtual void dec(int a);
    virtual int getA();

};

#endif

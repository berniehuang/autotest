package com.example.foo;

public class Foo {
    public boolean isEvenNumber(int number){
        boolean result = false;
        if(number%2 == 0){
            result = true;
        }
        return result;
    }

    public int Factorial(int number){
        int result = 1;
        for (int i = 1; i <= number; i++){
            result *= i;
        }
        return result;
    }

    public boolean IsPrime(int number){
        if (number <= 1){
            return false;
        }

        if (number % 2 == 0){
            return number == 2;
        }

        for (int i = 3; ;i += 2){
            if (i > number/i){
                break; 
            }
            if(number % i == 0){
                return false;
            }
        }
        return true;
    }
}

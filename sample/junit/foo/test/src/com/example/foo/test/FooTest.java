package com.example.foo.test;
import com.example.foo.Foo;

import android.support.test.runner.AndroidJUnit4;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.hamcrest.Matchers.is;
import static org.junit.Assert.assertEquals;


@RunWith(AndroidJUnit4.class)
public class FooTest {
    @Test
    public void testEvenOddNumber(){
        Foo foo = new Foo();
        assertEquals("10 is a even number", true, foo.isEvenNumber(10));
    }
}

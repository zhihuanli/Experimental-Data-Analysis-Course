# A short introduction to C++ - Advanced 

* Part 0: Dynamic memory allocation
* Part 1: Namespace
* Part 2: Using functions
* Part 3: Classes
* Part 4: Organize codes into modules

## Part 0. Dynamic memory allocation (动态内存分配)

Allocating memory at run-time with `new`:

* New file! `dynamic_array.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    int n = 5;
    int *array = new int[n];

    for (int i = 0; i < n; i++) {
        array[i] = i * i;
    }

    for (int i = 0; i < n; i++) {
        cout << "array[" << i << "] = " << array[i] << endl;
    }

    delete[] array;
    array = nullptr;
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 dynamic_array.cpp -o dynamic_array
  ./dynamic_array
  ```

Operator `delete` releases dynamic memory previously allocated with `new`.

A common problem in programs is a memory leak:

* if there is no matching `delete` / `delete[]`, memory is allocated but never released.

---

## Part 1. Namespaces

Single global namespace is often a bad idea.

* There can be naming conflicts.
* The namespace feature in C++ allows you to explicitly control the scope of your symbols.

* New file! `namespace_demo.cpp`

```cpp
#include <iostream>

namespace foo
{
    int global = 7;

    void func()
    {
        std::cout << "foo::global = " << global << std::endl;
    }
}

int main()
{
    std::cout << "Access with scope operator: " << foo::global << std::endl;
    foo::func();

    using std::cout;
    using std::endl;
    cout << "Selected symbols from std also work." << endl;
    return 0;
}
```

* All symbols in the Standard Library are wrapped in the namespace `std`.
* Compile and run:
  ```bash
  g++ -std=c++17 namespace_demo.cpp -o namespace_demo
  ./namespace_demo
  ```

---

## Part 2. Using functions

### 2. Function overloading (函数重载)

Often algorithms have different implementations with the same functionality. Overloaded functions have the same name, but different argument lists.

* New file! `minimum3.cpp`

```cpp
#include <iostream>

using namespace std;

int minimum3(int a, int b, int c)
{
    return (a < b ? (a < c ? a : c) : (b < c ? b : c));
}

float minimum3(float a, float b, float c)
{
    return (a < b ? (a < c ? a : c) : (b < c ? b : c));
}

int main()
{
    int a = 3, b = 5, c = 1;
    float x = 4.5f, y = 1.2f, z = -3.0f;

    int d = minimum3(a, b, c);
    float w = minimum3(x, y, z);

    cout << "minimum3 for int = " << d << endl;
    cout << "minimum3 for float = " << w << endl;
    return 0;
}
```

* Compiler selects the appropriate overloaded function based on the argument list.
* Compile and run:
  ```bash
  g++ -std=c++17 minimum3.cpp -o minimum3
  ./minimum3
  ```

### 3. Passing Arguments

#### 3.1 Pass by value, reference and pointer

* New file! `swap_demo.cpp`

```cpp
#include <iostream>

using namespace std;

void swap_by_value(int a, int b)
{
    int tmp = a;
    a = b;
    b = tmp;
}

void swap_by_reference(int &a, int &b)
{
    int tmp = a;
    a = b;
    b = tmp;
}

void swap_by_pointer(int *a, int *b)
{
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int main()
{
    int a = 3, b = 5;

    swap_by_value(a, b);
    cout << "After swap_by_value: a=" << a << ", b=" << b << endl;

    swap_by_reference(a, b);
    cout << "After swap_by_reference: a=" << a << ", b=" << b << endl;

    swap_by_pointer(&a, &b);
    cout << "After swap_by_pointer: a=" << a << ", b=" << b << endl;
    return 0;
}
```

* `swap_by_value` does not change the original variables.
* `swap_by_reference` and `swap_by_pointer` do change the originals.
* In general: use references when you can, pointers when you have to.
* Compile and run:
  ```bash
  g++ -std=c++17 swap_demo.cpp -o swap_demo
  ./swap_demo
  ```

#### 3.2 Passing arrays as function parameters

* New file! `array_to_function.cpp`

```cpp
#include <iostream>

using namespace std;

void fun(int *arr, unsigned int n)
{
    for (unsigned int i = 0; i < n; i++) {
        cout << " " << arr[i];
    }
    cout << endl;
}

int main()
{
    int arr[] = {1, 2, 3, 4, 5, 6, 7, 8};
    unsigned int n = sizeof(arr) / sizeof(arr[0]);

    fun(arr, n);
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 array_to_function.cpp -o array_to_function
  ./array_to_function
  ```

---

## Part 3. Classes

### 4. Constructor, member function, destructor

A class representing a vector in 2-D.

* New file! `vector_class.cpp`

```cpp
#include <cmath>
#include <iostream>

using namespace std;

class Vector
{
  public:
    Vector();
    Vector(double x, double y);
    ~Vector();

    double x() const { return m_x; }
    double y() const { return m_y; }
    double r() const { return sqrt(m_x * m_x + m_y * m_y); }
    double theta() const { return atan2(m_y, m_x); }

    void setX(double x) { m_x = (x < 0 ? -x : x); }
    void setY(double y) { m_y = (y < 0 ? -y : y); }
    void setR(double r);
    void setTheta(double theta);

  private:
    double m_x;
    double m_y;
};

Vector::Vector() : m_x(0.0), m_y(0.0)
{
    cout << "default constructor" << endl;
}

Vector::Vector(double x, double y)
{
    setX(x);
    setY(y);
    cout << "constructor with parameters" << endl;
}

Vector::~Vector()
{
    cout << "destructor for Vector(" << m_x << ", " << m_y << ")" << endl;
}

void Vector::setR(double r_new)
{
    double old_r = r();
    if (old_r == 0.0) {
        m_x = r_new;
        m_y = 0.0;
        return;
    }

    double scale = r_new / old_r;
    m_x *= scale;
    m_y *= scale;
}

void Vector::setTheta(double theta_new)
{
    double radius = r();
    m_x = radius * cos(theta_new);
    m_y = radius * sin(theta_new);
}

int main()
{
    Vector u;
    Vector v(1.5, 3.7);

    v.setX(2.9);
    v.setR(10.0);

    cout << "v.x = " << v.x() << endl;
    cout << "v.y = " << v.y() << endl;
    cout << "v.r = " << v.r() << endl;
    cout << "v.theta = " << v.theta() << endl;

    Vector *vPtr = new Vector(3.0, 4.0);
    cout << "vPtr->r() = " << vPtr->r() << endl;
    delete vPtr;

    return 0;
}
```

* A constructor has the same name as the class and no return type.
* The destructor is called automatically when an object goes out of scope; for dynamically allocated objects, it is called when `delete` is used.
* `m_x` and `m_y` are declared `private`, so they cannot be accessed directly outside the class.
* Compile and run:
  ```bash
  g++ -std=c++17 vector_class.cpp -o vector_class
  ./vector_class
  ```

### 5. Inheritance (继承)

Inheritance is a technique to build a new class based on an old class.

* New file! `inheritance_demo.cpp`

```cpp
#include <iostream>

using namespace std;

class Point
{
  public:
    void InitP(float xx = 0, float yy = 0)
    {
        X = xx;
        Y = yy;
    }

    void Move(float xOff, float yOff)
    {
        X += xOff;
        Y += yOff;
    }

    float GetX() const { return X; }
    float GetY() const { return Y; }

  private:
    float X = 0;
    float Y = 0;
};

class Rectangle : public Point
{
  public:
    void InitR(float x, float y, float w, float h)
    {
        InitP(x, y);
        W = w;
        H = h;
    }

    float GetH() const { return H; }
    float GetW() const { return W; }

  private:
    float W = 0;
    float H = 0;
};

int main()
{
    Rectangle rect;
    rect.InitR(2, 3, 20, 10);
    rect.Move(3, 2);

    cout << "The data of rect(X,Y,W,H):" << endl;
    cout << rect.GetX() << ", "
         << rect.GetY() << ", "
         << rect.GetW() << ", "
         << rect.GetH() << endl;
    return 0;
}
```

* `Rectangle` inherits public members from `Point`.
* Compile and run:
  ```bash
  g++ -std=c++17 inheritance_demo.cpp -o inheritance_demo
  ./inheritance_demo
  ```

### 6. Virtual function （虚拟函数）

Often derived classes behave differently. Virtual functions make runtime polymorphism possible.

* New file! `virtual_function_demo.cpp`

```cpp
#include <iostream>
#include <string>

using namespace std;

class TDish
{
  public:
    virtual ~TDish() = default;
    virtual bool ForSoup() const = 0;
    virtual string Name() const = 0;

    void SetFull() { m_full = true; }
    bool IsFull() const { return m_full; }

  private:
    bool m_full = false;
};

class TPlate : public TDish
{
  public:
    bool ForSoup() const override { return false; }
    string Name() const override { return "Plate"; }
};

class TBowl : public TDish
{
  public:
    bool ForSoup() const override { return true; }
    string Name() const override { return "Bowl"; }
};

void FillWithSoup(TDish *dish)
{
    if (dish->ForSoup()) {
        dish->SetFull();
    }
}

int main()
{
    TDish *a = new TPlate();
    TDish *b = new TBowl();

    FillWithSoup(a);
    FillWithSoup(b);

    cout << a->Name() << " full? " << a->IsFull() << endl;
    cout << b->Name() << " full? " << b->IsFull() << endl;

    delete a;
    delete b;
    return 0;
}
```

* This example is deliberately simple, but the idea will appear again when we work with ROOT base classes and derived classes.
* Compile and run:
  ```bash
  g++ -std=c++17 virtual_function_demo.cpp -o virtual_function_demo
  ./virtual_function_demo
  ```

---

## Part 4. Organize codes into modules

Usually it is not convenient to keep all C++ source code in a single file.

* Split source code into multiple files.
* Use header files (`.h` / `.hh`) for declarations.
* Use source files (`.cc` / `.cpp`) for definitions.
* Protect header files with include guards.

### 7. Typical layout of a module

* `capitalize.hh`

```cpp
#ifndef CAPITALIZE_HH
#define CAPITALIZE_HH

void convertUpper(char *str);
void convertLower(char *str);

#endif
```

* `capitalize.cc`

```cpp
#include "capitalize.hh"

void convertUpper(char *ptr)
{
    while (*ptr) {
        if (*ptr >= 'a' && *ptr <= 'z') {
            *ptr -= ('a' - 'A');
        }
        ptr++;
    }
}

void convertLower(char *ptr)
{
    while (*ptr) {
        if (*ptr >= 'A' && *ptr <= 'Z') {
            *ptr += ('a' - 'A');
        }
        ptr++;
    }
}
```

* `use_capitalize.cpp`

```cpp
#include <iostream>
#include "capitalize.hh"

using namespace std;

int main()
{
    char text1[] = "Root Tutorial I";
    char text2[] = "ROOT Tutorial II";

    convertUpper(text1);
    convertLower(text2);

    cout << text1 << endl;
    cout << text2 << endl;
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 use_capitalize.cpp capitalize.cc -o use_capitalize
  ./use_capitalize
  ```


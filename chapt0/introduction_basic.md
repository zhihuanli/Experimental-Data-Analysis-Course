# A short introduction to C++ - basic 

* Part 0: Setting up C++
* Part 1: Hello world! Your first steps with C++
* Part 2: Files, arrays and functions
* Part 3: Pointers, arguments and classes

## Part 0. Setting up C++

OS: Linux / Mac OS / WSL

We are going to have two windows open at the same time:

1. A text editor (vi, emacs, vscode etc).
2. The command line or terminal, where a C++ compiler has already been installed and is working.

### 1. Getting ready

1. Create a new directory called `cpp`:
   ```bash
   mkdir cpp
   cd cpp
   ```
2. In this chapter, every example can be compiled with:
   ```bash
   g++ -std=c++17 filename.cpp -o program_name
   ```
3. Then run with:
   ```bash
   ./program_name
   ```

---

## Part 1. Hello world!

### 2. Hello world!

For `cin`, `cout`, `endl` stuff, we need the `<iostream>` library. Libraries are like toolboxes.

* New file! `helloworld.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    cout << "Hello world!" << endl;
    return 0;
}
```

* Save as `helloworld.cpp`.
* Compile:
  ```bash
  g++ -std=c++17 helloworld.cpp -o hello
  ```
* Run:
  ```bash
  ./hello
  ```

`return 0;` in the `main` function means the program executed successfully.

### 3. Use of variables

* New file! `variables.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    double x = 3.141;
    double y = 1.618;
    auto j = 16;      // j is int
    auto k = 2.3;     // k is double
    auto good = true; // good is bool

    cout << "The value of x is " << x
         << " and the value of y is " << y << endl;
    cout << "j = " << j << ", k = " << k
         << ", good = " << good << endl;
    return 0;
}
```

* `auto` declaration type (since C++11): the type is deduced from the initializer.
* Compile and run:
  ```bash
  g++ -std=c++17 variables.cpp -o variables
  ./variables
  ```

### 4. Command-line input

* New file! `height.cpp`
* We are going to use strings here, which need the `<string>` library.

```cpp
#include <iostream>
#include <string>

using namespace std;

int main()
{
    string name;
    double height;

    cout << "What is your name?" << endl;
    cin >> name;

    cout << "What is your height (in metres)?" << endl;
    cin >> height;

    cout << name << " is " << height << " metres tall." << endl;
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 height.cpp -o height
  ./height
  ```

### 5. Maths

* New file! `calculator.cpp`

```cpp
#include <cmath>
#include <iostream>

using namespace std;

int main()
{
    double x;

    cout << "Enter a number" << endl;
    cin >> x;

    cout << "That number squared is " << pow(x, 2) << endl;
    if (x >= 0) {
        cout << "The square root of that number is " << sqrt(x) << endl;
    } else {
        cout << "The square root is not a real number." << endl;
    }

    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 calculator.cpp -o calculator
  ./calculator
  ```

### 6. If

* New file! `bartender.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    int age;

    cout << "Welcome to the pub." << endl;
    cout << "What is your age?" << endl;
    cin >> age;

    if (age > 18) {
        cout << "Have a pint!" << endl;
    } else if (age == 18) {
        cout << "Show me your ID and then have a pint!" << endl;
    } else {
        cout << "I'm calling the police." << endl;
    }

    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 bartender.cpp -o bartender
  ./bartender
  ```

### 7. For and while loops

* New file! `square_numbers.cpp`

```cpp
#include <cmath>
#include <iostream>

using namespace std;

int main()
{
    int n = 10;

    cout << "Squares from a for loop:" << endl;
    for (int i = 0; i < n; i++) {
        cout << i << "^2 = " << pow(i, 2) << endl;
    }

    cout << endl;
    cout << "Cubes from a while loop:" << endl;
    int i = 3;
    while (i < n) {
        cout << i << "^3 = " << pow(i, 3) << endl;
        i++;
    }

    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 square_numbers.cpp -o square_numbers
  ./square_numbers
  ```

---

## Part 2. Files, arrays and functions

### 8. Saving and reading data

To save and read files, we need to include the `<fstream>` library.

* New file! `save_to_file.cpp`

```cpp
#include <fstream>
#include <iostream>

using namespace std;

int main()
{
    ofstream myfile("greeting.txt");
    if (!myfile) {
        cerr << "Cannot open greeting.txt for writing." << endl;
        return 1;
    }

    myfile << "header line 1" << endl;
    myfile << "header line 2" << endl;
    myfile << "header line 3" << endl;

    int datapoint = 10;
    myfile << datapoint << endl;

    for (int i = 0; i < datapoint; ++i) {
        myfile << i << "  " << 0.01 + 0.2 * i + 0.03 * i * i << endl;
    }

    myfile.close();
    cout << "Data saved to greeting.txt" << endl;
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 save_to_file.cpp -o save_to_file
  ./save_to_file
  ```

Your turn:

* Create another file, for example `save_to_file2.cpp`, where you print the first 10 squares to a text file.
* Run your program again. What can you say about how it writes to the text file?
* Replace
  ```cpp
  ofstream myfile("square_numbers.txt");
  ```
  with
  ```cpp
  ofstream myfile("square_numbers.txt", ios_base::app);
  ```
  if you want to append to the end of a text file, rather than overwrite.

* New file! `read_from_file.cpp`

```cpp
#include <fstream>
#include <iostream>
#include <string>

using namespace std;

int main()
{
    string line;
    ifstream myfile("greeting.txt");
    if (!myfile) {
        cerr << "Cannot open greeting.txt for reading." << endl;
        return 1;
    }

    for (int i = 0; i < 3; i++) {
        getline(myfile, line);
        cout << line << endl;
    }

    int datapoint;
    myfile >> datapoint;
    cout << "point: " << datapoint << endl;

    int x[1000];
    double y[1000];
    int count = 0;

    while (myfile >> x[count] >> y[count]) {
        cout << count << " " << x[count] << " " << y[count] << endl;
        count++;
    }

    if (datapoint != count) {
        cout << "data miss" << endl;
    } else {
        cout << "read all data." << endl;
    }

    myfile.close();
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 read_from_file.cpp -o read_from_file
  ./read_from_file
  ```

> Note: this version uses `while (myfile >> x[count] >> y[count])`, which is safer than checking `eof()` first.

### 9. Arrays

* New file! `array_square_numbers.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    int n = 10;
    int square_numbers[10];
    int favourite_numbers[10] = {3, 1, -4, 1};

    for (int i = 0; i < n; i++) {
        square_numbers[i] = i * i;
    }

    cout << "square_numbers:" << endl;
    for (int i = 0; i < n; i++) {
        cout << square_numbers[i] << endl;
    }

    cout << endl;
    cout << "favourite_numbers:" << endl;
    for (int i = 0; i < n; i++) {
        cout << favourite_numbers[i] << endl;
    }

    int magic_square[3][3] = {
        {4, 9, 2},
        {3, 5, 7},
        {8, 1, 6}
    };

    cout << endl;
    cout << "magic_square[1][1] = " << magic_square[1][1] << endl;
    return 0;
}
```

* Note you cannot directly `cout` an array.
* We can also declare:
  ```cpp
  int favourite_numbers[] = {3, 1, -4, 1};
  ```
* Compile and run:
  ```bash
  g++ -std=c++17 array_square_numbers.cpp -o array_square_numbers
  ./array_square_numbers
  ```

### 10. Functions

Writing functions allows us to do more complicated things.

* New file! `learning_functions.cpp`

```cpp
#include <iostream>

using namespace std;

int sign_function(int n);

int main()
{
    int n = -7;
    cout << "sign_function(" << n << ") = " << sign_function(n) << endl;
    return 0;
}

int sign_function(int n)
{
    int sign;

    if (n > 0) {
        sign = 1;
    } else if (n == 0) {
        sign = 0;
    } else {
        sign = -1;
    }

    return sign;
}
```

* Global and local variables.
* Note: order is important. What happens if you define `sign_function` after `main` without a declaration?
* The line
  ```cpp
  int sign_function(int n);
  ```
  is a forward declaration.
* Compile and run:
  ```bash
  g++ -std=c++17 learning_functions.cpp -o learning_functions
  ./learning_functions
  ```

---

## Part 3. Pointers, arguments and classes

### 11. Pointers

* New file! `pointers.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    int x = 10;
    int *p = &x;

    cout << "Value of x is " << x << endl;
    cout << "Address of x is " << &x << endl;
    cout << "Address stored in p is " << p << endl;
    cout << "Value of *p is " << *p << endl;

    x = 25;
    cout << "After changing x, *p = " << *p << endl;
    return 0;
}
```

* The `&` sign indicates an address in memory.
* A pointer is a variable whose value is the address of another variable, and is notated with a `*`.

* New file! `pointer_array.cpp`

```cpp
#include <iostream>

using namespace std;

int main()
{
    int primes[3] = {2, 3, 5};
    int *p = primes;

    for (int i = 0; i < 3; i++) {
        cout << "Address of primes[" << i << "] is " << p << endl;
        cout << "Value of primes[" << i << "] is " << *p << endl;
        p++;
    }

    cout << "*(primes + 2) = " << *(primes + 2) << endl;
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 pointers.cpp -o pointers
  ./pointers
  
  g++ -std=c++17 pointer_array.cpp -o pointer_array
  ./pointer_array
  ```

### 12. Main function with arguments

If you want to access command-line arguments, you can declare `main()` as follows.

* New file! `main_arg.cpp`

```cpp
#include <iostream>

using namespace std;

int main(int argc, char *argv[])
{
    cout << "argc == " << argc << '\n';
    for (int i = 0; i < argc; i++) {
        cout << "argv[" << i << "] == " << argv[i] << '\n';
    }
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 main_arg.cpp -o main_arg
  ./main_arg table_in.dat table_out.dat
  ```

Typical output:
```text
argc == 3
argv[0] == ./main_arg
argv[1] == table_in.dat
argv[2] == table_out.dat
```

This form will be useful later when you want to read input files and write output files from the terminal.

### 13. Classes

Classes are one of the main things that separate C++ from C. Classes are ways for us to set up objects that have properties and functions which are particular to that type of object. A class is something like a user-defined data type.

* New file! `rectangles.cpp`

```cpp
#include <iostream>

using namespace std;

class Rectangle
{
  public:
    double width;
    double height;

    double area() { return width * height; }
    double perimeter() { return 2.0 * (width + height); }
    void set_dimensions(double x, double y);
};

void Rectangle::set_dimensions(double x, double y)
{
    width = x;
    height = y;
}

int main()
{
    Rectangle Rec1;
    Rectangle Rec2;

    Rec1.set_dimensions(5.0, 6.0);
    Rec2.set_dimensions(10.0, 12.0);

    cout << "Area of Rec1: " << Rec1.area() << endl;
    cout << "Perimeter of Rec1: " << Rec1.perimeter() << endl;
    cout << "Area of Rec2: " << Rec2.area() << endl;
    cout << "Perimeter of Rec2: " << Rec2.perimeter() << endl;
    return 0;
}
```

* `area()` and `perimeter()` are member functions.
* `set_dimensions()` shows another way of defining a member function outside the class body.
* Compile and run:
  ```bash
  g++ -std=c++17 rectangles.cpp -o rectangles
  ./rectangles
  ```

If you want to use `Rectangle` in many files, it is annoying to define it every time. In actual usage, the declaration of the class usually goes into a header file, and the definitions of member functions go into a source file.

* `rectangle.h`

```cpp
#ifndef RECTANGLE_H
#define RECTANGLE_H

class Rectangle
{
  public:
    Rectangle();
    Rectangle(double w, double h);

    double area() const;
    double perimeter() const;
    void set_dimensions(double x, double y);

  private:
    double width;
    double height;
};

#endif
```

* `rectangle.cc`

```cpp
#include "rectangle.h"

Rectangle::Rectangle() : width(0.0), height(0.0) {}

Rectangle::Rectangle(double w, double h) : width(w), height(h) {}

double Rectangle::area() const
{
    return width * height;
}

double Rectangle::perimeter() const
{
    return 2.0 * (width + height);
}

void Rectangle::set_dimensions(double x, double y)
{
    width = x;
    height = y;
}
```

* `rectangles_module.cpp`

```cpp
#include <iostream>
#include "rectangle.h"

using namespace std;

int main()
{
    Rectangle Rec1;
    Rectangle Rec2(10.0, 12.0);

    Rec1.set_dimensions(5.0, 6.0);

    cout << "Area of Rec1: " << Rec1.area() << endl;
    cout << "Perimeter of Rec1: " << Rec1.perimeter() << endl;
    cout << "Area of Rec2: " << Rec2.area() << endl;
    cout << "Perimeter of Rec2: " << Rec2.perimeter() << endl;
    return 0;
}
```

* Compile and run:
  ```bash
  g++ -std=c++17 rectangles_module.cpp rectangle.cc -o rectangles_module
  ./rectangles_module
  ```

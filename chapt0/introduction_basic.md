# A short introduction to C++  - basic

* **Part 0:** Setting up C++
* **Part 1:** Hello world! Your first steps with C++
* **Part 2:** Arrays, files and functions
* **Part 3:** Pointers and classes 



## Part 0. Setting up C++

OS:  Linux / Mac OS

We are going to have two windows open at the same time:

1. A text editor (vi, emacs, vscode etc.)
2. The command line or terminal, where a C++ compiler has already been installed and is working

## Part 1. Hello world!

### 1. Getting ready

1. Create a new directory (folder) in your working directory called `cpp` by typing `mkdir cpp`. 
2. Change directory to your new `cpp` directory by typing `cd cpp`

### 2. Hello world!

For `cin` `cout` `endl`  stuff, we need the `<iostream>` library. Libraries are like toolboxes.

```c++
#include <iostream> //**
using namespace std; //**

int main()
{
    cout << "Hello world!" << endl;
    return 0;
}
```

* Save as `helloworld.cpp` (colours!)
* Compile by going to the command line and typing

```bash
g++ helloworld.cpp -o hello
```
* Then run the program.
```bash
./hello
```

### 3. Use of variables
```c++
#include <iostream>
using namespace std;

int main()
{
    double x;
    double y;
    x = 3.141;
    y = 1.618;
    cout << "The value of x is " << x << " and the value of y is " << y << endl;
    return 1;
}
```
- `auto` declaration type since C++ 2011

  - the type is deduced from the initializer。

    ```cpp
    autoj=16; //j is integer 
    autoj=2.3; //j is double 
    autoj=true; //j is bool
    ```

    

* Compile and run.

### 4. Command-line input
* New file! `height.cpp`. Note that we're going to use strings here, which need the `<string>` library.
```c++
#include <iostream>
#include <string>
using namespace std;

int main()
{
    string name;
    double height;
    cout << "What is your name?" << endl;
    cin >> name;
    cout << "What is your height?" << endl;
    cin >> height;
    cout << name << " is " << height << " metres tall." << endl;
    return 1;
}
```
* Compile and run.

### 5. Maths
* New file! `calculator.cpp`
```c++
#include <iostream>
#include <cmath>
using namespace std;

int main()
{
    double x;
    cout << "Enter a number" << endl;
    cin >> x;
    cout << "That number squared is " << pow(x,2) << endl;
    cout << "The square root of that number is " << sqrt(x) << endl;
    return 1;
}
```

### 6. If
* New file! `bartender.cpp`
```c++
#include <iostream>
using namespace std;

int main()
{
    int age;
    cout << "Welcome to the pub." << endl;
    cout << "What is your age?" << endl;
    cin >> age;
		if(age > 18){
    	cout << "Have a pint!" << endl;
		} else if(age == 18){
    	cout << "Show me your ID and then have a pint!" << endl;
		} else {
   	 	cout << "I'm calling the police." << endl;
		}
    return 1;
}
```
* Compile and run

  
### 7. For and while loops
* New file! `square_numbers.cpp`
```c++
#include <iostream>
#include <cmath>
using namespace std;

int main()
{
    int n = 10;
    for(int i=0; i<n; i++){
        cout << pow(i,2) << endl;
    }
    return 1;
}
```
* Compile and run!

* Change the file: let's **comment out** the for loop above and instead write it as a while loop.
```c++
int i=3; // We can define and initialise a variable at the same time.
while(i<n){
    cout << pow(i,3) << endl;
    i++;
}
```

### 8. Main function with arguments

If you want to access command line arguments you can declare main() as follows 

New file! `main_arg.cpp`

```cpp
#include <iostream>
using namespace std;

int main(int argc, char *argv[])
{
    cout << "argc == " << argc << '\n'; 
    for(int i=0; i< argc; i++) {
        cout << "argv[" << i << "] == " << argv[i] << '\n';
    }
    return 1
}
```

- compile and run

  - `g++ main_arg.cpp -o main_arg`

  - `./main_arg table_in.dat table_out.dat`

    - ```bash
      argc == 3
      argv[0] == ./main_arg
      argv[1] == table_in.dat
      argv[2] == table_out.dat
      ```



## Part 2. Files, arrays and functions

### 9. Saving and reading data

To save and read files, we need to include the `<fstream>` library.

* New file! `save_to_file.cpp`

```c++
#include <iostream>
#include <fstream>
using namespace std;

int main()
{
    ofstream myfile;
    myfile.open ("greeting.txt");
    myfile << "Hello there!" << endl;
    myfile.close();

    return 1;
}
```

Your turn:
* Create a new file, `save_to_file2.cpp`, where you print the first 10 squares to a text file called `square_numbers.txt`.
* Run your program again. What can you say about how it writes to the text file?
* Replace `myfile.open ("square_numbers.txt");` with `myfile.open ("square_numbers.txt", ios_base::app);` to make C++ append to the end of a text file, rather than overwrite.



* New file! `read_from_file.cpp`

```c++
#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main()
{
    string line;
    ifstream myfile;
    myfile.open ("greeting.txt");
    while (getline(myfile,line)){
        cout << line << endl;
    }
    myfile.close();

    return 1;
}
```

### 10. Arrays

* Edit `square_numbers.cpp`
```c++
#include <iostream>
#include <cmath>
using namespace std;

int main()
{
    int n = 10;
    int square_numbers[10];
    for(int i=0; i<n; i++){
        square_numbers[i] = pow(i,2);
    }
    for(int i=0; i<n; i++){
        cout << square_numbers[i] << endl;
    }    
    return 1;
}
```
* Note you can't `cout` an array
* We can also define arrays like this:
```c++
int main()
{
    int n = 10;
    int square_numbers[10];
    int favourite_numbers[10] = {3, 1, -4, 1}; // Note we haven't defined them all.;

    for(int i=0; i<n; i++){
        square_numbers[i] = pow(i,2);
    }

    for(int i=0; i<n; i++){
        cout << square_numbers[i] << endl;
    }    
    for(int i=0; i<n; i++){
        cout << favourite_numbers[i] << endl;
    }        

    return 0;
}
```
* You can only use curly brackets like this at initialisation time.

* We can also declare:
    * ```cpp
      int favourite_numbers[] = {3,1,-4,1};
      ```
    
* Multidimensional arrays work too
    * ```cpp
      int magic_square[3][3] = {{4,9,2},{3,5,7},{8,1,6}};
      ```

### 11. Functions 

Writing functions allows us to do more complicated things.

* New file! `learning_functions.cpp`

```c++
#include <iostream>
using namespace std;

int sign_function(int n)
{
    int sign;
    if(n>0){
        sign = 1;
    } else if(n==0){
        sign = 0;
    } else {
        sign = -1;
    }
    return sign;
}

int main()
{
    int n;
    n = 3;
    cout << sign_function(n) << endl;

    return 1;
}
```
* Global and local variables.
* Note: order is important. What happens if you define `sign_function` after `main`?



* There is a way to define functions with `main` first: it's called 'forward declaration'.
* In general, this is better because it allows more flexible code.

```c++
#include <iostream>
using namespace std;

int sign_function(int n);

int main()
{
    int n;
    n = 3;
    cout << sign_function(n) << endl;

    return 0;
}

int sign_function(int n)
{
    int sign;
    if(n>0){
        sign = 1;
    } else if(n==0){
        sign = 0;
    } else {
        sign = -1;
    }
    return sign;
}

```
* Compile and run

* And now we compile like this:
```bash
g++ sign_function.cpp absolute_value.cpp learning_functions.cpp -o sign
```
* The header file is also a good place to put constants you want to have pre-defined in all of the files in your project.




## Part 3. Pointers, classes

### 12. Pointers

* New file! `pointers.cpp`:
```c++
#include <iostream>
using namespace std;

int main(){
   int x = 10;

   cout << "Value of x is " << x << endl;
   cout << "Address of x is " << &x << endl;

   return 0;
}
```
* The `&` sign indicates an address in memory.
* A *pointer* is a variable whose value is the address of another variable, and is notated with a `*`

```c++
#include <iostream>
using namespace std;

int main(){
   int x = 10;
   int *p;
   p = &x;          

   cout << "Value of x is " << x << endl;
   cout << "Address stored in p is " << p << endl;
   cout << "Value of *p variable is " << *p << endl;

   return 0;
}
```

* See what happens to the value of `*p` if we change the value of `x`.



* Historically pointers were used instead of arrays.
* New file! `pointer_array.cpp`

```c++
#include <iostream>
using namespace std;

int main () {
    int primes[3] = {2, 3, 5};
    int *p;

    p = primes; // Set the pointer to point at the start of the array

    for (int i = 0; i < 3; i++) {
        cout << "Address of primes[" << i << "] is " << p << endl;
        cout << "Value of primes[" << i << "] is " << *p << endl;
        p++;
    }  

   return 0;
}
```

* See what `*(primes + 2)` outputs.


### 13. Classes
Classes are one of the main things that separate C++ from C. Classes are ways for us to set up objects that have properties and functions which are particular to that type of object. A class is something like a userdefined data type. 

* New file `rectangles.cpp`
```c++
#include <iostream>
using namespace std;

class Rectangle {
   public:
      double width;    // Width of rectangle
      double height;   // Height of rectangle
};

int main() {
   Rectangle Rec1;        // Declare Rec1 of type Rectangle

   // Rec1 specification
   Rec1.height = 5.0;
   Rec1.width = 6.0;

   double area;

   // area of Rec1
   area = Rec1.height * Rec1.width;
   cout << "Area of Rec1: " << area << endl;

   return 0;
}
```



* Add another rectangle, `Rec2`

You should get something like:

```c++
#include <iostream>
using namespace std;

class Rectangle {
   public:
      double width;    // Width of rectangle
      double height;   // Height of rectangle
};

int main() {
   Rectangle Rec1;        // Declare Rec1 of type Rectangle
   Rectangle Rec2;        // Declare Rec2 of type Rectangle

   // Rec1 specification
   Rec1.height = 5.0;
   Rec1.width = 6.0;

   // Rec2 specification
   Rec2.height = 10.0;
   Rec2.width = 12.0;

   double area;

   // area of Rec1
   area = Rec1.height * Rec1.width;
   cout << "Area of Rec1: " << area << endl;

   // area of Rec2
   area = Rec2.height * Rec2.width;
   cout << "Area of Rec2: " << area << endl;

   return 0;
}
```



* Let's make area a 'member function' of the class (so we can call `Rec1.area()`, for example)

```c++
class Rectangle {
   public:
      double width;   // Length of rectangle
      double height;   // Height of rectangle
      double area() {return width*height;}
};

```



* Replace `area = Rec1.height * Rec1.width;` with `area = Rec1.area();` and see that it works.
* Add a member function `perimeter` which returns the length of the perimeter.



* We're going to look at another way of creating a member function. This is entirely equivalent.
* Just like how we forward declared functions earlier, we can forward declare them here.

```c++
class Rectangle {
   public:
      double width;   // Length of rectangle
      double height;   // Height of rectangle
      double area() {return width*height;}
      void set_dimensions (double x, double y);
};

void Rectangle::set_dimensions (double x, double y) {
  width = x;
  height = y;
}
```



* Replace `Rec1.height = 5.0;` and `Rec1.width = 6.0;` with a call to `Rec1.set_dimensions`

If you want to use `Rectangle` in lots of files, it's annoying to define it every time.

- In actual usage, the definition of class `rectangle` would typically go in the file `rectangle.h` and the definitions of the member functions, like `rectangle::set_dimensions`, would go in the file `rectangle.cc`.

* Put the class declaration and `set_dimensions` definition in a header file, `rectangle.h`, and call it from `rectangles.cpp`

  - `rectangle.h`
  
  ```cpp
  class Rectangle {
     public:
        double width;   // Length of rectangle
        double height;   // Height of rectangle
        double area() {return width*height;}
        void set_dimensions (double x, double y);
  };
  ```
  
  - `rectangle.cc`
  
  ```c++
  #include "rectangle.h"
  void Rectangle::set_dimensions (double x, double y) {
    width = x;
    height = y;
  }
  ```
  
  - `rectangles.cpp`
  
  ```c++
  #include <iostream>
  #include "rectangle.h"
  using namespace std;
  
  int main() {
     Rectangle Rec1;        // Declare Rec1 of type Rectangle
     Rectangle Rec2;        // Declare Rec2 of type Rectangle
  
     // Rec1 specification
     Rec1.height = 5.0;
     Rec1.width = 6.0;
  
     // Rec2 specification
     Rec2.height = 10.0;
     Rec2.width = 12.0;
  
     double area;
  
     // area of Rec1
     area = Rec1.height * Rec1.width;
     cout << "Area of Rec1: " << area << endl;
  
     // area of Rec2
     area = Rec2.height * Rec2.width;
     cout << "Area of Rec2: " << area << endl;
  
     return 0;
  }
  ```
  
  - Compile and run
  
    `g++ rectangles.cpp  rectangle.cc -o rectangles`
### 14. Debugging

* Download the scripts from the debugging folder and try to run them. Can you fix them all?
* [Debugging](debugging/)



Modified from [https://github.com/Pecnut/course-intro-to-cpp](https://github.com/Pecnut/course-intro-to-cpp)



# A short introduction to C++ - Advanced

* **Part 0:** Dynamic memory allocation
* **Part 1:** Namespace
* **Part 2:** Using functions
* **Part 3:** Classes
* **Part 4:** Organize codes into modules

## Part 0. Dynamic memory allocation (动态内存分配)

- Allocating memory at run-time with `new`

```cpp
//pseudo-code
// Single object allocation
Type* ptr = new Type ;
Type* ptr = new Type(initValue) ;
// Arrays of objects allocation
Type* ptr = new Type[size] ;
Type* ptr = new Type[size1][size2]...[sizeN] ;
```

- Operator `delete` releases dynamic memory previously allocated with `new`

```cpp
// release single object
delete ptr ;
// release rrays of objects
delete[] ptr ;
```

- A common problem in programs are memory leaks
  - Memory is allocated but never released even when it is not used anymore

```cpp
void leakFunc() {
  int* array = new int[1000] ;
  // do stuff with array
  delete[] array // statement A
}
int main() {
	int i ;
  for (i=0 ; i<1000 ; i++) {
  	leakFunc() ; // we leak 4K at every call without statement A， 
	} 
}
```


## Part 1. Namespaces 

- Single global namespace often bad idea 
  - Possibility for conflict: someone else (or even you inadvertently) may have used the name want you use in your new piece of code elsewhere $\to $ Linking and runtime errors may result 

- The namespace feature in C++ allows you to explicitly control the scope of your symbols 

```cpp
namespace name 
{
	int global = 0 ;
 	void func() {
 		cout << global << endl ; 
 	}
}
```

- code outside namespace must explicitly use scope operator with namespace name to resolve symbol

```cpp
void bar() {
	cout << foo::global << endl ;
 	foo::func() ;
} 
```

**Namespaces and the Standard Library **

- All symbols in the Standard library are wrapped in the namespace ‘std’ 
  - <iostream>, <math>  etc.

```cpp
#include <iostream>
int main () {
 std::cout << "Hello World!“ << std::endl;
 return 0;
}
```

- It is possible to import symbols from a given namespace into the current scope 

```cpp
#include <iostream>
using std::cout; //Import selected symbols into global namespace 
using std::endl;
int main () {
 cout << "Hello World!“ << endl;
 return 0;
} 
```

- You can also import the symbol contents of an entire namespace 

```cpp
#include <iostream>
using namespace std ;
int main () {
 cout << "Hello World!“ << endl;
 return 0;
}
```

- If possible only import symbols you need 

## Part 2. Using functions

### 1. Default arguments 

 in C++ functions, arguments can have default values 

```cpp
double line(double x, double slope=1, double offset=0);
double line(double x, double slope, double offset)
{
	return x*slope + offset;
}
int main() {
	double x = 1. ;
  double y;
  y=line(x,3.7,5.2);// here slope=3.7, offset=5.2
 	y=line(x,3.7);    // here offset=0.
  y=line(x);        // uses slope=1, offset=0
  return 1;
}
```

- all arguments without default values must appear to the left of all arguments with default values 

### 2. Function overloading (函数重载)

Often algorithms have different implementations with the same functionality, overloaded functions have same name, but different list of arguments. 

```c++
int minimum3(int a, int b, int c) {
 return (a < b ? ( a < c ? a : c ) : ( b < c ? b : c) ) ;
}
float minimum3 (float a, float b, float c) {
 return (a < b ? ( a < c ? a : c ) : ( b < c ? b : c) ) ;
}
int main() {
	int a=3, b=5, c=1;
 	float x=4.5, y=1.2, z=-3.0;
 	int d = minimum3(a,b,c) ; // int minimum3()
 	float w = minimum3(x,y,z) ; // float minimum3()
}
```

* Compiler selects appropriate overloaded function based on argument list 

### 3. Passing Arguments

1. **pass by values**

- Function is passed **copies** of input arguments. 

```c++
void swap(int a, int b) ;
int main() 
{
	int a=3, b=5 ;
  swap(a,b) ;
  cout << “a=“ << a << “, b=“ << b << endl ; 
}
void swap(int a, int b) { //a and b in swap() are copies of a and b in main()
  int tmp ;
 	tmp = a ; a=b; b = tmp ;
}     
```
> output:
```cpp
“a=3, b=5”
```

- For objects a copy is passed –If the subroutine changes the object, only the copy is changed

2. **pass by references**

```cpp
void swap(int &a, int &b) ;
int main() 
{
	int a=3, b=5 ;
  swap(a,b) ;
  cout << “a=“ << a << “, b=“ << b << endl ; 
}
// a and b in swap() are references to original a and b in main(). 
// Any operation affects originals. 
void swap(int &a, int &b) { 
  int tmp ;
 	tmp = a ; a=b; b = tmp ;
}  
```

> output

```cpp
“a=5, b=3”
```

- This is the way to return multiple values from a function.
- Use const references instead of ‘pass-by-value’ when you are dealing with large objects that will not be changed 

3. **pass by pointers**

```cpp
void swap(int* a, int* b) ;
int main() 
{
	int a=3, b=5 ;
	swap(&a,&b) ;
	cout << “a=“ << a << “, b=“ << b << endl ;
}
// a and b in swap() are pointers to original a and b in main(). 
// Any operation affects originals
void swap(int* a, int* b) {
  int tmp ;
  tmp = *a ; *a = *b ; *b = tmp ;
}
```

> Output:

```cpp
“a=5, b=3”
```

- use references when you can, pointers only when you have to.

3. **Passing array as function parameters**

```cpp
void fun(int *arr, unsigned int n)
{
   int i;
   for (i = 0; i < n; i++)
     cout <<" "<< arr[i];
}

int main()
{
   int arr[] = {1, 2, 3, 4, 5, 6, 7, 8};
   unsigned int n = sizeof(arr)/sizeof(arr[0]);
   fun(arr, n);
   return 0;
}
```



## Part 3. Classes

### 4. Constructor, destructor

A class representing vector in 2-D.

```c++
class Vector {
public:
 	Vector();                  //constructor
  Vector(double x, double y);//constructor
  double x();                //get x 
  double y();                //get y 
  double r();                //get r
  double theta();            //get theta
  void setX(double x);       //set x 
  void setY(double y);       //set y 
  void setR(double r);       //set R 
  void setTheta(double theta);//set Theta 
private:
  double m_x;
  double m_y;
}; //Note the semi-colon after the closing brace.

```

1. **Constructor** (构造函数)

- The constructor serves to initialize the object
- A constructor always has the same name as that of the class.

```cpp
public:
 	Vector();
  Vector(double x, double y);
```

```cpp
Vector::Vector() {
  m_x = 0;
  m_y = 0;
}
Vector::Vector(double x, double y) {
  m_x = x;
  m_y = y;
}
```

- A constructor has no return type.
- It is a function that is called when an object is created.

```cpp
Vector u; //calls Vector::Vector()
Vector v(1.5, 3.7) // calss Vector::Vector(double x, double y)
```

- If we provide no constructors for our class, C++ automatically gives us a default constructor

2. **Member function**（成员函数）

```cpp
void Vector::setX(double x) {m_x = x;}
void Vector::setY(double x) {m_y = y;}
void Vector::setR(double R) {
	double cosTheta = m_x / r();
  double sinTheta = m_y / r();
  m_x = R * cosTheta;
  m_y = R * sinTheta;
}
```

```cpp
Vector v(1.5, 3.7);
v.setX(2.9); //set v's value of m_x to 2.9
```

3. **Pointers to objects**

```cpp
Vector* vPtr; //declare a pointer to Vector class; this doesn't create an object yet!
vPtr = new Vector(1.5, 3.7);//create an Vector object
double vX = vPtr->x();
cout << "vX = "<<vX <<endl;// prints vx = 1.5
```

- call meber function of an object with `->`(not with `.`)

3. **Information hiding** 

```cpp
private:
  double m_x;
  double m_y;
```

- `m_x` and `m_y` are declared private, a Vector object’s values of m_x and m_y cannot be accessed directly, but only from within the class’s member functions

```cpp
Vector v(1.5, 3.7);
cout << v.m_x << "," << v.m_y << endl;// Error!
```

4. **Destructor** (析构函数)

- C++ defines Destructor function for each class to be called at end of lifetime of object
  -  Can be used to release memory, resources before death

```cpp
class File {
private:
  fstream fs;
  char* filename;
public:
	File(const char* name) { 
    fs = open(name);
    filename = (char*) name;
  } 
	~File() { close(filename) ; }
	...
};
```

- Destructor calls can take care of automatic resource control

  **Example with dynamically allocated File object**

```cpp
void readFromFile() {
   File *f = new File(“theFile.txt”) ; //Opens file automatically
   // read something from file
   delete f ;                         //Closes file automatically
}
```

​      **Example with automatic File object**

```cpp
void readFromFile() {
   File f(“theFile.txt”) ;             //Opens file automatically
   // read something from file
}  //Deletion of automatic variable f calls destructor & closes file automatically
```

### 5. Inheritance (继承)

- Inheritance is a technique to build a new class based on an old class

```cpp
//Rectangle.h
class Point	//基类Point类的声明
{
public:	//公有函数成员
	void InitP(float xx=0, float yy=0) {X=xx;Y=yy;}
	void Move(float xOff, float yOff) {X+=xOff;Y+=yOff;}
	float GetX() {return X;}
	float GetY() {return Y;}
private:	//私有数据成员
	float X,Y;
};
class Rectangle: public Point	//派生类声明部分
{
public:	//新增公有函数成员
	void InitR(float x, float y, float w, float h){
      InitP(x,y);//基类构造函数
      W=w;H=h;
   }	//调用基类公有成员函数
	float GetH() {return H;}
	float GetW() {return W;}
private:	//新增私有数据成员
	float W,H;
};
```

```cpp
#include<iostream>
#include<cmath>
#include "rectangle.h"
using namespace std;
void main()
{
	Rectangle rect;	//声明Rectangle类的对象
	rect.InitR(2,3,20,10);	//设置矩形的数据
	rect.Move(3,2);	//移动矩形位置
	cout<<"The data of rect(X,Y,W,H):"<<endl;
	cout<<rect.GetX()<<","	//输出矩形的特征参数
	      <<rect.GetY()<<","
	      <<rect.GetW()<<","
	      <<rect.GetH()<<endl;
}
```

- **Virtual function** （虚拟函数）
  - Often derived classes behave differently:

```cpp
class TDish {
  ...
  virtual bool ForSoup() const = 0; //pure virtual function
};
class TPlate: public TDish { 
  ...
  virtual bool ForSoup() { return false;} //implement ForSoup in class TPlate
};
class TBowl: public TDish { 
  ...
  virtual bool ForSoup() { return true; } ////implement ForSoup in class TDish
};
```



```cpp
void FillWithSoup(TDish* dish) {
	if(dish->ForSoup())
		dishD->SetFull();
  // if a Dish is a Plast then do nothing!
    
}
TDish* a = new TPlate();
TDish* b = new TBowl();
FillWithSoup(a);// will not be full
FillWithSoup(b);// is now full
```

### Part 4. Organize codes into modules

- usually it is not convenient to keep all C++ source code in a single file.
  - Split source code into multiple files.

#### 6. Typical layout of a module

- Declarations file

```cpp
// capitalize.hh
#ifndef CAPITALIZE_HH
#define CAPITALIZE_HH

class Fifo {
public: 
  char read() ;
};
void convertUpper(char* str) ;
void convertLower(char* str) ;

#endif
```

**-   Safeguarding against multiple inclusion in `.hh`**

```cpp
#ifndef NAME
#define NAME
//code
(#else)
#endif
```

- Definitions file

```cpp
// capitalize.cc
#include “capitalize.hh”
char Fifo::read() {
  count-- ;
  if (front==len) front=0 ;
  return s[front++] ;
}
void convertUpper(char* ptr) {
	while(*ptr) {
  	if (*ptr>=‘a’&&*ptr<=‘z’) *ptr -= ‘a’-’A’ ;
    ptr++ ;
	} 
}
void convertLower(char* ptr) {
  while(*ptr) {
    if (*ptr>=‘A’&&*ptr<=‘Z’) *ptr += ‘a’-’A’ ;
    ptr++ ;
	} 
}
```

- Main function

```cpp
// demo.cc
#include “capitalize.hh”
int main(int argc, const char* argv[]) 
{ 
  if (argc!=2) return 0 ; 
  convertUpper(argv[1]) ;
	cout << argv[1] << endl ;
}
```

- Compile 

```bash
g++ demo.cc capitalize.cc -o demo
```

### 7. Makefiles

* Long compilation scripts are a bit much:

```bash
g++ demo.cc capitalize.cc -o demo
```

* So let's put it in a makefile:

```bash
all:
    g++ demo.cc capitalize.cc -o demo
```

* (note you need a `tab` at the beginning, not spaces. )
* Then run `make all`



- 更多高阶内容将在数据处理课程的对应章节讲授




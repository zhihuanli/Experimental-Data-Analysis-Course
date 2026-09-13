CXX = c++
CPPFLAGS = -Iinclude $(shell root-config --cflags)
CXXFLAGS = -O2 -Wall
LDLIBS = $(shell root-config --libs)
SOURCES = main.cpp $(wildcard src/*.cpp src/*.C)
HEADERS = $(wildcard include/*.h)

all: tracking

tracking: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDLIBS) -o $@

clean:
	rm -f tracking

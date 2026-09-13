CXX = c++
CPPFLAGS = -Iinclude $(shell root-config --cflags)
CXXFLAGS = -O2 -Wall
LDLIBS = $(shell root-config --libs)
SOURCES = main.cpp $(wildcard src/*.cpp src/*.C) LinkDict.cc
HEADERS = $(wildcard include/*.h)

all: dssd libhits.so

LinkDict.cc: $(HEADERS) Linkdef.h
	rootcling -f $@ -Iinclude include/ana.h Linkdef.h

dssd: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDLIBS) -o $@

libhits.so: LinkDict.cc $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -shared LinkDict.cc $(LDLIBS) -o $@

clean:
	rm -f libhits.so dssd LinkDict.cc LinkDict_rdict.pcm

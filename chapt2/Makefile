#############################################################################
OBJ = tracking
MainFile = main.cpp

###############################################################################

SourceFile := $(wildcard $(shell pwd)/src/*.c $(shell pwd)/src/*.cc $(shell pwd)/src/*.C $(shell pwd)/src/*.cpp $(shell pwd)/src/*.cxx)
IncludeFile := $(wildcard $(shell pwd)/include/*.h $(shell pwd)/include/*.hh $(shell pwd)/include/*.hpp)

###############################################################################

ROOTCFLAGS  = $(shell root-config --cflags)
ROOTLIBS    = $(shell root-config --libs)
ROOTGLIBS = $(shell root-config --glibs)

GXX = g++ 
# -Wl ,--no-as-needed
DIR_INC = -I$(shell pwd)/include
CFLAGS = -Wall -O2 $(ROOTCFLAGS) $(DIR_INC)  #动态连接库不要写在这里
LIBS = $(ROOTGLIBS) -lSpectrum   #动态连接库写在这里 

###############################################################################

all:$(OBJ)
$(OBJ): $(MainFile) $(SourceFile)
	$(GXX) $(CFLAGS) -o $@ $(MainFile) $(SourceFile) $(LIBS)
	@echo "=============================================================="
	@echo "$@ done !"
	@echo "=============================================================="
clean:
	rm -f *.o *.d $(OBJ)

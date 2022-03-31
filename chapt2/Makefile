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
DIR_INC = -I$(ROOTSYS)/include  -I$(shell pwd)/include
CFLAGS = -Wall -O2 $(DIR_INC) -I$(ROOTSYS)/include  $(ROOTLIBS) -lSpectrum -lXMLParser  -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64

###############################################################################

all:$(OBJ)
$(OBJ): $(MainFile) $(SourceFile)
	$(GXX) $(CFLAGS) $(ROOTCFLAGS) $(ROOTLIBS) $(ROOTGLIBS) -o $@ $(MainFile) $(SourceFile)
	@echo "=============================================================="
	@echo "$@ done !"
	@echo "=============================================================="
clean:
	rm -f *.o *.d $(OBJ)

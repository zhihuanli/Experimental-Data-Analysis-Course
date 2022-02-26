#############################################################################
OBJ = dssd
MainFile = main.cpp

###############################################################################

LinkFile = LinkDict.cc

###############################################################################

SourceFile := $(LinkFile) $(MainFile) $(wildcard $(shell pwd)/src/*.c $(shell pwd)/src/*.cc $(shell pwd)/src/*.C $(shell pwd)/src/*.cpp $(shell pwd)/src/*.cxx) 
IncludeFile := $(wildcard $(shell pwd)/include/*.h $(shell pwd)/include/*.hh $(shell pwd)/include/*.hpp)

###############################################################################

ROOTCFLAGS  = $(shell root-config --cflags)
ROOTLIBS    = $(shell root-config --libs)
ROOTGLIBS = $(shell root-config --glibs) #--glibs 与 --libs 的区别在于多了 -lGui 

GXX = g++ 
# -Wl ,--no-as-needed
DIR_INC = -I$(shell pwd)/include
CFLAGS = -Wall -O2 $(ROOTCFLAGS) $(DIR_INC) -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 #动态连接库不要写在这里
LIBS = $(ROOTGLIBS) -lSpectrum -lXMLParser  #动态连接库写在这里 

###############################################################################

all:$(OBJ)

#以下在 Linkdef.h 之前添加 Linkdef.h 中包含 vector 类的文件
$(LinkFile) : include/ana.h Linkdef.h
	rootcling -f $(LinkFile) -c $^	

$(OBJ): $(SourceFile) 
	$(GXX) $(CFLAGS) -o $@ $(SourceFile) $(LIBS)
	@echo "=============================================================="
	@echo "$@ done !"
	@echo "=============================================================="
clean:
	rm -f *.o *.d $(OBJ) *Dict*

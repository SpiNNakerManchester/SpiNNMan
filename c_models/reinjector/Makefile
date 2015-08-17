# An example Makefile suitable for use in SpiNNaker applications using the
# spinnaker_tools libraries and makefiles.

# The name of the application to be built (binary will be this with a `.aplx`
# extension)
APP = reinjector

# Directory to create APLX files in (must include trailing slash)
APP_OUTPUT_DIR = ../../spinnman/model_binaries/

# Directory to place compilation artefacts (must include trailing slash)
BUILD_DIR = build/

# A space-separated list of object files to be built into the executable. These
# .o files will be created from corresponding .c files (e.g. example.c in this
# case).
OBJECTS = reinjector.o

CFLAGS += -Ofast
LFLAGS += -Ofast -Wl,--wrap=sark_int

# The spinnaker_tools standard makefile
include $(SPINN_DIRS)/Makefile.common

SPINN_LIBS := $(SPINN_LIB_DIR)/libsark.a

all: $(APP_OUTPUT_DIR)$(APP).aplx

clean:
	$(RM) $(OBJECTS) $(BUILD_DIR)$(APP).elf $(BUILD_DIR)$(APP).txt $(APP_OUTPUT_DIR)$(APP).aplx


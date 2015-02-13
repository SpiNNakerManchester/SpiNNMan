# If SPINN_DIRS is not defined, this is an error!
ifndef SPINN_DIRS
    $(error SPINN_DIRS is not set.  Please define SPINN_DIRS (possibly by running "source setup" in the spinnaker package folder))
endif

include $(SPINN_DIRS)/Makefile.common

LIBRARIES += -lspinn_common -lm

ifeq ($(GNU),1)
    SPINN_LIBS += $(SPINN_LIB_DIR)/libspin1_api.a
else
    SPINN_LIBS += $(SPINN_LIB_DIR)/spin1_api.a
endif

APP = re_injection

# Primary target is an APLX file - built from the ELF

#  1) Create a binary file which is the concatenation of RO and RW sections
#  2) Make an APLX header from the ELF file with "mkaplx" and concatenate
#     that with the binary to make the APLX file
#  3) Remove temporary files and "ls" the APLX file

../$(APP).aplx: $(APP).elf
ifeq ($(GNU),1)
	$(OC) -O binary -j RO_DATA $(APP).elf RO_DATA.bin
	$(OC) -O binary -j RW_DATA $(APP).elf RW_DATA.bin
	$(SPINN_TOOLS_DIR)/mkbin RO_DATA.bin RW_DATA.bin > $(APP).bin
else
	$(OC) --bin --output $(APP).bin $(APP).elf
endif
	$(SPINN_TOOLS_DIR)/mkaplx -nm $(NM) $(APP).elf | $(CAT) - $(APP).bin > ../$(APP).aplx
	$(RM) $(APP).bin RO_DATA.bin RW_DATA.bin
	$(LS) ../$(APP).aplx

# Build the ELF file

#  1) Make a "sark_build.c" file containing app. name and build time
#     with "mkbuild" and compile it
#  2) Link application object(s), build file and library to make the ELF
#  3) Tidy up temporaries and create a list file

$(APP).elf: $(APP).o $(SCRIPT) $(SPINN_LIBS) 
	$(SPINN_TOOLS_DIR)/mkbuild $(APP) > sark_build.c
	$(CC) -o sark_build.o sark_build.c
	$(LD) $(LFLAGS) $(APP).o sark_build.o $(SPINN_LIBS) $(LIBRARIES) -o $(APP).elf
	$(RM) sark_build.c sark_build.o
	$(OD) > $(APP).txt $(APP).elf


# Build the main object file. If there are other files in the
# application, place their build dependencies below this one.

$(APP).o: $(APP).c $(SPINN_INC_DIR)/spinnaker.h $(SPINN_INC_DIR)/sark.h $(SPINN_INC_DIR)/spin1_api.h
	$(CC) $(CFLAGS) $(APP).c


# Tidy and cleaning dependencies
clean:
	$(RM) $(APP).o $(APP).elf $(APP).txt ../$(APP).aplx

#-------------------------------------------------------------------------------
#------------------------------------------------------------------------------#
if !AMDISTRIBUTESOFTWARE
if AMHAVEVT
VTxxxCPPFLAGS = @VT_CPPFLAGS@
endif
endif

#------------------------------------------------------------------------------#
if !AMDISTRIBUTESOFTWARE
if AMHAVEVT
if AMHAVEOMP
VTOPARIxxxCPPFLAGS = @VT_CPPFLAGS@ \
-vt:opari "-rcfile $(top_builddir)/src/scafes.opari.rc -table $(top_builddir)/src/scafes.opari.tab.c"
endif
endif
endif

#------------------------------------------------------------------------------#
SCAFES_TESTS_DIR=$(top_srcdir)/examples

CPPFLAGS_COMMON= \
        -I$(top_srcdir)/tests/system/HeatEqnFDM \
        -I$(top_srcdir)/tests/system/HeatEqnFDM/Neumann \
        -I$(top_srcdir)/src \
        -I$(top_builddir)/src \
        @NETCDF_CPPFLAGS@ \
        @BOOST_CPPFLAGS@ \
        @MPI_CPPFLAGS@ \
        @OPENMP_CXXFLAGS@ \
        @ADOLC_CPPFLAGS@ \
        $(VTxxxCPPFLAGS) \
        $(VTOPARIxxxCPPFLAGS)

LDFLAGS_COMMON = $(VTxxxCPPFLAGS) \
                 $(VTOPARIxxxCPPFLAGS)

LDADD_COMMON = \
        $(top_builddir)/src/libscafes.la \
        @BOOST_LDFLAGS@ \
        @BOOST_PROGRAM_OPTIONS_LIB@ \
        @BOOST_REGEX_LIB@ \
        @BOOST_SERIALIZATION_LIB@ \
        @MPI_LDFLAGS@ \
        @BOOST_MPI_LIB@ \
        @OPENMP_CXXFLAGS@ \
        @NETCDF_LDFLAGS@ \
        @ADOLC_LDFLAGS@

DEPENDENCIES_COMMON= $(top_builddir)/src/libscafes.la

################################################################################
include_HEADERS=
bin_PROGRAMS=
noinst_HEADERS=
check_HEADERS=
check_PROGRAMS=
EXTRA_DIST=

################################################################################
noinst_HEADERS +=
check_PROGRAMS += HeatEqnFdmNeumannTimeLinSpaceLin1D
HeatEqnFdmNeumannTimeLinSpaceLin1D_SOURCES = main1D.cpp \
                     TimeLinSpaceLin.hpp
HeatEqnFdmNeumannTimeLinSpaceLin1D_CPPFLAGS = $(CPPFLAGS_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin1D_LDFLAGS = $(LDFLAGS_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin1D_LDADD = $(LDADD_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin1D_DEPENDENCIES = $(DEPENDENCIES_COMMON)
#------------------------------------------------------------------------------#
check_PROGRAMS += HeatEqnFdmNeumannTimeLinSpaceLin2D
HeatEqnFdmNeumannTimeLinSpaceLin2D_SOURCES = main2D.cpp \
                     TimeLinSpaceLin.hpp
HeatEqnFdmNeumannTimeLinSpaceLin2D_CPPFLAGS = $(CPPFLAGS_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin2D_LDFLAGS = $(LDFLAGS_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin2D_LDADD = $(LDADD_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin2D_DEPENDENCIES = $(DEPENDENCIES_COMMON)
#------------------------------------------------------------------------------#
check_PROGRAMS += HeatEqnFdmNeumannTimeLinSpaceLin3D
HeatEqnFdmNeumannTimeLinSpaceLin3D_SOURCES = main3D.cpp \
                     TimeLinSpaceLin.hpp
HeatEqnFdmNeumannTimeLinSpaceLin3D_CPPFLAGS = $(CPPFLAGS_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin3D_LDFLAGS = $(LDFLAGS_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin3D_LDADD = $(LDADD_COMMON)
HeatEqnFdmNeumannTimeLinSpaceLin3D_DEPENDENCIES = $(DEPENDENCIES_COMMON)

#------------------------------------------------------------------------------#
if !AMDISTRIBUTESOFTWARE
clean-local:
	-rm -f *.gcno *.opari.inc *.pomp.cpp *.core
endif

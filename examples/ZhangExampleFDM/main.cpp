/* ScaFES
 * Copyright (c) 2011-2015, ZIH, TU Dresden, Federal Republic of Germany.
 * For details, see the files COPYING and LICENSE in the base directory
 * of the package.
 */

#include "ScaFES.hpp"
#include "ZhangExampleFDM.hpp"

/** Space dimension of problem. */
const int DIM = 1;

/** Main program for ZhangExampleFDM. */
int main(int argc, char *argv[]) {
    ScaFES::Parameters paramsCl(argc, argv);
    ScaFES::GridGlobal<DIM> gg(paramsCl);
    std::vector<std::string> nameDatafield(1);
    nameDatafield[0] = "T"; /* Temperature vector. */
    std::vector<int> stencilWidth(1);
    stencilWidth[0] = 1;
    std::vector<bool> isKnownDf(1);
    isKnownDf[0] = false;
    std::vector<int> nLayers(1);
    nLayers[0] = 0;
    std::vector<double> defaultValue(1);
    defaultValue[0] = 0.0;
    std::vector<ScaFES::WriteHowOften> writeToFile(1, ScaFES::WriteHowOften::LIKE_GIVEN_AT_CL);
    std::vector<bool> computeError(1);
    computeError[0] = false;
    std::vector<double> geomparamsInit;

    ZhangExampleFDM<double, DIM> ppp(paramsCl, gg, false, nameDatafield, stencilWidth,
                                isKnownDf, nLayers, defaultValue, writeToFile,
                                computeError, geomparamsInit);
    ppp.iterateOverTime();

    return 0;
}

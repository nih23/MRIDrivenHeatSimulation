/* ScaFES
 * Copyright (c) 2017, ZIH, TU Dresden, Federal Republic of Germany.
 * For details, see the files COPYING and LICENSE in the base directory
 * of the package.
 */

/**
 *  @file HeatEqnFdmTimeLinSpaceLin.hpp
 *
 *  @brief Implementation of n-dimensional heat equation problem on unit hybercube.
 *
 * <ul>
 * Given solution: \f[y: \bar{\Omega} \times [t_S; t_E] \to {R}\f]
 * \f[ y(x,t) := (1 + t) \cdot  (1 + \sum_p x_p), \f] </li>
 * <li> given source \f[f: \bar{\Omega} \times (t_S;t_E] \to R,\f],
 * \f[ f(x,t) := 1 + \sum_p x_p, \f] </li>
 * \f[ \widetilde{y}(x,t) := (1 + t) \cdot  (1 + \sum_p x_p). \f] </li>
 * <li> given boundary condition \f[g: \partial\Omega \times (t_S;t_E] \to R,\f]
 * \f[ g(x,t) := (1 + t) \cdot (1 + \sum_p x_p), \f] </li>
 * <li> given initial condition \f[\widetilde{y}: \bar{\Omega} \to R,\f]
 * \f[ \widetilde{y}(x,t) := (1 + t) \cdot  (1 + \sum_p x_p). \f] </li>
 * </ul>
 */

#include "ScaFES.hpp"
#include "HeatEqnFDM.hpp"

template<typename CT, std::size_t DIM>
class HeatEqnFdmTimeLinSpaceLin : public HeatEqnFDM<CT,DIM, HeatEqnFdmTimeLinSpaceLin<CT,DIM> > {

  public:
    /** All fields which are related to the underlying problem
     * are added in terms of an entry of the parameters of
     * type \c std::vector.
     * @param params Set of ScaFES parameters.
     * @param gg Global grid.
     * @param useLeapfrog Should the leap frog scheme be used?
     * @param nameDatafield Name of the fields.
     * @param stencilWidth Stencil width of the fields.
     * @param isKnownDf Is the data field are known or unknown one?
     * @param nLayers Number of layers at the global boundary.
     * @param defaultValue Default value of fields.
     * @param writeToFile How often should the data field be written to file.
     * @param computeError Should the Linf error between the numerical
     *                     and exact solution be computed?
     * @param geomparamsInit Initial guess of geometrical parameters.
     */
    HeatEqnFdmTimeLinSpaceLin(ScaFES::Parameters const& params,
               ScaFES::GridGlobal<DIM> const& gg,
               bool useLeapfrog,
               std::vector<std::string> const& nameDatafield,
               std::vector<int> const& stencilWidth,
               std::vector<bool> const& isKnownDf,
               std::vector<int> const& nLayers = std::vector<int>(),
               std::vector<CT> const& defaultValue = std::vector<CT>(),
               std::vector<ScaFES::WriteHowOften> const& writeToFile
                 = std::vector<ScaFES::WriteHowOften>(),
               std::vector<bool> const& computeError = std::vector<bool>(),
               std::vector<CT> const& geomparamsInit = std::vector<CT>() )
        : HeatEqnFDM<CT, DIM, HeatEqnFdmTimeLinSpaceLin<CT,DIM> >(params, gg, useLeapfrog,
                                                        nameDatafield, stencilWidth,
                                                        isKnownDf, nLayers,
                                                        defaultValue, writeToFile,
                                                        computeError, geomparamsInit)
        { }

    /** Evaluates all fields at one given global inner grid node.
     *  @param vNew Set of all fields.
     *  @param idxNode Index of given grid node.
     */
    void evalInner(std::vector< ScaFES::DataField<CT, DIM> >& vNew,
                   ScaFES::Ntuple<int,DIM> const& idxNode,
                   int const& timestep) {
        ScaFES::Ntuple<double,DIM> x = this->coordinates(idxNode);
        double t = this->time(timestep);

        /* Vector for f. */
        vNew[0](idxNode) = 0.0;
        double dTdt = 1.0;
        for (std::size_t pp = 0; pp < DIM; ++pp) {
            dTdt += x[pp];
        }
        vNew[0](idxNode) = dTdt; // - 0

        /* Vector for y. */
        vNew[2](idxNode) = 1.0;
        for (std::size_t pp = 0; pp < DIM; ++pp) {
            vNew[2](idxNode) += x[pp];
        }
        vNew[2](idxNode) *= (1.0 + t);
        /* Vector for g. */
        vNew[1](idxNode) = vNew[2](idxNode);
    }

    /** Evaluates all fields at one given global border grid node.
     *  @param vNew Set of all fields.
     *  @param idxNode Index of given grid node.
     *  @param timestep Given time step.
     */
    void evalBorder(std::vector< ScaFES::DataField<CT, DIM> >& vNew,
                    ScaFES::Ntuple<int,DIM> const& idxNode,
                    int const& timestep) {
        this->evalInner(vNew, idxNode, timestep);
    }

    /** Initializes all unknown fields at one given global inner grid node.
     *  @param vNew Set of all unknown fields (return value).
     *  @param idxNode Index of given grid node.
     */
    template<typename TT>
    void initInner(std::vector< ScaFES::DataField<TT, DIM> >& vNew,
                   std::vector<TT> const& /*vOld*/,
                   ScaFES::Ntuple<int,DIM> const& idxNode,
                   int const& timestep) {
        ScaFES::Ntuple<double,DIM> x = this->coordinates(idxNode);
        double t_s = this->time(timestep);

        vNew[0](idxNode) = 1.0;
        for (std::size_t pp = 0; pp < DIM; ++pp) {
                vNew[0](idxNode) += x[pp];
        }
        vNew[0](idxNode) *= (1.0 + t_s);
    }

    /** Initializes all unknown fields at one given global border grid node.
     *  @param vNew Set of all unknown fields (return value).
     *  @param vOld Set of all given fields.
     *  @param idxNode Index of given grid node.
     *  @param timestep Given time step.
     */
    template<typename TT>
    void initBorder(std::vector< ScaFES::DataField<TT, DIM> >& vNew,
                    std::vector<TT> const& vOld,
                    ScaFES::Ntuple<int,DIM> const& idxNode,
                    int const& timestep) {
        this->template initInner<TT>(vNew, vOld, idxNode, timestep);
    }
};
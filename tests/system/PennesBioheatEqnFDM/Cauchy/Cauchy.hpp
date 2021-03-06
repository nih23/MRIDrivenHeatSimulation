/* ScaFES
 * Copyright (c) 2017, ZIH, TU Dresden, Federal Republic of Germany.
 * For details, see the files COPYING and LICENSE in the base directory
 * of the package.
 */

/**
 *  @file Cauchy.hpp
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

#ifndef PENNESHEATEQNFDM_CAUCHY_HPP_
#define PENNESHEATEQNFDM_CAUCHY_HPP_

#include "ScaFES.hpp"
#include "PennesBioheatEqnFDM.hpp"

template<typename CT, std::size_t DIM, typename Class>
class Cauchy : public PennesBioheatEqnFDM<CT,DIM, Cauchy<CT,DIM, Class> > {

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
    Cauchy(ScaFES::Parameters const& params,
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
        : PennesBioheatEqnFDM<CT, DIM, Cauchy<CT,DIM,Class> >(params, gg, useLeapfrog,
                                                     nameDatafield, stencilWidth,
                                                     isKnownDf, nLayers,
                                                     defaultValue, writeToFile,
                                                     computeError, geomparamsInit)
        { }

    /** Evaluates all fields at one given global inner grid node.
     *  @param vNew Set of all fields.
     *  @param idxNode Index of given grid node.
     *  @param timestep Given time step.
     */
    void evalInner(std::vector< ScaFES::DataField<CT, DIM> >& vNew,
                   ScaFES::Ntuple<int,DIM> const& idxNode,
                   int const& timestep) {
        static_cast<Class*>(this)->evalInner(vNew, idxNode, timestep);
    }

    /** Evaluates all fields at one given global border grid node.
     *  @param vNew Set of all fields.
     *  @param idxNode Index of given grid node.
     *  @param timestep Given time step.
     */
    void evalBorder(std::vector< ScaFES::DataField<CT, DIM> >& vNew,
                    ScaFES::Ntuple<int,DIM> const& idxNode,
                    int const& timestep) {
        static_cast<Class*>(this)->evalBorder(vNew, idxNode, timestep);
    }

    /** Initializes all unknown fields at one given global inner grid node.
     *  @param vNew Set of all unknown fields (return value).
     *  @param vOld Set of all given fields.
     *  @param idxNode Index of given grid node.
     *  @param timestep Given time step.
     */
    template<typename TT>
    void initInner(std::vector< ScaFES::DataField<TT, DIM> >& vNew,
                   std::vector<TT> const& vOld,
                   ScaFES::Ntuple<int,DIM> const& idxNode,
                   int const& timestep) {
        static_cast<Class*>(this)->initInner(vNew, vOld, idxNode, timestep);
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
        static_cast<Class*>(this)->initBorder(vNew, vOld, idxNode, timestep);
    }

    /** Updates all unknown fields at one given global border grid node.
     *  @param vNew Set of all unknown fields at new time step (return value).
     *  @param vOld Set of all given fields.
     *  @param idxNode Index of given grid node.
     */
    template<typename TT>
    void updateBorder(std::vector<ScaFES::DataField<TT,DIM>>& vNew,
                      std::vector<ScaFES::DataField<TT,DIM>>const& vOld,
                      ScaFES::Ntuple<int,DIM> const& idxNode,
                      int const& /*timestep*/) {
        bool useCauchy = true;

        /* Use Dirichlet boundary condition if at least one element in
         * grid node is zero. */
        for (std::size_t pp = 0; pp < DIM; ++pp) {
            if (idxNode.elem(pp) == 0) {
                useCauchy = false;
                vNew[0](idxNode) = this->knownDf(1, idxNode);
                break;
            }
        }
        /* Otherwise use Cauchy boundary condition. */
        if (useCauchy == true) {
            vNew[0](idxNode) = vOld[0](idxNode);
            for (std::size_t pp = 0; pp < DIM; ++pp) {
                /* Cauchy boundary condition has to be used in this direction. */
                if (idxNode.elem(pp) == (this->nNodes(pp)-1)) {
                    vNew[0](idxNode) += this->tau() * this->COEFF_A * (
                                        vOld[0](this->connect(idxNode, 2*pp))
                                        /* vOld[0](this->connect(idxNode, 2*pp+1) */
                                        + vOld[0](this->connect(idxNode, 2*pp))
                                        - ((2.0*this->gridsize(pp)/this->LAMBDA)
                                           * this->ALPHA * vOld[0](idxNode))
                                        + ((2.0*this->gridsize(pp)/this->LAMBDA)
                                           * this->knownDfOld(1, idxNode))
                                        /******************************************/
                                        - 2.0 * vOld[0](idxNode) )
                                        / (this->gridsize(pp) * this->gridsize(pp));
                }
                /* Usual central differencing scheme for this direction. */
                else {
                    vNew[0](idxNode) += this->tau() * this->COEFF_A * (
                                        vOld[0](this->connect(idxNode, 2*pp))
                                        + vOld[0](this->connect(idxNode, 2*pp+1))
                                        - 2.0 * vOld[0](idxNode) )
                                        / (this->gridsize(pp) * this->gridsize(pp));
                }
            }
            vNew[0](idxNode) -= this->tau()
                                * ((this->RHO_BLOOD*this->C_BLOOD)
                                    /(this->RHO*this->C))
                                * this->W * vOld[0](idxNode);
            vNew[0](idxNode) += this->tau() * (1.0/(this->RHO*this->C))
                                * this->knownDfOld(0, idxNode);
        }
    }
};
#endif

// ==============================================================================
//
//  Scatter2d.h
//  QTR
//
//  Created by Albert Lu on 1/12/21.
//  alu@tacc.utexas.edu
//
//  Last modified on 4/22/26
//
//  Note:
//
// ==============================================================================

#ifndef QTR_Scatter2d_H
#define QTR_Scatter2d_H

#include <complex>

#include "Containers.h"
#include "Eigen.h"
#include "Pointers.h"

namespace QTR_NS {
    
    class Scatter2d {
        
    public:
        Scatter2d(class QTR *q);
        ~Scatter2d();
  
        void                          Evolve();
        inline int                    GridToIdx(int x1, int x2);

    private:

        void            init();
        QTR             *qtr;
        Error           *err;
        Log             *log;
        Parameters      *parameters;

        // General parameters
        std::complex<double>  I;      // sqrt(-1)
        std::complex<double>  xZERO;  // complex zero
        int             DIMENSIONS;
        int             EDGE;
        int             PERIOD;
        int             PRINT_PERIOD;
        int             PRINT_WAVEFUNC_PERIOD;
        int             GRIDS_TOT;
        bool            QUIET;
        bool            TIMING;
        bool            DEBUG;
        double          TIME;   

        // Grid size
        double          kk;    // time resolution
        VectorXd        H;     // grid size 
        VectorXd        Hi;    // inverse grid size
        VectorXd        Hisq;  // inverse grid size square     

        // Domain size
        VectorXd        Box;
        VectorXi        BoxShape;
        int             M1;
        int             W1;
        int             O1;

        // Potential parameters  
        int             idx_des_2_min;    
        int             idx_des_2_max;
        int             idx_des_1;
        int             idx_dis_1_min;
        int             idx_dis_1_max;
        int             idx_dis_2;
        double          hb;
        double          m;
        double          m1;
        double          m2;

        // Wavefunction
        VectorXd        Wave0;
        VectorXd        A;
        VectorXd        P;

        // Truncate parameters
        bool            isEmpty;
        bool            isFullGrid; 
        double          TolH;
        double          TolL;
        double          TolHd;
        double          TolLd;
        double          ExReduce;
        int             ExLimit;

        // Domains
        MeshIndex       TB;    // Truncation boundary
        MeshIndex       TBL;
        MeshIndex       TBL_P;
        MeshIndex       ExFF;
        std::vector<int> Check;

        double          toggle_threshold;
        bool            isReNorm;
        bool            isFluxNProb;
        bool            isPrintEdge;
        bool            isPrintDensity;
        bool            isPrintAdiaDensity;
        bool            isPrintWaveFunc;
        bool            isToggle;
    };
}

#endif /* QTR_Scatter2d_H */

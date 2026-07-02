# Wikipedia Import: Analysis of covariance

## Matched Term

Analysis of covariance

## Domain

contraindications_uncertainty

## Source

https://en.wikipedia.org/wiki/Analysis_of_covariance

## Description



## Summary

Analysis of covariance (ANCOVA) is a general linear model that blends ANOVA and regression. ANCOVA evaluates whether the means of a dependent variable (DV) are equal across levels of one or more categorical independent variables (IV) and across one or more continuous variables. For example, the categorical variable(s) might describe treatment and the continuous variable(s) might be covariates (CV)'s, typically nuisance variables; or vice versa. Mathematically, ANCOVA decomposes the variance in the DV into variance explained by the CV(s), variance explained by the categorical IV, and residual variance. Intuitively, ANCOVA can be thought of as 'adjusting' the DV by the group means of the CV(s).
The ANCOVA model assumes a linear relationship between the response (DV) and covariate (CV):





          y

            i
            j


        =
        μ
        +

          τ

            i


        +

          B

        (

          x

            i
            j


        −


            x
            ¯


        )
        +

          ϵ

            i
            j


        .


    {\displaystyle y_{ij}=\mu +\tau _{i}+\mathrm {B} (x_{ij}-{\overline {x}})+\epsilon _{ij}.}


In this equation, the DV,




          y

            i
            j




    {\displaystyle y_{ij}}

 is the jth observation under the ith categorical group; the CV,




          x

            i
            j




    {\displaystyle x_{ij}}

 is the jth observation of the covariate under the ith group. Variables in the model that are derived from the observed data are



        μ


    {\displaystyle \mu }

 (the grand mean) and





            x
            ¯




    {\displaystyle {\overline {x}}}

 (the global mean for covariate



        x


    {\displaystyle x}

). The variables to be fitted are




          τ

            i




    {\displaystyle \tau _{i}}

 (the effect of the ith level of the categorical IV),



        B


    {\displaystyle B}

 (the slope of the line) and




          ϵ

            i
            j




    {\displaystyle \epsilon _{ij}}

 (the associated unobserved error term for the jth observation in the ith group).
Under this specification, the categorical treatment effects sum to zero




          (


              ∑

                i


                a



              τ

                i


            =
            0

          )

        .


    {\displaystyle \left(\sum _{i}^{a}\tau _{i}=0\right).}

 The standard assumptions of the linear regression model are also assumed to hold, as discussed below.

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.

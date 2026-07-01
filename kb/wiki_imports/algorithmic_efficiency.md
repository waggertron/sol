# Wikipedia Import: Algorithmic efficiency

## Matched Term

Algorithmic efficiency

## Domain

communication_linguistic_markers

## Source

https://en.wikipedia.org/wiki/Algorithmic_efficiency

## Description



## Summary

In computer science, algorithmic efficiency is a property of an algorithm which relates to the amount of computational resources used by the algorithm. Algorithmic efficiency can be thought of as analogous to engineering productivity for a repeating or continuous process.
For maximum efficiency it is desirable to minimize resource usage. However, different resources such as time and space complexity cannot be compared directly, so which of two algorithms is considered to be more efficient often depends on which measure of efficiency is considered most important.
For example, cycle sort and Timsort are both algorithms to sort a list of items from smallest to largest. Cycle sort organizes the list in time proportional to the number of elements squared (



        O
        (

          n

            2


        )


    {\textstyle O(n^{2})}

, see big O notation), but minimizes the writes to the original array and only requires a small amount of extra memory which is constant with respect to the length of the list (



        O
        (
        1
        )


    {\textstyle O(1)}

). Timsort sorts the list in time linearithmic (proportional to a quantity times its logarithm) in the list's length (



        O
        (
        n
        log
        ⁡
        n
        )


    {\textstyle O(n\log n)}

), but has a space requirement linear in the length of the list (



        O
        (
        n
        )


    {\textstyle O(n)}

). If large lists must be sorted at high speed for a given application, timsort is a better choice; however, if minimizing the program/erase cycles and memory footprint of the sorting is more important, cycle sort is a better choice.

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.

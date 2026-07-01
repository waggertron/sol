# Wikipedia Import: Abstract semantic graph

## Matched Term

Abstract semantic graph

## Domain

communication_linguistic_markers

## Source

https://en.wikipedia.org/wiki/Abstract_semantic_graph

## Description



## Summary

In computer science, an abstract semantic graph (ASG) or term graph is a form of abstract syntax in which an expression of a formal or programming language is represented by a graph whose vertices are the expression's subterms. An ASG is at a higher level of abstraction than an abstract syntax tree (or AST), which is used to express the syntactic structure of an expression or program.
ASGs are more complex and concise than ASTs because they may contain shared subterms (also known as "common subexpressions"). Abstract semantic graphs are often used as an intermediate representation by compilers to store the results of performing common subexpression elimination upon abstract syntax trees. ASTs are trees and are thus incapable of representing shared terms. ASGs are usually directed acyclic graphs (DAG), although in some applications graphs containing cycles may be permitted. For example, a graph containing a cycle might be used to represent the recursive expressions that are commonly used in functional programming languages as non-looping iteration constructs. The mutability of these types of graphs, is studied in the field of graph rewriting.
The nomenclature term graph is associated with the field of term graph rewriting, which involves the transformation and processing of expressions by the specification of rewriting rules, whereas abstract semantic graph is used when discussing linguistics, programming languages, type systems and compilation.
Abstract syntax trees are not capable of sharing subexpression nodes because it is not possible for a node in a proper tree to have more than one parent. Although this conceptual simplicity is appealing, it may come at the cost of redundant representation and, in turn, possibly inefficiently duplicating the computation of identical terms. For this reason ASGs are often used as an intermediate language at a subsequent compilation stage to abstract syntax tree construction via parsing.
An abstract semantic graph is typically constructed from an abstract syntax tree by a process of enrichment and abstraction. The enrichment can for example be the addition of back-pointers, edges from an identifier node (where a variable is being used) to a node representing the declaration of that variable. The abstraction can entail the removal of details which are relevant only in parsing, not for semantics.

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.

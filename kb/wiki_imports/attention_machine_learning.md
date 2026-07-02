# Wikipedia Import: Attention (machine learning)

## Matched Term

Attention (machine learning)

## Domain

behavioral_regularities

## Source

https://en.wikipedia.org/wiki/Attention_(machine_learning)

## Description



## Summary

In machine learning, attention is a method that determines the importance of each component in a sequence relative to the other components in that sequence. In natural language processing, importance is represented by "soft" weights assigned to each word in a sentence. More generally, attention encodes vectors called token embeddings across a fixed-width sequence that can range from tens to millions of tokens in size.
Unlike "hard" weights, which are computed during the backwards training pass, "soft" weights exist only in the forward pass and therefore change with every step of the input. Earlier designs implemented the attention mechanism in a serial recurrent neural network (RNN) language translation system, but a more recent design, namely the transformer, removed the slower sequential RNN and relied more heavily on the faster parallel attention scheme.
Inspired by ideas about attention in humans, the attention mechanism was developed to address the weaknesses of using information from the hidden layers of recurrent neural networks. Recurrent neural networks favor information contained in words at the end of a sentence and thus deemed more recent, thereby tending to attenuate the significance and associated predictive weight assigned to information earlier in the sentence. Attention allows a token equal access to any part of a sentence directly, rather than only through the previous state.

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.

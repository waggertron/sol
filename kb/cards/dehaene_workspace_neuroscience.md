# Source Card: Dehaene Workspace Neuroscience

## Citation

Primary source:

Dehaene, S., and Naccache, L. (2001). Towards a cognitive neuroscience of
consciousness: basic evidence and a workspace framework. Cognition, 79(1-2),
1-37. https://doi.org/10.1016/S0010-0277(00)00123-2

Related imported sources:

- Dehaene, S., Cohen, L., Naccache, L., Le Bihan, D., Mangin, J.-F., Poline,
  J.-B., and Rivière, D. (2001). Cerebral mechanisms of word masking and
  unconscious repetition priming. Nature Neuroscience, 4(7), 752-758.
  https://doi.org/10.1038/89551
- Dehaene, S., Sergent, C., and Changeux, J.-P. (2003). A neuronal network
  model linking subjective reports and objective physiological data during
  conscious perception. Proceedings of the National Academy of Sciences, 100(14),
  8520-8525. https://doi.org/10.1073/PNAS.1332574100
- Dehaene, S., Kerszberg, M., and Changeux, J.-P. (1998). A neuronal model of a
  global workspace in effortful cognitive tasks. Proceedings of the National
  Academy of Sciences, 95(24), 14529-14534.
  https://doi.org/10.1073/PNAS.95.24.14529
- Crick, F., and Koch, C. (2003). A framework for consciousness. Nature
  Neuroscience, 6(2), 119-126. https://doi.org/10.1038/NN0203-119

Contextual contrast:

- Dennett, D. (2001). Are we explaining consciousness yet? Cognition, 79(1-2),
  221-237. https://doi.org/10.1016/S0010-0277(00)00130-X
- Edelman, G. M. (2003). Naturalizing consciousness: A theoretical framework.
  Proceedings of the National Academy of Sciences, 100(9), 5520-5524.
  https://doi.org/10.1073/PNAS.0931349100

Source registry id: `dehaene_workspace_neuroscience`

## Domain

- context-specific states
- attention and awareness
- neural evidence
- computational cognitive models

## Key Contribution

This cluster translates workspace ideas into a more empirical and computational
frame. The core contribution is not that it proves a single theory of
consciousness. The useful point for this project is methodological:

- distinguish nonconscious processing from reportable access
- look for threshold-like transitions rather than assuming everything is linear
- connect subjective report, behavioral output, and measurable system state
- treat broad availability as a functional property, not just a content label

That is directly relevant to user modeling. A platform like this should not
collapse raw signal presence into full-profile certainty. Some information may
be weakly present in data but not sufficiently stable, repeated, or user-ratified
to deserve global use in generation.

## Model Implications

Use this cluster to justify:

- evidence thresholds before promoting an observation into an active profile
  atom
- separate storage for latent cues, candidate atoms, and active steering atoms
- uncertainty markers when evidence is sparse, indirect, or conflicting
- explicit linkage between subjective/user-confirmed reports and model state

It also supports an engineering pattern:

- collect local signals
- aggregate and score them
- expose only high-confidence or user-confirmed summaries to downstream
  generation

That pattern is much closer to a defensible profile system than direct
"personality from traces" claims.

## Limits and Cautions

These papers study conscious access, neural correlates, and computational
models, not personality inference. They are useful for information-flow
architecture, thresholding, and evidence integration.

They should not be used to justify:

- neuroscientific branding for ordinary user modeling
- claims that profile atoms map to brain states
- pseudo-clinical interpretations of user behavior

In this repo, their value is architectural rigor, not biological overreach.

## Evidence Grade

`A`

## Useful Search Terms

- workspace framework
- conscious access
- reportability threshold
- subjective report and objective data
- global neuronal workspace
- unconscious repetition priming

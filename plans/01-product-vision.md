# Product Vision Plan

## Thesis

Generative systems become more useful when they remember and respect a user's
communication style, creative taste, motivations, values, and context-specific
preferences. This project explores whether that memory can be modeled
rigorously, visibly, and ethically.

## Product Frame

Use:

> personality and style model

Avoid:

> true personality detector

> clinical diagnosis engine

> literal engram

## Target Users

Initial candidates:

- creators who need coherent personal style across content
- professionals who want generated writing to match their voice
- users interested in self-expression and reflective profiling
- developers who may later use the platform through an API

## Core Value

The system should help users produce outputs that feel more personally aligned
than generic generation.

## Current State

The repository now has a research RAG, JSONDB import queue, OCEAN assessment
corpus, and a local assessment/profile workbench through scoped context export.
The next product validation step is to add user-reviewed generation guidance,
persisted pilot runs, and one consented writing-sample path before broader
multimodal generation.

## Non-Goals

- diagnose mental health conditions
- infer protected traits
- rank people for eligibility decisions
- hide profiling from users
- claim complete psychological accuracy

## Open Questions

- Is the initial wedge creator-facing, self-reflection-facing, or productivity-
  facing?
- What level of profile visibility feels useful without becoming overwhelming?
- Which output modalities matter first after text?

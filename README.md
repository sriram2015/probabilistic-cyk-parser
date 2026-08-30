# Probabilistic CYK Algorithm for Finding Most Likely Parse Trees

## NLP Mini Project

### Student Details

| Detail | Information |
|---|---|
| **Name** | Sriram J |
| **Register Number** | 2117240030146 |
| **Department** | Artificial Intelligence and Machine Learning |
| **Course** | AL23531 - Natural Language Processing |
| **Semester** | V |

---

## 📌 Project Overview

This project implements a **Probabilistic CYK (CKY) Algorithm** for finding the most likely parse tree of an input sentence.

The system uses a **Probabilistic Context-Free Grammar (PCFG)**, dynamic programming, and Viterbi-style backtracking to identify the highest-probability syntactic parse.

---

## 🎯 Objectives

- Implement the Probabilistic CYK algorithm.
- Use a Probabilistic Context-Free Grammar.
- Calculate probabilities for possible constituents.
- Find the most likely parse tree.
- Implement Viterbi-style backtracking.
- Provide a web-based interface.
- Visualize the CKY chart and parsing results.

---

## 🏗️ System Architecture

```text
                Sentence Input
                       │
                       ▼
                 Tokenization
                       │
                       ▼
             Lexical Probability
                Initialization
                       │
                       ▼
            CKY Dynamic Programming
                       │
                       ▼
             Viterbi Backtracking
                       │
                       ▼
              Most Likely Parse Tree

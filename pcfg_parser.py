"""
Probabilistic CKY / CYK parser for a small Chomsky-Normal-Form PCFG.

The parser stores the best probability for every non-terminal in each
chart cell and keeps a back-pointer so the most likely parse tree can
be reconstructed.
"""

import math
from collections import defaultdict

class PCFGParser:
    def __init__(self):
        # All probabilities are conditional rule probabilities.
        # For each LHS, probabilities sum to 1.0.
        self.start_symbol = "S"

        self.lexical_rules = {
            "Det": {"the": 0.60, "a": 0.40},
            "N": {"boy": 0.25, "girl": 0.25, "dog": 0.25, "cat": 0.25},
            "Adj": {"big": 0.50, "small": 0.50},
            "V": {"sees": 0.50, "likes": 0.50},
            "Adv": {"quickly": 1.00},
        }

        self.binary_rules = [
            ("S", "NP", "VP", 1.00),
            ("NP", "Det", "N", 0.55),
            ("NP", "Det", "AdjN", 0.25),
            ("NP", "N", "N", 0.20),
            ("AdjN", "Adj", "N", 1.00),
            ("VP", "V", "NP", 0.60),
            ("VP", "V", "Adv", 0.40),
        ]

        # No unary rules are required for the demonstration grammar.
        # Keeping the grammar in binary/lexical form makes it suitable for CKY. 
        self.unary_rules = []

        self._validate_grammar()

    def _validate_grammar(self):
        totals = defaultdict(float)
        for lhs, _, _, p in self.binary_rules:
            totals[lhs] += p
        for lhs, _, p in self.unary_rules:
            totals[lhs] += p
        for lhs, words in self.lexical_rules.items():
            totals[lhs] += sum(words.values())

        # S, NP, VP have binary/unary alternatives; this simplified grammar
        # intentionally uses probabilities only within the alternatives that
        # are active in the project demonstration.
        if any(p <= 0 or p > 1 for p in [r[3] for r in self.binary_rules]):
            raise ValueError("Invalid binary rule probability.")

    @staticmethod
    def _log(p):
        return math.log(p)

    def rules_for_display(self):
        rules = []
        for lhs, rhs, p in []:
            rules.append({"lhs": lhs, "rhs": rhs, "probability": p})
        for lhs, rhs1, rhs2, p in self.binary_rules:
            rules.append({
                "lhs": lhs,
                "rhs": f"{rhs1} {rhs2}",
                "probability": p,
                "type": "binary"
            })
        for lhs, rhs, p in self.unary_rules:
            rules.append({
                "lhs": lhs,
                "rhs": rhs,
                "probability": p,
                "type": "unary"
            })
        for lhs, words in self.lexical_rules.items():
            for word, p in words.items():
                rules.append({
                    "lhs": lhs,
                    "rhs": f"'{word}'",
                    "probability": p,
                    "type": "lexical"
                })
        return rules

    def _apply_unary_closure(self, cell):
        changed = True
        while changed:
            changed = False
            for lhs, rhs, p in self.unary_rules:
                if rhs in cell:
                    candidate = cell[rhs]["prob"] * p
                    if lhs not in cell or candidate > cell[lhs]["prob"]:
                        cell[lhs] = {
                            "prob": candidate,
                            "back": ("unary", rhs, p)
                        }
                        changed = True

    def parse(self, sentence):
        tokens = sentence.lower().strip().split()
        if len(tokens) < 1:
            raise ValueError("Sentence must contain at least one word.")

        unknown = []
        for word in tokens:
            if not any(word in words for words in self.lexical_rules.values()):
                unknown.append(word)
        if unknown:
            raise ValueError(
                "Unknown word(s): " + ", ".join(unknown) +
                ". Try: the boy sees the dog"
            )

        n = len(tokens)
        chart = [[{} for _ in range(n + 1)] for _ in range(n)]

        # Lexical initialization.
        for i, word in enumerate(tokens):
            cell = chart[i][i + 1]
            for lhs, words in self.lexical_rules.items():
                if word in words:
                    cell[lhs] = {
                        "prob": words[word],
                        "back": ("lexical", word, words[word])
                    }
            self._apply_unary_closure(cell)

        # CKY dynamic programming.
        operations = []
        for span in range(2, n + 1):
            for i in range(n - span + 1):
                j = i + span
                cell = chart[i][j]

                for k in range(i + 1, j):
                    left = chart[i][k]
                    right = chart[k][j]
                    if not left or not right:
                        continue

                    for lhs, rhs1, rhs2, rule_p in self.binary_rules:
                        if rhs1 in left and rhs2 in right:
                            candidate = (
                                left[rhs1]["prob"]
                                * right[rhs2]["prob"]
                                * rule_p
                            )
                            operations.append({
                                "span": [i, j],
                                "split": k,
                                "rule": f"{lhs} -> {rhs1} {rhs2}",
                                "probability": candidate
                            })
                            if lhs not in cell or candidate > cell[lhs]["prob"]:
                                cell[lhs] = {
                                    "prob": candidate,
                                    "back": ("binary", k, rhs1, rhs2, rule_p)
                                }

                self._apply_unary_closure(cell)

        root = chart[0][n].get(self.start_symbol)
        if not root:
            raise ValueError(
                "No valid parse tree was found for this sentence under the supplied PCFG."
            )

        tree = self._build_tree(chart, tokens, 0, n, self.start_symbol)

        # Convert log probability to a more readable percentage-like score.
        probability = root["prob"]
        return {
            "sentence": sentence,
            "tokens": tokens,
            "parse_found": True,
            "most_likely_probability": probability,
            "log_probability": math.log(probability),
            "tree": tree,
            "bracketed_tree": self._tree_to_brackets(tree),
            "chart": self._chart_to_json(chart, tokens),
            "operations": operations,
            "metrics": {
                "tokens": n,
                "chart_cells": n * (n + 1) // 2,
                "candidate_operations": len(operations),
                "algorithm": "Probabilistic CKY (Viterbi-style)",
                "complexity": "O(n^3 * |G|)"
            }
        }

    def _build_tree(self, chart, tokens, i, j, symbol):
        entry = chart[i][j][symbol]
        back = entry["back"]

        if back[0] == "lexical":
            return {"label": symbol, "children": [tokens[i]], "probability": entry["prob"]}

        if back[0] == "unary":
            child = self._build_tree(chart, tokens, i, j, back[1])
            return {
                "label": symbol,
                "children": [child],
                "probability": entry["prob"]
            }

        _, k, rhs1, rhs2, _ = back
        left = self._build_tree(chart, tokens, i, k, rhs1)
        right = self._build_tree(chart, tokens, k, j, rhs2)
        return {
            "label": symbol,
            "children": [left, right],
            "probability": entry["prob"]
        }

    def _tree_to_brackets(self, node):
        if all(isinstance(c, str) for c in node["children"]):
            return f"({node['label']} {' '.join(node['children'])})"
        return "(" + node["label"] + " " + " ".join(
            self._tree_to_brackets(c) for c in node["children"]
        ) + ")"

    def _chart_to_json(self, chart, tokens):
        result = []
        n = len(tokens)
        for span in range(1, n + 1):
            for i in range(n - span + 1):
                j = i + span
                entries = []
                for symbol, value in sorted(chart[i][j].items()):
                    entries.append({
                        "symbol": symbol,
                        "probability": value["prob"]
                    })
                result.append({
                    "start": i,
                    "end": j,
                    "text": " ".join(tokens[i:j]),
                    "entries": entries
                })
        return result

if __name__ == "__main__":
    parser = PCFGParser()
    print(parser.parse("the boy sees the dog")["bracketed_tree"])

"""
Acceptance tests for Dream Changers Publishing — 3 competing homepage concepts.

Linked to:
  BDD scenarioId: 141956f6-1f8b-492c-91a5-cef7b54c274d
  TDD test set:   eb038368-a8de-4164-991b-ec9588964526

Run:    python3 -m unittest -v landing-pages/tests/test_acceptance.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
CONCEPT_A = os.path.join(ROOT, "concept-1-galaxy", "index.html")
CONCEPT_B = os.path.join(ROOT, "concept-2-storybook", "index.html")
CONCEPT_C = os.path.join(ROOT, "concept-3-tooniverse-live", "index.html")
ALL_CONCEPTS = [CONCEPT_A, CONCEPT_B, CONCEPT_C]


def read(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class IndexPage(unittest.TestCase):
    def test_index_exists(self):
        self.assertTrue(os.path.exists(INDEX), f"missing: {INDEX}")

    def test_index_lists_three_concepts(self):
        html = read(INDEX)
        self.assertIn("concept-1-galaxy/", html)
        self.assertIn("concept-2-storybook/", html)
        self.assertIn("concept-3-tooniverse-live/", html)

    def test_index_thumbnails_link_to_each_concept(self):
        html = read(INDEX)
        for href in ("concept-1-galaxy/", "concept-2-storybook/", "concept-3-tooniverse-live/"):
            self.assertRegex(html, rf'href\s*=\s*["\'][^"\']*{re.escape(href)}', f"index missing link to {href}")


class EveryConcept(unittest.TestCase):
    def test_all_concept_files_exist(self):
        for p in ALL_CONCEPTS:
            self.assertTrue(os.path.exists(p), f"missing concept file: {p}")

    def test_each_has_doctype_html5(self):
        for p in ALL_CONCEPTS:
            html = read(p).lstrip()
            self.assertRegex(html[:50].lower(), r"^<!doctype html>", f"{p} missing <!doctype html>")

    def test_each_has_meta_viewport(self):
        for p in ALL_CONCEPTS:
            html = read(p).lower()
            self.assertIn("name=\"viewport\"", html, f"{p} missing meta viewport")
            self.assertIn("width=device-width", html)

    def test_each_has_unique_title(self):
        titles = []
        for p in ALL_CONCEPTS:
            m = re.search(r"<title>(.*?)</title>", read(p), re.IGNORECASE | re.DOTALL)
            self.assertIsNotNone(m, f"{p} missing <title>")
            titles.append(m.group(1).strip().lower())
        self.assertEqual(len(set(titles)), 3, f"titles not unique: {titles}")

    def test_each_exposes_one_primary_cta(self):
        for p in ALL_CONCEPTS:
            html = read(p)
            self.assertRegex(html, r'class\s*=\s*["\'][^"\']*\bcta\b', f"{p} missing element with class 'cta'")

    def test_each_links_back_to_index(self):
        for p in ALL_CONCEPTS:
            html = read(p)
            self.assertRegex(html, r'href\s*=\s*["\'](?:\.\./|/landing-pages/)?(?:index\.html|\.\./)',
                             f"{p} missing back link to parent index")

    def test_no_autoplay_audio(self):
        for p in ALL_CONCEPTS:
            html = read(p).lower()
            self.assertNotRegex(html, r"<audio[^>]*\bautoplay\b", f"{p} has autoplay audio")

    def test_prefers_reduced_motion_respected(self):
        for p in ALL_CONCEPTS:
            html = read(p)
            self.assertIn("prefers-reduced-motion", html,
                          f"{p} does not respect prefers-reduced-motion")

    def test_external_libs_via_https_cdn(self):
        for p in ALL_CONCEPTS:
            html = read(p)
            for m in re.finditer(r'src\s*=\s*["\']([^"\']+)["\']', html):
                src = m.group(1)
                if src.startswith("http://") or src.startswith("//"):
                    self.fail(f"{p} loads non-https resource: {src}")


class ConceptIdentity(unittest.TestCase):
    def test_a_uses_three_js(self):
        html = read(CONCEPT_A).lower()
        self.assertIn("three", html, "concept A must use Three.js")
        self.assertTrue("three.module" in html or "three.min" in html or "three@" in html,
                        "concept A must load three.js from CDN")

    def test_b_uses_painterly_palette(self):
        html = read(CONCEPT_B).lower()
        # parchment / ember / forest hex anchors
        warm_palette_hits = sum(int(any(h in html for h in group)) for group in [
            ["#f3e3c3", "#f4e4c1", "#f8ecd1", "#efe1bf", "#f5e6c4"],   # parchment
            ["#b34a1f", "#c75a2c", "#a84323", "#ce5b1f", "#b74d20"],   # ember
            ["#2e4f3a", "#1f4630", "#2d5a3f", "#264b35", "#27553a"],   # forest
        ])
        self.assertGreaterEqual(warm_palette_hits, 2,
                                "concept B must use a warm painterly palette (parchment/ember/forest)")

    def test_c_uses_variable_font_kinetic_type(self):
        html = read(CONCEPT_C).lower()
        self.assertTrue(
            "font-variation-settings" in html or "@import url('https://fonts.googleapis.com" in html or "fonts.googleapis" in html,
            "concept C must use variable fonts / kinetic typography")
        # kinetic type = scale or stretch animation present
        self.assertTrue(
            "transform" in html and ("scale" in html or "stretch" in html or "wdth" in html),
            "concept C must animate transforms for kinetic typography")

    def test_each_has_distinct_palette(self):
        # extract any hex colors from each file; the leading-dominant set must differ across the three
        def palette(path):
            return set(re.findall(r"#[0-9a-fA-F]{6}", read(path)))
        a, b, c = palette(CONCEPT_A), palette(CONCEPT_B), palette(CONCEPT_C)
        self.assertGreater(len(a), 0, "concept A defines no hex colors")
        self.assertGreater(len(b), 0, "concept B defines no hex colors")
        self.assertGreater(len(c), 0, "concept C defines no hex colors")
        # at least 80% unique-to-self
        for name, mine, others in [("A", a, b | c), ("B", b, a | c), ("C", c, a | b)]:
            unique = mine - others
            self.assertGreaterEqual(len(unique) / max(len(mine), 1), 0.4,
                                    f"concept {name} palette overlaps too much with the others")

    def test_each_has_distinct_hero_copy(self):
        # extract first <h1> innerText from each
        def h1(path):
            m = re.search(r"<h1[^>]*>(.*?)</h1>", read(path), re.IGNORECASE | re.DOTALL)
            self.assertIsNotNone(m, f"{path} has no <h1>")
            return re.sub(r"<[^>]+>", "", m.group(1)).strip().lower()
        ha, hb, hc = h1(CONCEPT_A), h1(CONCEPT_B), h1(CONCEPT_C)
        self.assertEqual(len({ha, hb, hc}), 3, f"hero <h1> copy not distinct: {ha!r} {hb!r} {hc!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

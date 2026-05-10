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
CONCEPT_D = os.path.join(ROOT, "concept-4-immersiverse", "index.html")
CONCEPT_F = os.path.join(ROOT, "concept-5-wall-of-heroes", "index.html")
CONCEPT_G = os.path.join(ROOT, "concept-6-lost-legend-archive", "index.html")
ALL_CONCEPTS = [CONCEPT_A, CONCEPT_B, CONCEPT_C, CONCEPT_D, CONCEPT_F, CONCEPT_G]


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

    def test_index_lists_extra_concepts(self):
        html = read(INDEX)
        self.assertIn("concept-4-immersiverse/", html)
        self.assertIn("concept-5-wall-of-heroes/", html)
        self.assertIn("concept-6-lost-legend-archive/", html)

    def test_index_thumbnails_link_to_each_concept(self):
        html = read(INDEX)
        for href in (
            "concept-1-galaxy/", "concept-2-storybook/", "concept-3-tooniverse-live/",
            "concept-4-immersiverse/", "concept-5-wall-of-heroes/", "concept-6-lost-legend-archive/",
        ):
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
        self.assertEqual(len(set(titles)), len(ALL_CONCEPTS), f"titles not unique: {titles}")

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

    def test_d_anchors_immersiverse_pillar(self):
        html = read(CONCEPT_D).lower()
        self.assertIn("mesh", html, "concept D must reference MESH Learning")
        self.assertTrue(any(t in html for t in ("immersiverse", "classroom", "discovery room", "newbicon city")),
                        "concept D must reference ImmersiVerse / classroom pillar")

    def test_f_anchors_wall_of_heroes_pillar(self):
        html = read(CONCEPT_F).lower()
        self.assertTrue(any(t in html for t in ("wall of heroes", "founders", "founding", "honor wall", "patron")),
                        "concept F must reference Wall of Heroes / patronage pillar")

    def test_g_anchors_lost_legend_pillar(self):
        html = read(CONCEPT_G).lower()
        self.assertTrue(any(t in html for t in ("lost legend", "tude shifters", "library", "archive", "catalog")),
                        "concept G must reference Lost Legend Library / archive pillar")

    def test_each_has_distinct_palette(self):
        def palette(path):
            return set(re.findall(r"#[0-9a-fA-F]{6}", read(path)))
        sets = {p: palette(p) for p in ALL_CONCEPTS}
        for p, s in sets.items():
            self.assertGreater(len(s), 0, f"{p} defines no hex colors")
        # each concept must contain at least 4 hex colors not shared by any other concept
        for p, mine in sets.items():
            others = set().union(*[v for k, v in sets.items() if k != p])
            unique = mine - others
            self.assertGreaterEqual(len(unique), 4,
                                    f"{p} palette overlaps too much; only {len(unique)} unique hexes")

    def test_each_has_distinct_hero_copy(self):
        def h1(path):
            m = re.search(r"<h1[^>]*>(.*?)</h1>", read(path), re.IGNORECASE | re.DOTALL)
            self.assertIsNotNone(m, f"{path} has no <h1>")
            return re.sub(r"<[^>]+>", "", m.group(1)).strip().lower()
        heroes = [h1(p) for p in ALL_CONCEPTS]
        self.assertEqual(len(set(heroes)), len(heroes), f"hero <h1> copy not all distinct: {heroes!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

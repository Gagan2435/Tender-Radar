import unittest

from tenders import classifier, pipeline, sources


class PureLogicTests(unittest.TestCase):
    def test_parse_notice_multilingual(self):
        n = {"publication-number": "123-2026", "notice-title": {"fra": ["Titre"], "eng": ["Cloud services"]},
             "buyer-name": {"eng": ["City of X"]}, "buyer-country": ["DEU"], "classification-cpv": ["72000000"],
             "publication-date": "2026-09-01+02:00"}
        r = sources.parse_notice(n)
        self.assertEqual((r["title"], r["country"], r["published"]), ("Cloud services", "DEU", "2026-09-01"))

    def test_parse_notice_without_id(self):
        self.assertIsNone(sources.parse_notice({"notice-title": "x"}))

    def test_clean_rejects_and_normalises(self):
        self.assertIsNone(pipeline.clean({"ref": "1", "title": "  "}))
        c = pipeline.clean({"ref": " 9 ", "title": "  Road   works  ", "cpv": "45-233120", "country": "deu"})
        self.assertEqual((c["title"], c["country"], c["sector"]), ("Road works", "DEU", "Construction"))

    def test_classifier_beats_baseline_on_sample(self):
        rows = [(r["title"], classifier.cpv_sector(r["cpv"])) for r in sources.sample_data()]
        rep = classifier.evaluate(rows)
        self.assertGreater(rep["accuracy"], rep["baseline"])


if __name__ == "__main__":
    unittest.main()

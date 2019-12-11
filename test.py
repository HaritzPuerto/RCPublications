#!/usr/bin/env python
# encoding: utf-8

from urllib.parse import urlparse
import glob
import json
import os
import pprint
import sys
import unittest


PARTITIONS = []
PUBLICATIONS = {}


def url_validator (url):
    """validate the format of a URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


class TestVerifyPublications (unittest.TestCase):
    ALLOWED_FIELDS = set([
            "title",
            "datasets",
            "original"
            ])


    def allow_arg (self):
        return None
    

    def setUp (self):
        """load the publications list"""
        global PUBLICATIONS

        if len(PUBLICATIONS) > 0:
            self.publications = PUBLICATIONS
            return

        self.publications = {}
        count = 0

        for partition in PARTITIONS:
            with open(partition, "r") as f:
                #print("loading: {}".format(partition))
                self.publications[partition] = json.load(f)
                count += len(self.publications[partition])

        # store this dictionary in a global variable to prevent
        # reloading every partition file for every unit test
        PUBLICATIONS = self.publications
        print("\n{} publications total".format(count))


    def test_file_loaded (self):
        print("\n{} partitions loaded".format(len(self.publications)))
        self.assertTrue(len(self.publications) > 0)


    def test_has_required_fields (self):
        for partition, publications in self.publications.items():
            for pub in publications:
                if not set(["title", "datasets"]).issubset(pub.keys()):
                    raise Exception("{}: missing required fields\n{}".format(pub["id"], partition))


    def test_has_valid_url (self):
        for partition, publications in self.publications.items():
            for pub in publications:
                if "url" in pub:
                    url = pub["url"]

                    if url == "" or not url:
                        pass
                    elif not url_validator(url):
                        raise Exception("{}: badly formed URL {}\n{}".format(pub["title"], url, partition))


    def test_each_field (self):
        for partition, publications in self.publications.items():
            for pub in publications:
                for key in pub.keys():
                    if key not in self.ALLOWED_FIELDS:
                        raise Exception("{}: unknown field name {}\n{}".format(pub["title"], key, partition))


    def test_original_fields (self):
        for partition, publications in self.publications.items():
            for pub in publications:
                if "original" in pub.keys():
                    orig = pub["original"]

                    for key in ["url", "doi", "pdf", "journal"]:
                        if key in orig:
                            if not orig[key] or not isinstance(orig[key], str):
                                print(orig)
                                raise Exception("{}: bad value for {}\n{}".format(pub["title"], partition))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PARTITIONS.append(sys.argv.pop())
    else:
        subdir = "partitions"

        for partition in glob.glob(subdir + "/*.json"):
            PARTITIONS.append(partition)

    unittest.main()

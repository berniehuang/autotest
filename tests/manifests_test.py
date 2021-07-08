import os
import unittest
from suntest.util.manifests import Manifests


class TestManifests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifests_data_path = os.path.join(os.path.realpath(__file__).split("manifests_test.py")[0], "data/manifests")

    @classmethod
    def tearDownClass(cls):
        #Remove.remove_all_files(cls.manifests_data_path)
        pass

    def setUp(self):
        self.manifests_file = os.path.join(TestManifests.manifests_data_path, "default.xml")
        self.manifest = Manifests()
        self.manifest.get_project_list(self.manifests_file)
        self.manifest.get_remote_list(self.manifests_file)

    def tearDown(self):
        del self.manifest

    def test_get_remote_dict(self):
        _remote_dict = {u'JA168': u'ssh://igerrit.storm:29418/Src/16Model/JA168',
                        u'JA188': u'ssh://igerrit.storm:29418/Src/18Model/JA188',
                        u'origin': u'ssh://igerrit.storm:29418/Src/14Model/JA158'}
        _origin_fetch = unicode('ssh://igerrit.storm:29418/Src/14Model/JA158')

        self.assertEqual(_remote_dict, self.manifest.get_remote_dict())
        self.assertEqual(_origin_fetch, self.manifest.remote_dict.get("origin"))

    def test_get_project_path_list(self):
        _project_path_list = [u'build', u'development', u'board/common', u'framework/service/navi/src/core']
        self.assertEqual(sorted(_project_path_list) ,sorted(self.manifest.get_project_path_list()))

    def test_get_project_name_list(self):
        _project_name_list = [u'build', u'development', u'board/common', u'framework/navi/core']
        self.assertEqual(sorted(_project_name_list) ,sorted(self.manifest.get_project_name_list()))

    def test_get_project_name(self):
        _project_name = u'framework/navi/core'
        self.assertEqual(_project_name, self.manifest.get_project_name("framework/service/navi/src/core"))

    def test_get_project_path(self):
        _project_path = u'framework/service/navi/src/core'
        self.assertEqual(_project_path, self.manifest.get_project_path("framework/navi/core"))

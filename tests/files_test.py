import os
import unittest
import suntest.files.copy as Copy
import suntest.files.package as Package
import suntest.files.read as Read
import suntest.files.write as Write
import suntest.files.remove as Remove


class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files_data_path = os.path.join(os.path.realpath(__file__).split("files_test.py")[0], "data/files")

    @classmethod
    def tearDownClass(cls):
        Remove.remove_all_files(cls.files_data_path)

    def setUp(self):
        self.source_path = os.path.join(TestFiles.files_data_path, "source")
        self.target_path = os.path.join(TestFiles.files_data_path, "target")
        self.no_exist_dir = os.path.join(TestFiles.files_data_path, "noexist")
        self.fext = ".gcno"
        self.fname = "unittest"

        if not os.path.exists(self.source_path):
            os.makedirs(self.source_path)
        if not os.path.exists(self.target_path):
            os.makedirs(self.target_path)

        self.spc_file = "spcfile"
        if not os.path.exists(os.path.join(self.source_path, self.spc_file)):
            f = open(os.path.join(self.source_path, self.spc_file), 'w')
            f.write("this is UnitTest file.")
            f.close

        self.write_file = "writefile"

        self.gcno_file = "unittest.gcno"
        if not os.path.exists(os.path.join(self.source_path, self.gcno_file)):
            f = open(os.path.join(self.source_path, self.gcno_file), 'w')
            f.close

    def tearDown(self):
        Remove.remove_all_files(self.target_path)

    def test_copy_file(self):
        self.assertTrue(Copy.copy_file(self.source_path, self.target_path, self.spc_file))

    def test_copy_file_no_exist(self):
        # source_path is not exist
        self.assertFalse(Copy.copy_file(self.no_exist_dir, self.target_path, self.spc_file))
        # target_path is not exist
        self.assertFalse(Copy.copy_file(self.source_path, self.no_exist_dir, self.spc_file))

    def test_copy_file_source_path_type_error(self):
        # source_path type error
        with self.assertRaises(TypeError):
            Copy.copy_file(dict(), self.target_path, self.spc_file)

    def test_copy_file_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Copy.copy_file(self.source_path, dict(), self.spc_file)

    def test_copy_dir(self):
        self.assertTrue(Copy.copy_dir(self.source_path, self.target_path))

    def test_copy_dir_no_exist(self):
        # source_path is not exist
        self.assertFalse(Copy.copy_dir(self.no_exist_dir, self.target_path))
        # target_path is not exist
        self.assertFalse(Copy.copy_dir(self.source_path, self.no_exist_dir))

    def test_copy_dir_source_path_type_error(self):
        # source_path type error
        with self.assertRaises(TypeError):
            Copy.copy_dir(dict(), self.target_path)

    def test_copy_dir_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Copy.copy_dir(self.source_path, dict())

    def test_copy_tree_with_fext(self):
        self.assertTrue(Copy.copy_tree_with_fext(self.source_path, self.target_path, self.fext))

    def test_copy_tree_with_fext_no_exist(self):
        # source_path is not exist
        self.assertFalse(Copy.copy_tree_with_fext(self.no_exist_dir, self.target_path, self.fext))
        # target_path is not exist
        self.assertFalse(Copy.copy_tree_with_fext(self.source_path, self.no_exist_dir, self.fext))

    def test_copy_tree_with_fext_source_path_type_error(self):
        # source_path type error
        with self.assertRaises(TypeError):
            Copy.copy_tree_with_fext(dict(), self.target_path, self.fext)

    def test_copy_tree_with_fext_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Copy.copy_tree_with_fext(self.source_path, dict(), self.fext)

    def test_copy_tree_with_fname(self):
        self.assertTrue(Copy.copy_tree_with_fname(self.source_path, self.target_path, self.fname))

    def test_copy_tree_with_fname_no_exist(self):
        # source_path is not exist
        self.assertFalse(Copy.copy_tree_with_fname(self.no_exist_dir, self.target_path, self.fname))
        # target_path is not exist
        self.assertFalse(Copy.copy_tree_with_fname(self.source_path, self.no_exist_dir, self.fname))

    def test_copy_tree_with_fname_source_path_type_error(self):
        # source_path type error
        with self.assertRaises(TypeError):
            Copy.copy_tree_with_fname(dict(), self.target_path, self.fname)

    def test_copy_tree_with_fname_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Copy.copy_tree_with_fname(self.source_path, dict(), self.fname)

    def test_tar_files(self):
        tar_filename = os.path.join(self.target_path, "source.tar.gz")

        self.assertTrue(Package.tar_files(tar_filename, self.source_path))

    def test_tar_files_no_exist(self):
        tar_filename = os.path.join(self.target_path, "source.tar.gz")

        # target_path is not exist
        self.assertFalse(Package.tar_files(tar_filename, self.no_exist_dir))

    def test_tar_files_name_type_error(self):
        # name type error
        with self.assertRaises(TypeError):
            Package.tar_files(dict(), self.source_path)

    def test_tar_files_data_path_type_error(self):
        tar_filename = os.path.join(self.target_path, "source.tar.gz")

        # path type error
        with self.assertRaises(TypeError):
            Package.tar_files(tar_filename, dict())

    def test_find_files(self):
        os.path.walk(self.source_path, Remove.find_files, (self.spc_file))

    def test_remove_files(self):
        os.path.walk(self.source_path, Remove.remove_files, (self.spc_file))

    def test_remove_all_files(self):
        self.assertTrue(Remove.remove_all_files(self.target_path))

    def test_remove_all_files_no_exist(self):
        # target_path is not exist
        self.assertFalse(Remove.remove_all_files(self.no_exist_dir))

    def test_remove_all_files_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Remove.remove_all_files(dict())

    def test_remove_spc_files(self):
        self.assertTrue(Remove.remove_spc_files(self.target_path, self.spc_file))

    def test_remove_spc_files_no_exist(self):
        # target_path is not exist
        self.assertFalse(Remove.remove_spc_files(self.no_exist_dir, self.spc_file))

    def test_remove_spc_files_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Remove.remove_spc_files(dict(), self.spc_file)

    def test_read_file(self):
        self.assertTrue(Read.read_file(os.path.join(self.source_path, self.spc_file)))

    def test_read_file_no_exist(self):
        # target_path is not exist
        self.assertFalse(Read.read_file(os.path.join(self.no_exist_dir, self.spc_file)))

    def test_read_file_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Read.read_file(dict())

    def test_display_file(self):
        self.assertTrue(Read.display_file(os.path.join(self.source_path, self.spc_file), "UnitTest"))

    def test_display_file_no_exist(self):
        # target_path is not exist
        self.assertFalse(Read.display_file(os.path.join(self.no_exist_dir, self.spc_file), "UnitTest"))

    def test_display_file_target_path_type_error(self):
        # target_path type error
        with self.assertRaises(TypeError):
            Read.display_file(dict(), "UnitTest")

    def test_write_file(self):
        write_content = "the file is used to test files write module."

        self.assertTrue(Write.write_file(os.path.join(self.target_path, self.write_file), write_content))

    def test_write_file_target_path_type_error(self):
        write_content = "the file is used to test files write module."

        # target_path type error
        with self.assertRaises(TypeError):
            Write.write_file(dict(), write_content)

    def test_recored_file(self):
        recored_content = "the attend recored content."

        self.assertTrue(Write.recored_file(os.path.join(self.target_path, self.write_file), recored_content))

    def test_recored_file_target_path_type_error(self):
        recored_content = "the attend recored content."

        # target_path type error
        with self.assertRaises(TypeError):
            Write.recored_file(dict(), recored_content)

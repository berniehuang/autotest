# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
# Filename: svn.py
# author: huangbin@pset.suntec.net
# date: 2013.12.22
# input:
#       src_p: file path will be committed
#------------------------------------------------------------------------------
import sys
import os
import shutil
import time
import subprocess
from logging import debug
from logging import info
from logging import error


class Svn:
    def __init__(self, src_p, tgt_p, svn_url, svn_usr, svn_pwd):
        self.src_pth = src_p
        self.tgt_pth = tgt_p
        self.__svn_srv_url = svn_url
        self.__svn_srv_usr = svn_usr
        self.__svn_srv_pwd = svn_pwd

        if(os.path.exists(src_p) is False):
            error("source code files path" + self.src_pth + "is not exist.")
            sys.exit()

    def CommitSvn(self, svn_pth, log_nm):
        svn_co_tgt_pth = os.path.join(self.tgt_pth, svn_pth) + log_nm
        svn_co_src_pth = self.src_pth + log_nm
        info("copy " + svn_co_src_pth + " to " + svn_co_tgt_pth)
        if os.path.isfile(svn_co_src_pth):
            try:
                shutil.copyfile(svn_co_src_pth, svn_co_tgt_pth)
            except Exception, e:
                raise e
        else:
            try:
                print "svn_co_src_pth: %s svn_co_tgt_pth: %s" % (svn_co_src_pth, svn_co_tgt_pth)
                shutil.rmtree(svn_co_tgt_pth)
                shutil.copytree(svn_co_src_pth, svn_co_tgt_pth, True)
            except Exception, e:
                raise e
        svn_add_cmd = "svn add %s" % (svn_co_src_pth)
        debug("svn add command:" + svn_add_cmd)
        try:
            hd_svn_add = subprocess.Popen(svn_add_cmd, shell=True, stdout=None)
        except Exception, e:
            raise e
        tmr = 100
        while True:
            rc = subprocess.Popen.poll(hd_svn_add)
            if rc is None:
                time.sleep(1)
                tmr = tmr - 1
                if tmr == 0:
                    error("Test result svn add failed...")
                    sys.exit()
                continue
            else:
                info("Finished svn add.")
                break

        svn_cmit_cmd = "svn commit -m \"add or update test result\" %s" % (svn_co_tgt_pth)
        debug("svn commit command: " + svn_cmit_cmd)
        hd_svn_cmit = subprocess.Popen(svn_cmit_cmd, shell=True, stdout=None)
        tmr = 50
        while True:
            rc = subprocess.Popen.poll(hd_svn_cmit)
            if rc is None:
                continue
            else:
                info("Finished svn commit.")
                break

            time.sleep(1)
            tmr = tmr - 1
            if tmr == 0:
                error("Test result svn MoveSrcCodemmit failed.")
                sys.exit()

    def CheckoutSvn(self):
        svn_co_cmd = "svn checkout %s%s %s %s" % (self.__svn_srv_url, self.tgt_pth, self.__svn_srv_usr, self.__svn_srv_pwd)
        debug("svn checkout command: " + svn_co_cmd)
        sp_svn_co_cmd = subprocess.Popen(svn_co_cmd, shell=True, stdout=subprocess.PIPE)
        tmr = 50
        while True:
            tmr = tmr - 1
            time.sleep(1)
            if tmr == 0:
                error("svn checkout failed")
            rc = subprocess.Popen.poll(sp_svn_co_cmd)
            if rc is None:
                continue
            else:
                info("svn checkout succeeded")
                break

    def ClearSvn(self):
        clear_svn_cmd = "rm -rf svn_dir/*;rm -rf svn_dir/.svn"
        debug("clear svn command: " + clear_svn_cmd)
        hd_clear_svn_cmd = subprocess.Popen(clear_svn_cmd, shell=True)
        tmr = 50
        while True:
            tmr = tmr - 1
            rf = subprocess.Popen.poll(hd_clear_svn_cmd)
            if rf is None:
                continue
            else:
                info("Clear svn dir finished.")
                break
            time.sleep(1)
            if tmr == 0:
                error("Clear svn dir failed.")
                sys.exit()


def main(argv):
    source_path = "cpFile/system/core/ncore/"

    up_svn = Svn(source_path)
    up_svn.CommitSvn()

if __name__ == "__main__":
    main(sys.argv)

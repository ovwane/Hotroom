#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-07-17 21:03:33
# @Author  : Wangmengcn (eclipse_sv@163.com)
# @Link    : https://eclipsesv.com
# @Version : $Id$

from fabric.api import *

from datetime import datetime


env.use_ssh_config = True
env.hosts = ['al', 'al1']
env.roledefs = {
    'douyu': ['al'],
    'other': ['al1'],
}


@runs_once
@task
def pre_deploy():
    local('git add -A && git commit')
    local('git push origin master && git push tx master')


@runs_once
@roles('douyu')
def deploy_douyu():
    deploy_code('douyu_app')


@runs_once
@roles('other')
def deploy_other():
    deploy_code('other_app')


def deploy_code(cmd):
    code_dir = '~/git/Hotroom'
    with settings(warn_only=True):
        if run("ls {}".format(code_dir)).failed:
            run("git clone hhttps://github.com/love3forever/Hotroom.git {}".format(code_dir))
    with cd(code_dir):
        run("git pull")
        run("sudo pip install -r ./requirement.txt")
        with cd('./hotroom'):
            pids = run(
                "ps -ef | grep celery | grep -v grep | awk '{print $2}'")
            if pids:
                pid_list = pids.split('\r\n')
                for i in pid_list:
                    with settings(warn_only=True):
                        run('kill -9 %s' % i)
            run('pwd')
            run("(nohup celery -A {} worker -B --loglevel=error >& /dev/null < /dev/null &) && sleep 1".format(cmd))
            run('echo deployed')


@task
def deploy():
    execute(deploy_douyu)
    execute(deploy_other)


def dump(db):
    stamp = datetime.now().strftime('%y_%m_%d_%H_%M')
    cd_dir = '~/tars/dump/'
    dump_dir = '~/tars/dump/dump_{}'.format(stamp)
    dump_tar = 'dump_{}.tar.gz'.format(stamp)
    local_dir = '/Users/eclipse/Downloads/mongo34/dump/'
    local_tar_dir = '/Users/eclipse/Downloads/mongo34/dump/dump_{}'.format(
        stamp)
    local_dump_dir = '/Users/eclipse/Downloads/mongo34/dump/dump_{}.tar.gz'.format(
        stamp)
    with settings(warn_only=True):
        run('mkdir -p {}'.format(dump_dir))
        run('mongodump -d {} -c Roominfo -o {} --gzip'.format(db, dump_dir))
    with cd(cd_dir):
        run('ls')
        run('tar -zcvf {} {}'.format(dump_tar, 'dump_{}'.format(stamp)))
    with settings(warn_only=True):
        get('~/tars/dump/{}'.format(dump_tar), local_dir)
        run('echo current db:{}'.format(db))
        run('mongo')
        local('mkdir -p {}'.format(local_tar_dir))
        local('tar -zxvf {} -C {}'.format(local_dump_dir, local_dir))
        local('/Users/eclipse/Downloads/mongo34/bin/mongorestore --dir={} \
            --gzip'.format(local_tar_dir))


@task
@runs_once
@roles('douyu')
def dump_douyu():
    dump('Douyudata')


@task
@runs_once
@roles('other')
def dump_quanmin():
    dump('Quanmin')


@task
@runs_once
@roles('other')
def dump_panda():
    dump('Pandata')


if __name__ == '__main__':
    dump(1)

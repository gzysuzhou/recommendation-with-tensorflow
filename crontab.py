# -*- coding: UTF-8 -*-
from prehandle import PreHandle
from recommand import Recommand

class Tasks(object):

    def run(self):
        self.updateRecommandation()

    def updateRecommandation(self):
        PreHandle().run()
        Recommand().run(1, 0, 1)
        print('done')

Tasks().run()
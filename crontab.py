from prehandle import PreHandle

class Tasks(object):

    def run(self):
        self.updateRecommandation()

    def updateRecommandation(self):
        PreHandle().run()
        print('done')


Tasks().run()
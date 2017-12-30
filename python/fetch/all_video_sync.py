#!/usr/bin python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from common.envmod import *
import vj69.video
import ozsese.video
import singlove.video
if __name__ == '__main__':
    vj69videop = vj69.video.VideoParse()
    vj69videop.run()

    ozsesevideop = ozsese.video.VideoParse()
    ozsesevideop.run()

    singlovevideop = singlove.video.VideoParse()
    singlovevideop.run()

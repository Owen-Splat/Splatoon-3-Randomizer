# The MIT License (MIT)

# Copyright (c) 2018 LagoLunatic

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Wind Waker Randomizer
# by LagoLunatic


import os
import sys
import appdirs


if getattr(sys, "frozen", False):
    RUNNING_FROM_SOURCE = False
    ROOT_PATH = os.path.dirname(sys.executable)
    if sys.platform == 'darwin': # mac
        userdata_path = appdirs.user_data_dir('randomizer', 'Splatoon 3 Randomizer')
        if not os.path.isdir(userdata_path):
            os.mkdir(userdata_path)
        SETTINGS_PATH = os.path.join(userdata_path, 'settings.txt')
        LOGS_PATH = os.path.join(userdata_path, 'log.txt')
    else:
        SETTINGS_PATH = os.path.join('.', 'settings.txt')
        LOGS_PATH = os.path.join('.', 'log.txt')
else:
    RUNNING_FROM_SOURCE = True
    ROOT_PATH = os.path.dirname(__file__)
    SETTINGS_PATH = os.path.join(ROOT_PATH, 'settings.txt')
    LOGS_PATH = os.path.join(ROOT_PATH, 'log.txt')

DATA_PATH = os.path.join(ROOT_PATH, 'Data')
RESOURCE_PATH = os.path.join(ROOT_PATH, 'Resources')

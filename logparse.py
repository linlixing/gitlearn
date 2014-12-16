#coding=utf-8

# Author: Zhou ZhiBin
# Contact: email-zhouzhibin@xiaomi.com
#
# 0.02  2013/2/22  增加掉信号问题的分析选项，加上left Frame部分的布局

from Tkinter import *
from tkFileDialog   import askopenfilename
import zipfile
import os
import sys
import re
from functools import partial

__version__ = "0.02"


class AppFrame():
    ''' The application UI '''
    def __init__(self):
        self.root = Tk()
        self.root.title("Logparer " + __version__)
        self.init_pathEntry()
        self.phone_value = IntVar()
        #checkbutton的命名方式要遵循 button的名字加上 _value,否则get_issue_check会出错
        self.CB_reboot_value = IntVar()
        self.CB_lostsignal_value = IntVar()
        self.drawwidget()

        #self.root.geometry('500x500+300+100')
    def drawwidget(self):
        self.leftFrame = Frame(relief=RIDGE, bg='white', bd=4, padx=10,
                               pady=10)
        self.rightFrame = Frame(relief=RIDGE, bg='white', padx=0)

        level2_RFrame = partial(Frame, self.rightFrame, relief=RIDGE,
                                bg='white', padx=0, pady=0)
        self.rightF_level2_up = level2_RFrame(pady=0)
        self.rightF_level2_middle = level2_RFrame(pady=0)
        self.rightF_level2_down = level2_RFrame(pady=0)
        self.phone_value.set(1)

        level2_LFrame = partial(Frame, self.leftFrame, relief=RIDGE,
                                bg='white', padx=0, pady=0)
        self.leftF_level2_up = level2_LFrame(pady=0)
        self.leftF_level2_down = level2_LFrame(pady=0)

        #定义偏函数，方便生成Button
        phone_Radiobutton = partial(Radiobutton,
                        self.leftF_level2_up, variable=self.phone_value,
                        width=10, highlightcolor='cyan', anchor=W,
                        relief=RIDGE)
        self.product_radio_Mi2 = phone_Radiobutton(value=1, text='Mi2')
        self.product_radio_Mi2A = phone_Radiobutton(value=2, text='Mi2A')
        self.product_radio_Mi3 = phone_Radiobutton(value=3, text='Mi3')

        issue_checkButton = partial(Checkbutton, self.leftF_level2_down,
                            relief=RIDGE, font='Bold', anchor=W, padx=1,
                            pady=1)
        # issue CheckButton 的命名方式必须要和下面的一致，CB_开头，后面和issuel 中的一直
        self.CB_reboot = issue_checkButton(text='重启',
                        variable=self.CB_reboot_value)
        self.CB_lostsignal = issue_checkButton(text='无信号',
                        variable=self.CB_lostsignal_value)

        self.path_Entry = Entry(self.rightF_level2_up, text='请输入log位置', bd=5,
                relief=SUNKEN, font=('italic', 16), textvariable=self.logpath)
        self.parseText = Text(self.rightF_level2_down, relief=RIDGE, padx=10,
                              pady=10, bd=5)
        self.parseText.tag_config('analysis', foreground='red')
        self.openfiel_Button = Button(self.rightF_level2_up, relief=RIDGE,
                            bd=3, width=10, command=self.slectFile,
                            justify=RIGHT, text="浏览")
        self.start_Button = Button(self.rightF_level2_middle, relief=RIDGE,
                        bd=3, command=self.analysisout, text="分析", width=30)
        self.exitButton = Button(self.rightF_level2_middle, relief=RIDGE, bd=3,
                            text="退出")
        self.logscrollbar = Scrollbar(self.rightF_level2_down)
        self.parseText.config(yscrollcommand=self.logscrollbar.set)
        self.logscrollbar.config(command=self.parseText.yview)

        self.leftFrame.pack(fill=Y, expand=0, side=LEFT)
        self.rightFrame.pack(fill=BOTH, expand=1, side=RIGHT)
        self.leftF_level2_up.pack(fill=X, expand=0, side=TOP)
        self.leftF_level2_down.pack(fill=BOTH, expand=1, side=BOTTOM, pady=20)
        self.rightF_level2_up.pack(fill=X, expand=0, side=TOP)
        self.rightF_level2_middle.pack(fill=X, expand=0)
        self.rightF_level2_down.pack(fill=BOTH, expand=1, side=BOTTOM)

        self.start_Button.pack(anchor=CENTER)
        #self.exitButton.pack(anchor = CENTER)

        self.path_Entry.pack(fill=X, expand=1, side=LEFT)
        self.openfiel_Button.pack(fill=X, expand=0, side=RIGHT)
        #self.openfiel_Button.pack
        self.parseText.pack(fill=BOTH, expand=1, side=LEFT)
        self.logscrollbar.pack(fill=Y, side=RIGHT)
        self.product_radio_Mi2.pack()
        self.product_radio_Mi2A.pack()
        self.product_radio_Mi3.pack()
        self.CB_reboot.pack(fill=X)
        self.CB_lostsignal.pack(fill=X)

    def init_pathEntry(self):
        self.logpath = StringVar()
        self.logpath.set("Select to log file to parse")

    def slectFile(self):
        self.fn = askopenfilename(filetypes=[("bugreport", "*.zip"),
                ("All", "*.*")])
        self.logpath.set(self.fn)

    def get_select_phone(self):
        """ check product_radio Button value"""
        return self.phone_value.get() - 1

    def get_issue_check(self):
        issue_widget_list = [i for i in dir(self)
                             if ('CB_' in i and 'value' in i)]
        check_list = [issue for issue in issue_widget_list
                      if eval('self.' + issue + '.get()')]
        return [i.split('_')[1] for i in check_list]

    def analysisout(self):
        #clear the Text before parse,1.0 define the position not a float
        self.parseText.delete(1.0, END)
        logparser.parsefile()


class LogOpertion():
    def __init__(self, log):
        self.log = log
        self.rmlog_f = False
        if ".zip" in log:
            assert(self.unziplog())
        else:
            self.finallog = self.log

    def unziplog(self):
        if not zipfile.is_zipfile(self.log):
            return False
        try:
            f = zipfile.ZipFile(self.log, 'r')
        except Exception:
            print 'BAD log file !!!'
            return False
        self.finallog = f.namelist()[0]
        f.extract(self.finallog)
        self.rmlog_f = True
        #print os.getcwd()
        return True

    def rmlog(self):
        ''' if the given log file is zip,
        need delete the temp file from extract'''
        if self.rmlog_f == True:
            print os.getcwd()
            os.remove(self.finallog)


class Logparser():
    ''' log parser need combine with the main app frame'''
    def __init__(self, App):
        self.app = App
        #product enumrate list, issue type list to be check
        #use a Three-dimensional array to manage the keyword, the third
        #dimensional is a list of keyword for a special issue of a product
        self.pl = ['Mi2', 'Mi2A', 'Mi3']
        self.issuel = ['reboot', 'lostsignal']
        #===================  keyword database  ==========================
        self.keyWD_array = [[''] * len(self.issuel) for row in range(len(self.pl))]
        self.keyWD_array[self.pl.index('Mi2')][self.issuel.index('reboot')] = (
        'subsystem_restart', 'Shutting down riva', 'Shutting down external_modem',
        'Kernel panic', 'resout_irq_handler PMIC Initiated shutdown',
        'SysRq : Emergency Remount R/O', 'PC is at', 'LR is at')
        self.keyWD_array[self.pl.index('Mi2')][self.issuel.index('lostsignal')]=(
        'VOICE_REGISTRATION_STATE {',)
        self.keyWD_array[self.pl.index('Mi2A')][self.issuel.index('reboot')]=(
        'GPU PAGE FAULT', 'EBI error detected', 'Device hang detected',)

    def parsefile(self):
        self.log = LogOpertion(self.app.logpath.get())
        self.selectphone = self.pl[self.app.get_select_phone()]
        self.selectissues = self.app.get_issue_check()
        out = ''
        print self.log.finallog
        #Call the correspond
        for i in self.selectissues:
            P_index = self.pl.index(self.selectphone)
            I_index = self.issuel.index(i)
            if len(self.keyWD_array[P_index][I_index]) < 1:
                out += "Have no the function to check " + i + ' for ' + \
                        self.selectphone + os.linesep
                self.app.parseText.insert(END, out, 'analysis')
                out = ''
                continue
            print 'self.parse_' + self.selectphone + '_' + i
            eval('self.parse_' + self.selectphone + '_' + i)(P_index, I_index)
        self.log.rmlog()

    def parse_Mi2_reboot(self, phone_index, issue_index):
        ''' 打印出当前的版本，和开机时间，在dmsg中寻找重启的原因，在last_kmsg中查找相关的log'''
        log_out_str = ''
        conclusion_str = ''
        power_reason = ''
        power_reason_dict = {'0x200010': 'other',
                             '0x80010': 'kpanic',
                             '0x80001': 'kpanic',
                             '0x1': 'noremal',
                             '0x100010': 'noremal',
                             }
        dmsg_find = False
        last_kmsg_find = False
        f = open(self.log.finallog)
        txt = f.readline()
        for i in range(20):
            if ('Build fingerprint:' in txt or 'up time:' in txt):
                log_out_str += txt
            txt = f.readline()
        while len(txt) > 0:
            if ('------ KERNEL LOG (dmesg) ------' not in txt):
                txt = f.readline()
            else:
                dmsg_find = True
                for j in range(10):
                    if 'powerup reason=' in txt:
                        log_out_str += txt
                        power_reason = txt.split('=')[1].splitlines()[0]
                        txt = f.readline()
                        break
                    txt = f.readline()
                break
        while len(txt) > 0:
            if ('------ LAST KMSG (/proc/last_kmsg) -----' not in txt):
                txt = f.readline()
                continue
            last_kmsg_find = True
            break
        while len(txt) > 0:
            for k in self.keyWD_array[phone_index][issue_index]:
                if k in txt:
                    log_out_str += txt
                    continue
            txt = f.readline()
        f.close()
        if power_reason in power_reason_dict.keys():
            conclusion_str = os.linesep + 'The power up reason is ' + power_reason_dict[power_reason]
        else:
            conclusion_str = os.linesep + 'The power up reason is UNKNOWN'
        self.app.parseText.insert(END, log_out_str)
        self.app.parseText.insert(END, conclusion_str, 'analysis')
        
    def parse_Mi2A_reboot(self, phone_index, issue_index):
        self.parse_Mi2_reboot(phone_index, issue_index)

    def parse_Mi2_lostsignal(self, phone_index, issue_index):
        log_out_str = ''
        conclusion_str = ''
        reg_init_state = 0
        iflost = False
        f = open(self.log.finallog)
        txt = f.readline()
        for i in range(20):
            if ('Build fingerprint:' in txt or 'up time:' in txt):
                log_out_str += txt
            txt = f.readline()
        while len(txt) > 0:
            for k in self.keyWD_array[phone_index][issue_index]:
                if k in txt:
                    log_out_str += txt
                    m = re.match('.+VOICE_REGISTRATION_STATE\s{(\d+),.+', txt)
                    if m is not None:
                        reg_state = int(m.group(1))
                        if reg_init_state == 0 and reg_state == 1:
                            reg_init_state = 1
                        elif reg_init_state == 0 and reg_state != 0:
                            pass
                        elif reg_init_state == 1 and reg_state == 1:
                            pass
                        elif reg_init_state == 1 and reg_state != 1:
                            iflost = True
                    continue
            txt = f.readline()
        f.close()
        if iflost:
            conclusion_str += (os.linesep + '发生掉网' + os.linesep)
        else:
            conclusion_str += (os.linesep + '没有发现掉网现象' + os.linesep)
        self.app.parseText.insert(END, log_out_str)
        self.app.parseText.insert(END, conclusion_str, 'analysis')

app = AppFrame()
logparser = Logparser(app)
app.root.mainloop()
